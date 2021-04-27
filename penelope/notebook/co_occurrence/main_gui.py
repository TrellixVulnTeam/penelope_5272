from dataclasses import dataclass
from typing import Callable, Optional, Union

import ipywidgets as widgets
from IPython.core.display import display
from penelope import co_occurrence, pipeline, workflows

from .. import co_occurrence as co_occurrence_gui
from ..interface import ComputeOpts
from ..utility import CLEAR_OUTPUT
from ..word_trends.trends_data import TrendsData

view = widgets.Output(layout={'border': '2px solid green'})

LAST_BUNDLE: co_occurrence.Bundle = None
LAST_ARGS = None
LAST_CONFIG = None


def create(
    data_folder: str,
    filename_pattern: str = co_occurrence.CO_OCCURRENCE_FILENAME_PATTERN,
    loaded_callback: Callable[[co_occurrence.Bundle], None] = None,
) -> co_occurrence_gui.LoadGUI:

    gui: co_occurrence_gui.LoadGUI = co_occurrence_gui.LoadGUI(default_path=data_folder).setup(
        filename_pattern=filename_pattern, load_callback=co_occurrence.load_bundle, loaded_callback=loaded_callback
    )
    return gui


@view.capture(clear_output=CLEAR_OUTPUT)
def compute_co_occurrence_callback(
    corpus_config: pipeline.CorpusConfig,
    args: ComputeOpts,
    checkpoint_file: Optional[str] = None,
) -> co_occurrence.Bundle:
    try:
        global LAST_BUNDLE, LAST_ARGS, LAST_CONFIG
        LAST_ARGS = args
        LAST_CONFIG = corpus_config

        if args.dry_run:
            print(args.command_line("co_occurrence"))
            return None

        bundle: co_occurrence.Bundle = workflows.co_occurrence.compute(
            args=args,
            corpus_config=corpus_config,
            checkpoint_file=checkpoint_file,
        )
        LAST_BUNDLE = bundle
        return bundle
    except workflows.co_occurrence.ZeroComputeError:
        return None


@dataclass
class MainGUI:
    def __init__(
        self,
        corpus_config: Union[pipeline.CorpusConfig, str],
        corpus_folder: str,
        data_folder: str,
        resources_folder: str,
        global_count_threshold: int = 25,
    ) -> widgets.VBox:

        self.trends_data: TrendsData = None
        self.config = (
            corpus_config
            if isinstance(corpus_config, pipeline.CorpusConfig)
            else pipeline.CorpusConfig.find(corpus_config, resources_folder).folders(corpus_folder)
        )

        self.gui_compute: co_occurrence_gui.ComputeGUI = co_occurrence_gui.create_compute_gui(
            corpus_folder=corpus_folder,
            data_folder=data_folder,
            corpus_config=self.config,
            compute_callback=compute_co_occurrence_callback,
            done_callback=self.display_explorer,
        )

        self.gui_load: co_occurrence_gui.LoadGUI = co_occurrence_gui.create_load_gui(
            data_folder=data_folder,
            filename_pattern=co_occurrence.CO_OCCURRENCE_FILENAME_PATTERN,
            loaded_callback=self.display_explorer,
        )

        self.gui_explore: co_occurrence_gui.ExploreGUI = None

        self.global_count_threshold = global_count_threshold

    def layout(self):

        accordion = widgets.Accordion(children=[self.gui_load.layout(), self.gui_compute.layout()])

        accordion.set_title(0, "LOAD AN EXISTING CO-OCCURRENCE COMPUTATION")
        accordion.set_title(1, '...OR COMPUTE A NEW CO-OCCURRENCE')

        return widgets.VBox([accordion, view])

    @view.capture(clear_output=CLEAR_OUTPUT)
    def display_explorer(self, bundle: co_occurrence.Bundle, *_, **__):
        global LAST_BUNDLE
        LAST_BUNDLE = bundle
        if bundle is None:
            return
        self.trends_data = co_occurrence.to_trends_data(bundle).update()
        self.gui_explore = (
            co_occurrence_gui.ExploreGUI(global_tokens_count_threshold=self.global_count_threshold)
            .setup()
            .display(trends_data=self.trends_data)
        )

        display(self.gui_explore.layout())
