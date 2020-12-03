import enum
from dataclasses import dataclass
from typing import Any, Dict

from penelope.corpus.readers import TextReaderOpts
from penelope.utility import get_pos_schema, replace_path

from . import interfaces


@enum.unique
class CorpusType(enum.IntEnum):
    Undefined = 0
    Text = 1
    Tokenized = 2
    SparvCSV = 3
    SpacyCSV = 4
    Pipeline = 5


@dataclass
class CorpusConfig:

    corpus_name: str = None
    corpus_type: CorpusType = CorpusType.Undefined
    corpus_pattern: str = "*.zip"
    text_reader_opts: TextReaderOpts = None
    pipeline_payload: interfaces.PipelinePayload = None
    pos_schema_name: str = None
    language: str = "english"

    def set_folder(self, folder: str) -> "CorpusConfig":
        if self.pipeline_payload.document_index_source is not None:
            if isinstance(self.pipeline_payload.source, str):
                self.pipeline_payload.document_index_source = replace_path(
                    self.pipeline_payload.document_index_source, folder
                )
        if isinstance(self.pipeline_payload.source, str):
            self.pipeline_payload.source = replace_path(self.pipeline_payload.source, folder)

        return self

    @property
    def pos_schema(self):
        return get_pos_schema(self.pos_schema_name)

    @property
    def props(self) -> Dict[str, Any]:
        return dict(
            corpus_name=self.corpus_name,
            corpus_type=int(self.corpus_type),
            text_reader_opts=self.text_reader_opts.props,
            pipeline_payload=self.pipeline_payload.props,
            pos_schema_name=self.pos_schema_name,
        )
