from io import StringIO
from typing import Sequence

import pandas as pd
from penelope.type_alias import TaggedFrame
from penelope.utility import term_frequency

from ..interfaces import ContentType
from .interface import CheckpointOpts, IContentSerializer, SerializableContent


# pylint: disable=unused-argument
class TextContentSerializer(IContentSerializer):
    def serialize(self, content: SerializableContent, options: CheckpointOpts) -> str:
        return content

    def deserialize(self, content: str, options: CheckpointOpts) -> SerializableContent:
        return content

    def compute_term_frequency(self, content: SerializableContent, checkpoint_opts: CheckpointOpts) -> dict:
        return {}


class TokensContentSerializer(IContentSerializer):
    def serialize(self, content: SerializableContent, options: CheckpointOpts) -> str:
        return ' '.join(content)

    def deserialize(self, content: str, options: CheckpointOpts) -> Sequence[str]:
        return content.split(' ')

    def compute_term_frequency(self, content: SerializableContent, checkpoint_opts: CheckpointOpts) -> dict:
        tfs = dict(term_frequency=term_frequency(content))
        return tfs


class CsvContentSerializer(IContentSerializer):
    def serialize(self, content: SerializableContent, options: CheckpointOpts) -> str:
        return content.to_csv(sep=options.sep, header=True)

    def deserialize(self, content: str, options: CheckpointOpts) -> SerializableContent:
        data: pd.DataFrame = pd.read_csv(
            StringIO(content), sep=options.sep, quoting=options.quoting, index_col=options.index_column
        )
        data.fillna("", inplace=True)
        if any(x not in data.columns for x in options.columns):
            raise ValueError(f"missing columns: {', '.join([x for x in options.columns if x not in data.columns])}")
        if options.lower_lemma:
            tokens: Sequence[str] = data[options.lemma_column]
            data[options.lemma_column] = pd.Series([x.lower() for x in tokens])
        return data[options.columns]

    def compute_term_frequency(self, content: SerializableContent, checkpoint_opts: CheckpointOpts) -> dict:

        if not checkpoint_opts.frequency_column:
            return {}

        tagged_frame: TaggedFrame = content
        tfs = dict(
            term_frequency=term_frequency(tagged_frame[checkpoint_opts.frequency_column]),
            pos_frequency=term_frequency(tagged_frame[checkpoint_opts.pos_column]),
        )
        return tfs


def create_serializer(options: CheckpointOpts) -> "IContentSerializer":

    if options.custom_serializer:
        return options.custom_serializer()

    if options.content_type == ContentType.TEXT:
        return TextContentSerializer()

    if options.content_type == ContentType.TOKENS:
        return TokensContentSerializer()

    if options.content_type == ContentType.TAGGED_FRAME:
        return CsvContentSerializer()

    raise ValueError(f"non-serializable content type: {options.content_type}")
