from __future__ import annotations

from typing import Any, Iterable, Mapping, Tuple

import pandas as pd
import scipy.sparse as sp
from gensim.matutils import Sparse2Corpus
from more_itertools import peekable
from textacy.representations.vectorizers import Vectorizer

from ..tokenized_corpus import TokenizedCorpus
from .corpus import VectorizedCorpus
from .vectorizer import CorpusVectorizer, DocumentTermsStream

"""Ways to vectorize:
1. penelope.corpus.CorpusVectorizer
    USES sklearn.feature_extraction.text.CountVectorizer

2. engine_gensim.convert.TranslateCorpus -> Sparse2Corpus, Dictionary
    gensim.Dictionary.doc2bow, corpus2csc

2. textacy.Vectorizer -> sp.csr_matrix, id_to_term
    Has lots of options! Easy to translate to VectorizedCorpus

Returns:
    [type]: [description]
"""


def id2token2token2id(id2token: Mapping[int, str]) -> dict:
    if id2token is None:
        return None
    if hasattr(id2token, 'token2id'):
        return id2token.token2id
    token2id: dict = {v: k for k, v in id2token.items()}
    return token2id


def from_sparse2corpus(
    source: Sparse2Corpus, *, token2id: Mapping[str, int], document_index: pd.DataFrame
) -> VectorizedCorpus:
    corpus: VectorizedCorpus = VectorizedCorpus(
        bag_term_matrix=source.sparse.tocsr().T,
        token2id=token2id,
        document_index=document_index,
    )
    return corpus


def from_spmatrix(
    source: sp.spmatrix, *, token2id: Mapping[str, int], document_index: pd.DataFrame
) -> VectorizedCorpus:
    corpus = VectorizedCorpus(bag_term_matrix=source, token2id=token2id, document_index=document_index)
    return corpus


def from_tokenized_corpus(
    source: TokenizedCorpus, *, document_index: pd.DataFrame, **vectorize_opts
) -> VectorizedCorpus:
    corpus: VectorizedCorpus = CorpusVectorizer().fit_transform(
        source,
        already_tokenized=True,
        vocabulary=source.token2id,
        document_index=document_index,
        min_df=vectorize_opts.get('min_df', 1),
        max_df=vectorize_opts.get('max_df', 1.0),
        # lowercase=False,
        # stop_words=None,
        # max_df=1.0,
        # min_df=1,
    )
    return corpus


def from_stream_of_tokens(
    source: Iterable[Iterable[str]], *, token2id: Mapping[str, int], document_index: pd.DataFrame, **vectorize_opts
) -> VectorizedCorpus:

    vectorizer: Vectorizer = Vectorizer(
        min_df=vectorize_opts.get('min_df', 1),
        max_df=vectorize_opts.get('max_df', 1.0),
        # tf_type: Literal["linear", "sqrt", "log", "binary"] = "linear",
        # idf_type: Optional[Literal["standard", "smooth", "bm25"]] = None,
        # dl_type: Optional[Literal["linear", "sqrt", "log"]] = None,
        # norm: Optional[Literal["l1", "l2"]] = None,
        # max_n_terms: Optional[int] = None,
        vocabulary_terms=token2id,
    )

    bag_term_matrix: sp.spmatrix = vectorizer.fit_transform(source)

    if token2id is None:
        token2id = id2token2token2id(vectorizer.id_to_term)

    corpus: VectorizedCorpus = VectorizedCorpus(
        bag_term_matrix=bag_term_matrix, token2id=token2id, document_index=document_index
    )

    return corpus


def from_stream_of_filename_tokens(
    source: DocumentTermsStream, *, token2id: Mapping[str, int], document_index: pd.DataFrame, **vectorize_opts
) -> VectorizedCorpus:

    corpus: VectorizedCorpus = CorpusVectorizer().fit_transform(
        source,
        already_tokenized=True,
        vocabulary=token2id,
        document_index=document_index,
        min_df=vectorize_opts.get('min_df', 1),
        max_df=vectorize_opts.get('max_df', 1.0),
        lowercase=vectorize_opts.get('lowercase', False),
        # stop_words=None,
    )

    return corpus


def from_stream_of_text(
    source: Iterable[str], *, token2id: Mapping[str, int], document_index: pd.DataFrame, **vectorize_opts
) -> VectorizedCorpus:

    corpus: VectorizedCorpus = CorpusVectorizer().fit_transform(
        source,
        already_tokenized=False,
        vocabulary=token2id,
        document_index=document_index,
        min_df=vectorize_opts.get('min_df', 1),
        max_df=vectorize_opts.get('max_df', 1.0),
        lowercase=vectorize_opts.get('lowercase', False),
        # stop_words=None,
    )

    return corpus

# pylint: disable=too-many-return-statements

class TranslateCorpus:
    @staticmethod
    def translate(
        source: Any, *, token2id: Mapping[str, int] = None, document_index: pd.DataFrame, **vectorize_opts
    ) -> VectorizedCorpus:
        """Translate source into a `VectorizedCorpus``"""

        if isinstance(source, VectorizedCorpus):
            return source

        if isinstance(source, sp.spmatrix):
            return from_spmatrix(source, token2id=token2id, document_index=document_index)

        # if type(source).__name__.endswith('Sparse2Corpus'):
        if isinstance(source, Sparse2Corpus):
            return from_sparse2corpus(source, token2id=token2id, document_index=document_index)

        if isinstance(source, TokenizedCorpus):
            return from_tokenized_corpus(source, document_index=document_index, **vectorize_opts)

        source: peekable = peekable(source)
        head: Any = source.peek()

        if isinstance(head, Tuple):
            """Vectorize using CorpusVectorizer, stream must be Iterable[Tuple[document-name, Iterable[str]]]"""
            return from_stream_of_filename_tokens(
                source, token2id=token2id, document_index=document_index, **vectorize_opts
            )

        if isinstance(head, str):
            """Vectorize using CorpusVectorizer, stream must be Iterable[Tuple[document-name, Iterable[str]]]"""
            return from_stream_of_text(source, token2id=token2id, document_index=document_index, **vectorize_opts)

        return from_stream_of_tokens(source, token2id=token2id, document_index=document_index, **vectorize_opts)
