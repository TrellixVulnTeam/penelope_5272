import os
import sys
from os.path import join as jj

import click

import penelope.corpus.readers.text_tokenizer as text_tokenizer
import penelope.corpus.tokenized_corpus as tokenized_corpus
import penelope.topic_modelling as topic_modelling
import penelope.utility.file_utility as file_utility

# pylint: disable=unused-argument, too-many-arguments


@click.command()
@click.argument('name')  # , help='Model name.')
@click.option('--n-topics', default=50, help='Number of topics.', type=click.INT)
@click.option('--corpus-folder', default=None, help='Corpus folder (if vectorized corpus exists on disk).')
@click.option(
    '--corpus-filename',
    help='Corpus filename (if text corpus file or folder, or Sparv XML). Corpus tag if vectorized corpus.',
)
@click.option('--engine', default="gensim_lda-multicore", help='LDA implementation')
@click.option('--passes', default=None, help='Number of passes.', type=click.INT)
@click.option('--alpha', default='asymmetric', help='Prior belief of topic probability. symmetric/asymmertic/auto')
@click.option('--random-seed', default=None, help="Random seed value", type=click.INT)
@click.option('--workers', default=None, help='Number of workers (if applicable).', type=click.INT)
@click.option('--max-iter', default=None, help='Max number of iterations.', type=click.INT)
@click.option('--prefix', default=None, help='Prefix.')
@click.option('--meta-field', '-f', default=None, help='RegExp fields to extract from document name', multiple=True)
def compute_topic_model(
    name,
    n_topics,
    corpus_folder,
    corpus_filename,
    engine,
    passes,
    random_seed,
    alpha,
    workers,
    max_iter,
    prefix,
    meta_field,
):
    run_model(
        name=name,
        n_topics=n_topics,
        corpus_folder=corpus_folder,
        corpus_filename=corpus_filename,
        engine=engine,
        passes=passes,
        random_seed=random_seed,
        alpha=alpha,
        workers=workers,
        max_iter=max_iter,
        prefix=prefix,
        meta_field=meta_field,
    )


def run_model(
    name=None,
    n_topics=50,
    corpus_folder=None,
    corpus_filename=None,
    engine="gensim_lda-multicore",
    passes=None,
    random_seed=None,
    alpha='asymmetric',
    workers=None,
    max_iter=None,
    prefix=None,
    meta_field=None,
):
    """ runner """

    if corpus_filename is None and corpus_folder is None:
        click.echo("usage: either corpus-folder or corpus filename must be specified")
        sys.exit(1)

    call_arguments = dict(locals())

    if corpus_folder is None:
        corpus_folder, _ = os.path.split(os.path.abspath(corpus_filename))

    target_folder = jj(corpus_folder, name)

    os.makedirs(target_folder, exist_ok=True)

    topic_modeling_opts = {
        k: v
        for k, v in call_arguments.items()
        if k in ['n_topics', 'passes', 'random_seed', 'alpha', 'workers', 'max_iter', 'prefix'] and v is not None
    }

    transformer_opts = dict(
        only_alphabetic=False,
        only_any_alphanumeric=True,
        to_lower=True,
        min_len=2,
        max_len=99,
        remove_accents=False,
        remove_stopwords=True,
        stopwords=None,
        extra_stopwords=None,
        language="swedish",
        keep_numerals=False,
        keep_symbols=False,
    )

    # if SparvTokenizer opts = dict(pos_includes='|NN|', lemmatize=True, chunk_size=None)
    filename_fields = None if len(meta_field or []) == 0 else file_utility.filename_field_parser(meta_field)

    tokenizer = text_tokenizer.TextTokenizer(
        source_path=corpus_filename,
        chunk_size=None,
        filename_pattern="*.txt",
        filename_filter=None,
        fix_hyphenation=True,
        fix_whitespaces=False,
        filename_fields=filename_fields,
    )

    corpus = tokenized_corpus.TokenizedCorpus(reader=tokenizer, **transformer_opts)

    train_corpus = topic_modelling.TrainingCorpus(
        terms=corpus.terms,
        doc_term_matrix=None,
        id2word=None,
        documents=corpus.documents,
    )

    inferred_model = topic_modelling.infer_model(
        train_corpus=train_corpus,
        method=engine,
        engine_args=topic_modeling_opts,
    )

    inferred_model.topic_model.save(jj(target_folder, 'gensim.model'))

    topic_modelling.store_model(inferred_model, target_folder)

    inferred_topics = topic_modelling.compile_inferred_topics_data(
        inferred_model.topic_model, train_corpus.corpus, train_corpus.id2word, train_corpus.documents
    )
    inferred_topics.store(target_folder)


if __name__ == '__main__':
    compute_topic_model()  # pylint: disable=no-value-for-parameter
