import logging
import os
from io import StringIO
from typing import Dict, List, Mapping, Tuple, Union

import numpy as np
import pandas as pd
from penelope.utility import strip_path_and_extension


class DocumentIndexError(ValueError):
    pass


def assert_is_monotonic_increasing_integer_series(series: pd.Series):
    if not is_monotonic_increasing_integer_series(series):
        raise ValueError(f"series: {series.name} must be an integer typed, monotonic increasing series starting from 0")


def is_monotonic_increasing_integer_series(series: pd.Series):
    if not np.issubdtype(series.dtype, np.integer):
        return False
    if not series.is_monotonic_increasing:
        return False
    if len(series) > 0 and series.min() != 0:
        return False
    return True


def metadata_to_document_index(metadata: List[Dict], *, document_id_field: str = None) -> pd.DataFrame:
    """Creates a document index with all collected metadata key as columns.
    The data frame's index is set to `filename` by (default) or `index_field` if it is supplied.
    The index is also added as a `document_id` column."""

    if metadata is None or len(metadata) == 0:
        metadata = {'filename': [], 'document_id': []}

    catalogue: pd.DataFrame = pd.DataFrame(metadata)

    if 'filename' not in catalogue.columns:
        raise ValueError("metadata is missing mandatory field `filename`")

    if 'document_id' in catalogue.columns:
        logging.warning("filename metadata already has a column named `document_id` (will be overwritten)")

    if 'document_name' not in catalogue.columns:
        catalogue['document_name'] = catalogue.filename.apply(strip_path_and_extension)

    catalogue['document_id'] = catalogue[document_id_field] if document_id_field is not None else catalogue.index

    assert_is_monotonic_increasing_integer_series(catalogue['document_id'])

    catalogue = catalogue.set_index('document_name', drop=False)

    return catalogue


def store_document_index(document_index: pd.DataFrame, filename: str):
    document_index.to_csv(filename, sep='\t', header=True)


def load_document_index(filename: Union[str, StringIO], *, key_column: str, sep: str) -> pd.DataFrame:
    """Loads a document index and sets `key_column` as index column. Also adds `document_id`"""

    if filename is None:
        return None

    if isinstance(filename, pd.DataFrame):
        return filename

    attrs = dict(sep=sep)

    document_index = pd.read_csv(filename, **attrs)

    if key_column is not None:
        if key_column not in document_index.columns:
            raise ValueError(f"specified key column {key_column} not found in columns")

    for old_or_unnamed_index_column in ['Unnamed: 0', 'filename.1']:
        if old_or_unnamed_index_column in document_index.columns:
            document_index = document_index.drop(old_or_unnamed_index_column, axis=1)

    if 'filename' not in document_index.columns:
        raise DocumentIndexError("expected mandatry column `filename` in document index, found no such thing")

    if 'document_id' not in document_index.columns and key_column is not None:
        if is_monotonic_increasing_integer_series(document_index[key_column]):
            document_index['document_id'] = document_index[key_column]

    if 'document_id' not in document_index.columns:
        if not is_monotonic_increasing_integer_series(document_index.index):
            document_index = document_index.reset_index(drop=True)
        document_index['document_id'] = document_index.index

    assert_is_monotonic_increasing_integer_series(document_index.document_id)

    if 'document_name' not in document_index.columns or (document_index.document_name == document_index.filename).all():
        document_index['document_name'] = document_index.filename.apply(strip_path_and_extension)

    document_index = document_index.set_index('document_name', drop=False).rename_axis('')

    return document_index


def load_document_index_from_str(data_str: str, key_column: str, sep: str) -> pd.DataFrame:
    df = load_document_index(StringIO(data_str), key_column=key_column, sep=sep)
    return df


def consolidate_document_index(document_index: pd.DataFrame, reader_index: pd.DataFrame):
    """Returns a consolidated document index from an existing index, if exists,
    and the reader index."""

    if document_index is not None:
        columns = [x for x in reader_index.columns if x not in document_index.columns]
        if len(columns) > 0:
            document_index = document_index.merge(reader_index[columns], left_index=True, right_index=True, how='left')
        return document_index

    return reader_index


def document_index_upgrade(document_index: pd.DataFrame) -> pd.DataFrame:
    """Fixes older versions of document indexes"""

    if 'document_name' not in document_index.columns:
        document_index['document_name'] = document_index.filename.apply(strip_path_and_extension)

    if document_index.index.dtype == np.dtype('int64'):

        if 'document_id' not in document_index.columns:
            document_index['document_id'] = document_index.index

    document_index = document_index.set_index('document_name', drop=False).rename_axis('')

    return document_index


def add_document_index_attributes(*, catalogue: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
    """ Adds document meta data to given data frame (must have a document_id) """
    df = target.merge(catalogue, how='inner', left_on='document_id', right_on='document_id')
    return df


def update_document_index_token_counts(
    document_index: pd.DataFrame, doc_token_counts: List[Tuple[str, int, int]]
) -> pd.DataFrame:
    """Updates or adds fields `n_raw_tokens` and `n_tokens` to document index from collected during a corpus read pass
    Only updates values that don't already exist in the document index"""
    try:

        strip_ext = lambda filename: os.path.splitext(filename)[0]

        df_counts: pd.DataFrame = pd.DataFrame(data=doc_token_counts, columns=['filename', 'n_raw_tokens', 'n_tokens'])
        df_counts['document_name'] = df_counts.filename.apply(strip_ext)
        df_counts = df_counts.set_index('document_name').rename_axis('').drop('filename', axis=1)

        if 'document_name' not in document_index.columns:
            document_index['document_name'] = document_index.filename.apply(strip_ext)

        if 'n_raw_tokens' not in document_index.columns:
            document_index['n_raw_tokens'] = np.nan

        if 'n_tokens' not in document_index.columns:
            document_index['n_tokens'] = np.nan

        document_index.update(df_counts)

    except Exception as ex:
        logging.error(ex)

    return document_index


def update_document_index_statistics(document_index, *, document_name: str, statistics: Mapping[str, int]):
    statistics = {k: statistics[k] for k in statistics if k not in ['document_name']}
    for key in [k for k in statistics if k not in document_index.columns]:
        document_index.insert(len(document_index.columns), key, np.nan)
    document_index.update(pd.DataFrame(data=statistics, index=[document_name], dtype=np.int64))
