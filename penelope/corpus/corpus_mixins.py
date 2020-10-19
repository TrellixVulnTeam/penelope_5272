import logging
import os
from typing import Any, Callable, Dict, List, Tuple, Union

import pandas as pd


class PartitionMixIn:

    def partition_documents(self, by: Union[str, List[str], Callable]) -> Dict[Any, List[str]]:

        if 'filename' not in self.documents.columns:
            raise ValueError("`filename` columns missing")

        groups = self.documents.groupby(by=by)['filename'].aggregate(list).to_dict()

        return groups


def stripext(filename):
    return os.path.splitext(filename)[0]


class UpdateTokenCountsMixIn:

    def update_token_counts(self, doc_token_counts: List[Tuple[str, int, int]]) -> pd.DataFrame:

        _documents = self._documents

        try:

            df_counts = pd.DataFrame(data=doc_token_counts, columns=['filename', 'x_raw_tokens', 'x_tokens'])
            df_counts['_basename'] = df_counts.filename.apply(stripext)
            df_counts = df_counts.set_index('_basename')\
                .drop('filename', axis=1)

            if '_basename' not in _documents.columns:
                _documents['_basename'] = _documents.filename.apply(stripext)
            if 'n_raw_tokens' not in _documents.columns:
                _documents['n_raw_tokens'] = 0
            if 'n_tokens' not in _documents.columns:
                _documents['n_tokens'] = 0

            _documents = _documents.merge(df_counts, how='left', left_on='_basename', right_index=True)
            _documents['n_raw_tokens'] = _documents['x_raw_tokens'].fillna(_documents['n_raw_tokens'])
            _documents['n_tokens'] = _documents['x_tokens'].fillna(_documents['n_tokens'])
            _documents = _documents.drop(['x_raw_tokens', 'x_tokens'], axis=1)

        except Exception as ex:
            logging.error(ex)

        return _documents
