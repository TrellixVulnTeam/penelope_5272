from penelope.notebook.topic_modelling import TopicModelContainer
from penelope.notebook.topic_modelling.topic_trends_overview_gui import TopicTrendsOverviewGUI


def test_create_gui(state: TopicModelContainer):
    gui: TopicTrendsOverviewGUI = TopicTrendsOverviewGUI(state=state)
    assert gui is not None

    gui = gui.setup()
    assert gui is not None

    layout = gui.layout()
    assert layout is not None

    gui.update_handler()
