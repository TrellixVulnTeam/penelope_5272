from IPython.display import display
from ipywidgets import Output, VBox
from penelope.corpus import dtm
from penelope.notebook import ipyaggrid_utility
from penelope.notebook.dtm import load_dtm_gui
from penelope.notebook.mdw import create_mdw_gui

view_display, view_gui = Output(), Output()


@view_display.capture(clear_output=True)
def display_mdw(corpus: dtm.VectorizedCorpus, df_mdw):  # pylint: disable=unused-argument
    g = ipyaggrid_utility.display_grid(df_mdw)
    display(g)


@view_gui.capture(clear_output=True)
def loaded_callback(
    corpus: dtm.VectorizedCorpus, corpus_folder: str, corpus_tag: str
):  # pylint: disable=unused-argument
    mdw_gui = create_mdw_gui(corpus, done_callback=display_mdw)
    display(mdw_gui.layout())


def create_main_gui(corpus_folder: str, loaded_callback=loaded_callback) -> VBox:

    gui = load_dtm_gui.create_load_gui(corpus_folder=corpus_folder, loaded_callback=loaded_callback)
    return VBox([gui.layout(), view_gui, view_display])
