import os
from typing import Optional

import penelope.co_occurrence as co_occurrence
import penelope.pipeline as pipeline
from loguru import logger
from penelope.corpus import VectorizedCorpus
from penelope.notebook import interface
from penelope.utility import deprecated

POS_CHECKPOINT_FILENAME_POSTFIX = '_pos_tagged_frame_csv.zip'


class ZeroComputeError(ValueError):
    def __init__(self):
        super().__init__("Computation ended up in ZERO records. Check settings!")


# pylint: disable=unused-argument
@deprecated
def compute(
    args: interface.ComputeOpts,
    corpus_config: pipeline.CorpusConfig,
    checkpoint_file: Optional[str] = None,
) -> co_occurrence.Bundle:
    """Creates and stores a concept co-occurrence bundle using specified options."""

    try:

        assert args.is_satisfied()

        target_filename = co_occurrence.folder_and_tag_to_filename(folder=args.target_folder, tag=args.corpus_tag)

        os.makedirs(args.target_folder, exist_ok=True)

        checkpoint_filename: Optional[str] = (
            checkpoint_file or f"{corpus_config.corpus_name}_{POS_CHECKPOINT_FILENAME_POSTFIX}"
        )

        tagged_frame_pipeline: pipeline.CorpusPipeline = corpus_config.get_pipeline(
            "tagged_frame_pipeline",
            corpus_filename=args.corpus_filename,
            checkpoint_filename=checkpoint_filename,
        )

        args.extract_tagged_tokens_opts.passthrough_tokens = list(args.context_opts.concept)

        p: pipeline.CorpusPipeline = (
            tagged_frame_pipeline
            # .tap_stream("./tests/output/tapped_stream__tagged_frame_pipeline.zip", "tap_1_tagged_frame_pipeline")
            + pipeline.wildcard_to_partitioned_by_key_co_occurrence_pipeline(
                tokens_transform_opts=args.tokens_transform_opts,
                extract_tagged_tokens_opts=args.extract_tagged_tokens_opts,
                tagged_tokens_filter_opts=args.tagged_tokens_filter_opts,
                context_opts=args.context_opts,
                global_threshold_count=args.count_threshold,
                # FIXME: Not used:
                partition_key=args.partition_keys[0],
            )
        )
        value: co_occurrence.CoOccurrenceComputeResult = p.value()

        if len(value.co_occurrences) == 0:
            raise ZeroComputeError()

        corpus: VectorizedCorpus = co_occurrence.partition_by_key.co_occurrence_dataframe_to_vectorized_corpus(
            co_occurrences=value.co_occurrences,
            document_index=value.document_index,
            # FIXME: Not used:
            partition_key=args.partition_keys[0],
        )

        bundle = co_occurrence.Bundle(
            corpus=corpus,
            corpus_tag=args.corpus_tag,
            corpus_folder=args.target_folder,
            co_occurrences=value.co_occurrences,
            document_index=value.document_index,
            token2id=value.token2id,
            compute_options=co_occurrence.create_options_bundle(
                reader_opts=corpus_config.text_reader_opts,
                tokens_transform_opts=args.tokens_transform_opts,
                context_opts=args.context_opts,
                extract_tokens_opts=args.extract_tagged_tokens_opts,
                input_filename=args.corpus_filename,
                output_filename=target_filename,
                partition_keys=args.partition_keys,
                count_threshold=args.count_threshold,
            ),
        )

        co_occurrence.store_bundle(target_filename, bundle)

        return bundle

    except (
        ValueError,
        FileNotFoundError,
        PermissionError,
    ) as ex:
        logger.error(ex)
        raise
    except Exception as ex:
        logger.error(ex)
        raise
