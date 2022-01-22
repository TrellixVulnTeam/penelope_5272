from typing import Any, Optional, Union

import penelope.topic_modelling as tm


class TopicModelException(Exception):
    pass


class TopicModelContainer:
    """Class for current (last) computed or loaded model"""

    _singleton: "TopicModelContainer" = None

    def __init__(self):
        self._trained_model: tm.InferredModel = None
        self._inferred_topics: tm.InferredTopicsData = None
        self._train_corpus_folder: str = None

    @staticmethod
    def singleton() -> "TopicModelContainer":
        TopicModelContainer._singleton = TopicModelContainer._singleton or TopicModelContainer()
        return TopicModelContainer._singleton

    def update(
        self,
        *,
        trained_model: Optional[tm.InferredModel] = None,
        inferred_topics: Optional[tm.InferredTopicsData] = None,
        train_corpus_folder: Union[str, tm.TrainingCorpus] = None,
    ) -> "TopicModelContainer":
        # if inferred_topics is not None:
        #     if 'n_tokens' not in inferred_topics.document_index.columns:
        #         raise ValueError("expected n_tokens in document_index (previous fix is removed)")
        #         # assert _trained_model.train_corpus is not None
        #         # _inferred_topics.document_index['n_tokens'] = _trained_model.train_corpus.n_tokens
        self._trained_model = trained_model
        self._inferred_topics = inferred_topics
        self._train_corpus_folder = train_corpus_folder

        return self

    @property
    def trained_model(self) -> tm.InferredModel:
        if self._trained_model is None:
            raise TopicModelException('Model not loaded or computed')
        return self._trained_model

    @property
    def inferred_topics(self) -> tm.InferredTopicsData:
        return self._inferred_topics

    @property
    def topic_model(self) -> Any:
        return self.trained_model.topic_model

    @property
    def num_topics(self) -> int:
        return self.inferred_topics.num_topics

    # @pu.deprecated
    # @cached_property
    # def train_corpus(self) -> tm.TrainingCorpus:
    #     if not self._train_corpus_folder:
    #         raise TopicModelException('Training corpus folder is not set!')
    #     if isinstance(self._train_corpus_folder, tm.TrainingCorpus):
    #         return self._train_corpus_folder
    #     return tm.TrainingCorpus.load(self._train_corpus_folder)
