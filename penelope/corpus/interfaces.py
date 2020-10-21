import abc
from typing import Any, Callable, Dict, Iterator, List, Set, Tuple, Union

import pandas as pd


class ICorpus(abc.ABC):
    @abc.abstractmethod
    def __next__(self) -> Tuple[str, Iterator[str]]:
        'Return the next item from the iterator. When exhausted, raise StopIteration'
        raise StopIteration

    @abc.abstractmethod
    def __iter__(self):
        return self


class ITokenizedCorpus(ICorpus):

    __slots__ = ()

    @property
    @abc.abstractproperty
    def terms(self) -> Iterator[Iterator[str]]:
        return None

    @property
    @abc.abstractproperty
    def metadata(self) -> List[Dict[str, Any]]:
        return None

    @property
    @abc.abstractproperty
    def filenames(self) -> List[str]:
        return None

    @property
    @abc.abstractproperty
    def documents(self) -> pd.DataFrame:
        return None


PartitionKeys = Union[str, List[str], Set[str], Callable]
