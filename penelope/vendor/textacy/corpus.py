import os
from typing import List, Any, Dict, Iterable, Tuple

import textacy
import pandas as pd

import penelope.utility as utility
import penelope.corpus.readers.text_tokenizer as text_tokenizer
import penelope.utility.file_utility as file_utility

from .language import create_nlp

logger = utility.getLogger('corpus_text_analysis')

# pylint: disable=too-many-arguments


def create_corpus(reader_with_meta, nlp, tick=utility.noop, n_chunk_threshold=100000):

    corpus = textacy.Corpus(nlp)
    counter = 0

    for filename, text, metadata in reader_with_meta:

        metadata = {**metadata, **dict(filename=filename)}

        if len(text) > n_chunk_threshold:
            doc = textacy.spacier.utils.make_doc_from_text_chunks(text, lang=nlp, chunk_size=n_chunk_threshold)
            corpus.add_doc(doc)
            doc._.meta = metadata
        else:
            corpus.add((text, metadata))

        counter += 1
        if counter % 100 == 0:
            logger.info('%s documents added...', counter)
        tick(counter)

    return corpus


@utility.timecall
def save_corpus(corpus, filename, lang=None, include_tensor=False):  # pylint: disable=unused-argument
    if not include_tensor:
        for doc in corpus:
            doc.tensor = None
    corpus.save(filename)


@utility.timecall
def load_corpus(filename: str, lang: str):  # pylint: disable=unused-argument
    corpus = textacy.Corpus.load(lang, filename)
    return corpus


def merge_named_entities(textacy_corpus):
    logger.info('Working: Merging named entities...')
    try:
        for doc in textacy_corpus:
            named_entities = textacy.extract.entities(doc)
            textacy.spacier.utils.merge_spans(named_entities, doc)
    except TypeError as ex:
        logger.error(ex)
        logger.info('NER merge failed')


def generate_corpus_filename(
    source_path: str, language: str, nlp_args=None, preprocess_args=None, compression='bz2', extension='bin'
):
    nlp_args = nlp_args or {}
    preprocess_args = preprocess_args or {}
    disabled_pipes = nlp_args.get('disable', ())
    suffix = '_{}_{}{}'.format(
        language,
        '_'.join([k for k in preprocess_args if preprocess_args[k]]),
        '_disable({})'.format(','.join(disabled_pipes)) if len(disabled_pipes) > 0 else '',
    )
    filename = utility.path_add_suffix(source_path, suffix, new_extension='.' + extension)
    if (compression or '') != '':
        filename += '.' + compression
    return filename


def _get_document_metadata(
    filename: str,
    metadata: Dict[str, Any] = None,
    documents: pd.DataFrame = None,
    document_columns: List[str] = None,
    filename_fields: Dict[str, Any] = None,
):
    """Extract document metadata from filename and document index"""
    metadata = metadata or {}

    if filename_fields is not None:

        metadata = {**metadata, **(file_utility.extract_filename_fields(filename, **filename_fields).__dict__)}

    if documents is not None:

        if 'filename' not in documents.columns:
            raise ValueError("Filename field 'filename' not found in document index")

        document_row = documents[documents.filename == filename]

        if document_columns is not None:
            document_row = document_row[document_columns]

        if len(document_row) == 0:
            raise ValueError(f"Name '{filename}' not found in index")

        metadata = {**metadata, **(document_row.iloc[0].to_dict())}

        if 'document_id' not in metadata:
            metadata['document_id'] = document_row.index[0]

    return metadata


def _extend_stream_with_metadata(
    tokenizer: text_tokenizer.TextTokenizer,
    documents: pd.DataFrame = None,
    document_columns: List[str] = None,
    filename_fields: Dict[str, Any] = None,
) -> Iterable[Tuple[str, str, Dict]]:
    """Extract and adds document meta data to stream

    Parameters
    ----------
    tokenizer : text_tokenizer.TextTokenizer
        Tokenizer, stream of filename and tokens
    documents : pd.DataFrame, optional
        Document index, by default None
    document_columns : List[str], optional
        Columns in document index, by default None
    filename_fields : Dict[str,Any], optional
        Filename fields to extract, by default None

    Yields
    -------
    Iterable[Tuple[str, str, Dict]]
        Stream augumented with meta data.
    """
    for filename, tokens in tokenizer:

        metadata = _get_document_metadata(
            filename,
            metadata=tokenizer.metadict['filename'],
            documents=documents,
            document_columns=document_columns,
            filename_fields=filename_fields,
        )

        yield filename, ' '.join(tokens), metadata


