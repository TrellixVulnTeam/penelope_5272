from typing import Any

import gensim
import numpy as np
import pandas as pd

import penelope.utility as utility

from .utility import add_document_metadata

logger = utility.getLogger('corpus_text_analysis')

def predict_document_topics(
    model: Any,
    corpus: Any,
    documents: pd.DataFrame = None,
    doc_topic_matrix: Any = None,
    minimum_probability: float = 0.001
) -> pd.DataFrame:
    """Applies a the topic model on `corpus` and returns a document-topic dataframe

    Parameters
    ----------
    model : ModelData
        The topic model
    corpus : Any
        The corpus
    documents : pd.DataFrame, optional
        The document index, by default None
    doc_topic_matrix : Any, optional
        The document-topic sparse matrix, by default None
    minimum_probability : float, optional
        Threshold, by default 0.001

    Returns
    -------
    pd.DataFrame
        Document topics
    """
    try:

        def document_topics_iter(model, corpus, minimum_probability=0.0):

            if isinstance(model, gensim.models.LsiModel):
                # Gensim LSI Model
                data_iter = enumerate(model[corpus])
            elif hasattr(model, 'get_document_topics'):
                # Gensim LDA Model
                data_iter = enumerate(model.get_document_topics(corpus, minimum_probability=minimum_probability))
            elif hasattr(model, 'load_document_topics'):
                # Gensim MALLET wrapper
                data_iter = enumerate(model.load_document_topics())
            elif hasattr(model, 'top_doc_topics'):
                # scikit-learn
                assert doc_topic_matrix is not None, "doc_topic_matrix not supplied"
                data_iter = model.top_doc_topics(doc_topic_matrix, docs=-1, top_n=1000, weights=True)
            else:
                data_iter = ((document_id, model[corpus[document_id]]) for document_id in range(0, len(corpus)))

                # assert False, 'compile_document_topics: Unknown topic model'

            for document_id, topic_weights in data_iter:
                for (topic_id, weight) in ((topic_id, weight) for (topic_id, weight) in topic_weights
                                           if weight >= minimum_probability):
                    yield (document_id, topic_id, weight)

        '''
        Get document topic weights for all documents in corpus
        Note!  minimum_probability=None filters less probable topics, set to 0 to retrieve all topcs

        If gensim model then use 'get_document_topics', else 'load_document_topics' for mallet model
        '''
        logger.info('Compiling document topics...')
        logger.info('  Creating data iterator...')
        data = document_topics_iter(model, corpus, minimum_probability)

        logger.info('  Creating frame from iterator...')
        df_doc_topics = pd.DataFrame(data, columns=['document_id', 'topic_id', 'weight'])

        df_doc_topics['document_id'] = df_doc_topics.document_id.astype(np.uint32)
        df_doc_topics['topic_id'] = df_doc_topics.topic_id.astype(np.uint16)

        df_doc_topics = add_document_metadata(df_doc_topics, 'year', documents)

        logger.info('  DONE!')

        return df_doc_topics

    except Exception as ex:  # pylint: disable=broad-except
        logger.error(ex)
        return None
        