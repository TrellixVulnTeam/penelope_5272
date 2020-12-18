from typing import Sequence

import pandas as pd
from penelope.co_occurrence import ContextOpts, store_bundle, to_vectorized_corpus
from penelope.corpus import TokensTransformOpts, VectorizedCorpus
from penelope.corpus.readers import ExtractTaggedTokensOpts
from penelope.notebook.co_occurrence import POS_CHECKPOINT_FILENAME_POSTFIX
from penelope.pipeline.config import CorpusConfig
from penelope.pipeline.pipelines import CorpusPipeline
from penelope.pipeline.spacy.pipelines import spaCy_co_occurrence_pipeline

from .utils import WorkflowException

# pylint: disable=too-many-arguments


def execute_workflow(
    corpus_filename: str,
    target_filename: str,
    corpus_config: CorpusConfig,
    *,
    context_opts: ContextOpts = None,
    extract_tokens_opts: ExtractTaggedTokensOpts = None,
    tokens_transform_opts: TokensTransformOpts = None,
    count_threshold: int = None,
    partition_keys: Sequence[str],
    # filename_field: Any = None,
    # document_index_filename: str=None,
    # document_index_sep: str='\t',
    # pos_schema_name: str = "Universal",
    # language: str = "english",
) -> pd.DataFrame:
    """Creates concept co-occurrence using specified options and stores a co-occurrence CSV file
    and optionally a vectorized corpus.

    Parameters
    ----------
    input_filename : str
        Sparv v4 input corpus in CSV export format
    output_filename : str
        Target co-occurrence CSV file, optionally compressed if extension is ".zip"
    partition_keys : Sequence[str]
        Key in corpus document index to use to split corpus in sub-corpora.
        Each sub-corpus co-occurrence is associated to the corresponding key value.
        Usually the `year` column in the document index.
    context_opts: ContextOpts
        context_width : int, optional
            Width of context i.e. distance to cencept word, by default None
        concept : List[str], optional
            Tokens that defines the concept, by default None
        no_concept : bool, optional
            Specifies if concept should be removed from result, by default False
    count_threshold : int, optional
        Word pair count threshold (entire corpus, by default None
    extract_tokens_opts : ExtractTaggedTokensOpts, optional
    tokens_transform_opts : TokensTransformOpts, optional
    filename_field : Any, optional
        Specifies fields to extract from document's filename, by default None
    store_vectorized : bool, optional
        If true, then the co-occurrence pairs are stored in a vectorized corpus
        with a vocabulary consisting of "word1/word2" tokens, by default False

    Raises
    ------
    WorkflowException
        When any argument check fails.
    """

    # TODO Add to corpus_confif
    pipeline: CorpusPipeline = spaCy_co_occurrence_pipeline

    if len(context_opts.concept or []) == 0:
        raise WorkflowException("please specify at least one concept (--concept e.g. --concept=information)")

    if len(corpus_config.text_reader_opts.filename_field or []) == 0:
        raise WorkflowException(
            "please specify at least one filename field (--filename-field e.g. --filename-field='year:_:1')"
        )

    if context_opts.context_width is None:
        raise WorkflowException(
            "please specify at width of context as max distance from cencept (--context-width e.g. --context_width=2)"
        )

    if len(partition_keys or []) == 0:
        raise WorkflowException("please specify partition key) (--partition-key e.g --partition-key=year)")

    if len(partition_keys) > 1:
        raise WorkflowException("only one partition key is allowed (for now)")

    checkpoint_filename: str = f"{corpus_config.corpus_name}{POS_CHECKPOINT_FILENAME_POSTFIX}"

    co_occurrences: pd.DataFrame = pipeline(
        corpus_config=corpus_config,
        tokens_transform_opts=tokens_transform_opts,
        extract_tagged_tokens_opts=extract_tokens_opts,
        tagged_tokens_filter_opts=corpus_config.tagged_tokens_filter_opts,
        context_opts=context_opts,
        global_threshold_count=count_threshold,
        partition_column=partition_keys[0],
        checkpoint_filename=checkpoint_filename,
    ).value()

    corpus: VectorizedCorpus = to_vectorized_corpus(co_occurrences=co_occurrences, value_column='value_n_t')

    store_bundle(
        target_filename,
        co_occurrences=co_occurrences,
        corpus=corpus,
        corpus_tag=None,
        input_filename=corpus_filename,
        partition_keys=partition_keys,
        count_threshold=count_threshold,
        reader_opts=corpus_config.reader_opts,
        tokens_transform_opts=tokens_transform_opts,
        context_opts=context_opts,
        extract_tokens_opts=extract_tokens_opts,
    )

    return co_occurrences