# pylint: disable=import-outside-toplevel
def load_or_create(
    source_path: Any,
    language: str,
    documents: pd.DataFrame = None,  # data_frame or lambda corpus: corpus_index
    merge_entities: bool = False,
    overwrite: bool = False,
    binary_format: bool = True,
    use_compression: bool = True,
    disabled_pipes: List[str] = None,
    filename_fields: Dict[str, Any] = None,
    document_columns: List[str] = None,
    tick=utility.noop,
) -> Dict[str, Any]:
    """Loads textaCy corpus from disk if it exists on disk with a name that satisfies the given arguments.
    Otherwise creates a new corpus and adds metadata to corpus documents as specified by `filename_fields` and/or document index.

    Parameters
    ----------
    source_path : Any
        Corpus path name.
    language : str
        The spaCy language designator.
    documents : pd.DataFrame, optional
        A document index (if specified, then must include a `filename` column), by default None
    overwrite : bool, optional
        Force recreate of corpus if it exists on disk, by default False
    binary_format : bool, optional
        Store in pickled binary format, by default True
    use_compression : bool, optional
        Use compression, by default True
    disabled_pipes : List[str], optional
        SpaCy pipes that should be disabled, by default None
    filename_fields : Dict[str, Any], optional
        Specifies metadata that should be extracted from filename, by default None
    document_columns : List[str], optional
        Columns in `documents` to add to metadata, all columns will be added if None, by default None
    tick : Callable, optional
        Progress callback function, by default utility.noop

    Returns
    -------
    Dict[str,Any]
        source_path         Source corpus path
        language            spaCy language specifier
        nlp                 spaCy nlp instance
        textacy_corpus      textaCy corpus
        textacy_corpus_path textaCy corpus filename
    """
    tick = tick or utility.noop

    nlp_args = {'disable': disabled_pipes or []}

    textacy_corpus_path = generate_corpus_filename(
        source_path,
        language,
        nlp_args=nlp_args,
        extension='bin' if binary_format else 'pkl',
        compression='bz2' if use_compression else '',
    )

    nlp = create_nlp(language, **nlp_args)

    if overwrite or not os.path.isfile(textacy_corpus_path):

        logger.info('Computing new corpus %s...', textacy_corpus_path)

        tokens_streams = text_tokenizer.TextTokenizer(
            source_path=source_path,
            transforms=[
                text_tokenizer.TRANSFORMS.fix_hyphenation,
                text_tokenizer.TRANSFORMS.fix_unicode,
                text_tokenizer.TRANSFORMS.fix_whitespaces,
                text_tokenizer.TRANSFORMS.fix_accents,
                text_tokenizer.TRANSFORMS.fix_contractions,
                text_tokenizer.TRANSFORMS.fix_ftfy_text,
            ],
            filename_fields=filename_fields,
        )

        reader = _extend_stream_with_metadata(
            tokens_streams,
            documents=documents,
            document_columns=document_columns,
            filename_fields=None,  # n.b. fields extracted abve
        )

        logger.info('Stream created...')

        tick(0, len(tokens_streams.filenames))

        logger.info('Creating corpus (this might take some time)...')
        textacy_corpus = create_corpus(reader, nlp, tick)

        logger.info('Storing corpus (this might take some time)...')
        save_corpus(textacy_corpus, textacy_corpus_path)

        tick(0)

    else:
        tick(1, 2)
        logger.info('...reading corpus (this might take several minutes)...')
        textacy_corpus = load_corpus(textacy_corpus_path, nlp)

    if merge_entities:
        merge_named_entities(textacy_corpus)

    tick(0)
    logger.info('Done!')

    return dict(
        source_path=source_path,
        language=language,
        nlp=nlp,
        textacy_corpus=textacy_corpus,
        textacy_corpus_path=textacy_corpus_path,
    )
