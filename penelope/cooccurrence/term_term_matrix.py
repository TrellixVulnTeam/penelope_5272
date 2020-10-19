from typing import Mapping, Union

import pandas as pd
import scipy

from penelope.corpus import CorpusVectorizer, TokenizedCorpus
from penelope.corpus.interfaces import ITokenizedCorpus
from penelope.corpus.readers.interfaces import ICorpusReader


def to_coocurrence_matrix(
    corpus_or_reader: Union[ICorpusReader, TokenizedCorpus], vocabulary: Mapping[str, int] = None
) -> scipy.sparse.spmatrix:
    """Computes a term-term coocurrence matrix for documents in corpus/reader.

    Parameters
    ----------
    corpus_or_reader : Union[ICorpusReader,TokenizedCorpus]
        Sequence of tokenized documents

    Returns
    -------
    pd.DataFrame
        Upper diagonal of term-term frequency matrix (TTM). Note that diagonal (wi, wi) is not returned
    """

    if not isinstance(corpus_or_reader, ITokenizedCorpus):
        corpus_or_reader = TokenizedCorpus(reader=corpus_or_reader)

    vocabulary = vocabulary or corpus_or_reader.token2id
    vectorizer = CorpusVectorizer()
    v_corpus = vectorizer.fit_transform(corpus_or_reader, vocabulary=vocabulary)
    term_term_matrix = v_corpus.cooccurrence_matrix()

    return term_term_matrix


def to_dataframe(
    term_term_matrix: scipy.sparse.spmatrix,
    id2token: Mapping[int, str],
    documents: pd.DataFrame = None,
    min_count: int = 1,
):
    """Converts a TTM to a Pandas DataFrame

    Parameters
    ----------
    term_term_matrix : scipy.sparse.spmatrix
        [description]
    id2token : Mapping[int,str]
        [description]
    documents : pd.DataFrame, optional
        [description], by default None
    min_count : int, optional
        [description], by default 1

    Returns
    -------
    [type]
        [description]
    """
    coo_df = (
        pd.DataFrame({
            'w1_id': term_term_matrix.row,
            'w2_id': term_term_matrix.col,
            'value': term_term_matrix.data
        })[['w1_id', 'w2_id', 'value']].sort_values(['w1_id', 'w2_id']).reset_index(drop=True)
    )

    if min_count > 1:
        coo_df = coo_df[coo_df.value >= min_count]

    if documents is not None:

        coo_df['value_n_d'] = coo_df.value / float(len(documents))

        if 'n_tokens' in documents:
            coo_df['value_n_t'] = coo_df.value / float(sum(documents.n_tokens.values()))

    coo_df['w1'] = coo_df.w1_id.apply(lambda x: id2token[x])
    coo_df['w2'] = coo_df.w2_id.apply(lambda x: id2token[x])

    coo_df = coo_df[['w1', 'w2', 'value', 'value_n_d', 'value_n_t']]

    return coo_df
