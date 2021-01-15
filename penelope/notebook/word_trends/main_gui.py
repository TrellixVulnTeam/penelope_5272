import ipywidgets as widgets
import penelope.notebook.dtm as dtm_gui
import penelope.notebook.word_trends as word_trends
import penelope.pipeline as pipeline
import penelope.workflows as workflows
from IPython.core.display import display
from penelope.corpus import VectorizedCorpus
from penelope.notebook.interface import ComputeOpts

view = widgets.Output(layout={'border': '2px solid green'})


@view.capture(clear_output=True)
def corpus_loaded_callback(
    corpus: VectorizedCorpus,
    corpus_tag: str,
    corpus_folder: str,
    **_,
):
    trends_data: word_trends.TrendsData = word_trends.TrendsData(
        corpus=corpus,
        corpus_folder=corpus_folder,
        corpus_tag=corpus_tag,
        n_count=25000,
    ).update()

    gui = word_trends.GofTrendsGUI(
        gofs_gui=word_trends.GoFsGUI().setup(),
        trends_gui=word_trends.TrendsGUI().setup(),
    )

    display(gui.layout())
    gui.display(trends_data=trends_data)


@view.capture(clear_output=True)
def compute_callback(args: ComputeOpts, corpus_config: pipeline.CorpusConfig):
    workflows.document_term_matrix.compute(args=args, corpus_config=corpus_config)


def create_to_dtm_gui(
    corpus_folder: str,
    corpus_config: str,
    resources_folder: str = None,
) -> widgets.CoreWidget:

    resources_folder = resources_folder or corpus_folder
    config: pipeline.CorpusConfig = pipeline.CorpusConfig.find(corpus_config, resources_folder).folder(corpus_folder)
    gui_compute: dtm_gui.ComputeGUI = dtm_gui.create_compute_gui(
        corpus_folder=corpus_folder,
        corpus_config=config,
        compute_callback=compute_callback,
        done_callback=corpus_loaded_callback,
    )

    gui_load: dtm_gui.LoadGUI = dtm_gui.create_load_gui(
        corpus_folder=corpus_folder,
        loaded_callback=corpus_loaded_callback,
    )

    accordion = widgets.Accordion(
        children=[
            widgets.VBox(
                [
                    gui_load.layout(),
                ],
                layout={'border': '1px solid black', 'padding': '16px', 'margin': '4px'},
            ),
            widgets.VBox(
                [
                    gui_compute.layout(),
                ],
                layout={'border': '1px solid black', 'padding': '16px', 'margin': '4px'},
            ),
        ]
    )

    accordion.set_title(0, "LOAD AN EXISTING DOCUMENT-TERM MATRIX")
    accordion.set_title(1, '...OR COMPUTE A NEW DOCUMENT-TERM MATRIX')

    return widgets.VBox([accordion, view])
