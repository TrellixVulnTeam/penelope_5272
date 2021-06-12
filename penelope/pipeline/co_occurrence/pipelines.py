from __future__ import annotations

from typing import TYPE_CHECKING

from penelope.co_occurrence import ContextOpts
from penelope.corpus import ExtractTaggedTokensOpts, TokensTransformOpts
from penelope.utility import PropertyValueMaskingOpts

from .. import pipelines

if TYPE_CHECKING:
    from ..pipelines import CorpusPipeline


def wildcard_to_partition_by_document_co_occurrence_pipeline(
    *,
    extract_opts: ExtractTaggedTokensOpts = None,
    filter_opts: PropertyValueMaskingOpts = None,
    transform_opts: TokensTransformOpts = None,  # pylint: disable=unused-argument
    context_opts: ContextOpts = None,
    global_threshold_count: int = None,
    **kwargs,  # pylint: disable=unused-argument
) -> CorpusPipeline:
    try:
        pipeline: pipelines.CorpusPipeline = (
            pipelines.wildcard()
            .vocabulary(
                lemmatize=extract_opts,
                progress=True,
                tf_threshold=extract_opts.global_tf_threshold,
                tf_keeps=context_opts.concept,
                close=True
            )
            .tagged_frame_to_tokens(
                extract_opts={**extract_opts, **{'global_tf_threshold': 1}},
                filter_opts=filter_opts,
                transform_opts=transform_opts,
            )
            # .tokens_transform(transform_opts=transform_opts)
            .to_document_co_occurrence(context_opts=context_opts, ingest_tokens=False)
            .tqdm(desc="Processing documents")
            .to_corpus_co_occurrence(
                context_opts=context_opts,
                global_threshold_count=global_threshold_count,
            )
        )

        return pipeline

    except Exception as ex:
        raise ex
