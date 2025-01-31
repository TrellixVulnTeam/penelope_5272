from typing import Any, Callable, Union

from penelope.corpus import VectorizedCorpus
from penelope.pipeline import CorpusConfig
from penelope.workflows import interface

from ..gui_base import BaseGUI


class ComputeGUI(BaseGUI):
    def layout(self, hide_input=False, hide_output=False):
        layout = super().layout(hide_input, hide_output)
        return layout

    def setup(
        self, *, config: CorpusConfig, compute_callback: Callable, done_callback: Callable[[Any, "ComputeGUI"], None]
    ):
        super().setup(config=config, compute_callback=compute_callback, done_callback=done_callback)
        return self


def create_compute_gui(
    *,
    corpus_folder: str,
    data_folder: str,
    corpus_config: Union[str, CorpusConfig],
    compute_callback: Callable[[interface.ComputeOpts, CorpusConfig], VectorizedCorpus],
    done_callback: Callable[[Any, interface.ComputeOpts], None],
) -> ComputeGUI:
    """Returns a GUI for turning a corpus pipeline to a document-term-matrix (DTM)"""
    corpus_config: CorpusConfig = CorpusConfig.find(corpus_config, corpus_folder).folders(corpus_folder)
    gui = ComputeGUI(
        default_corpus_path=corpus_folder,
        default_corpus_filename=(corpus_config.pipeline_payload.source or ''),
        default_data_folder=data_folder,
    ).setup(
        config=corpus_config,
        compute_callback=compute_callback,
        done_callback=done_callback,
    )

    return gui
