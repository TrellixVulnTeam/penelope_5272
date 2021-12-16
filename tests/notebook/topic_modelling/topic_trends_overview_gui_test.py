from penelope.notebook.topic_modelling import TopicModelContainer
from penelope.notebook.topic_modelling.topic_trends_overview_gui import TopicOverviewGUI
from penelope.topic_modelling.prevelance import AverageTopicPrevalenceOverTimeCalculator


def test_create_gui(state: TopicModelContainer):
    gui: TopicOverviewGUI = TopicOverviewGUI(calculator=AverageTopicPrevalenceOverTimeCalculator())
    assert gui is not None

    gui = gui.setup(state)
    assert gui is not None

    layout = gui.layout()
    assert layout is not None

    gui.update_handler()
