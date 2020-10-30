from .compute_hal_or_glove import compute
from .concept_co_occurrence import (
    corpus_concept_windows,
    load_co_occurrences,
    partitioned_corpus_concept_co_occurrence,
    store_co_occurrences,
    tokens_concept_windows,
    to_vectorized_corpus
)

# from .compute_partitioned import (compute_for_column_group, load_text_windows,
#                                   partitoned_co_occurrence)
from .term_term_matrix import to_co_occurrence_matrix, to_dataframe
from .vectorizer_glove import GloveVectorizer
from .vectorizer_hal import HyperspaceAnalogueToLanguageVectorizer
from .windows_corpus import WindowsCorpus, WindowsStream
