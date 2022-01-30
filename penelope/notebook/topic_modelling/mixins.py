from __future__ import annotations

import ipywidgets as w

from penelope import topic_modelling as tm

from . import model_container as mc


class TopicsStateGui:
    def __init__(self, state: mc.TopicModelContainer) -> None:
        super().__init__()
        self.state: mc.TopicModelContainer = state

    @property
    def inferred_topics(self) -> tm.InferredTopicsData:
        return self.state["inferred_topics"]

    @property
    def inferred_n_topics(self) -> int:
        return self.inferred_topics.num_topics


class NextPrevTopicMixIn:
    def __init__(self, **kwargs) -> None:

        # self._topic_id: w.IntSlider = w.IntSlider(min=0, max=199, step=1, value=0, continuous_update=False, description_width='initial')
        self._prev_topic_id: w.Button = w.Button(description="<<", layout=dict(button_style='Success', width="40px"))
        self._topic_id: w.Dropdown = w.Dropdown(options=[(str(i), i) for i in range(0, 200)], layout=dict(width="80px"))
        self._next_topic_id: w.Button = w.Button(description=">>", layout=dict(button_style='Success', width="40px"))
        self._next_prev_layout: w.HBox = w.HBox([self._prev_topic_id, self._topic_id, self._next_topic_id])

        super().__init__(**kwargs)

    @property
    def __wc_max_topic_id(self) -> int:
        if isinstance(self._topic_id, w.Dropdown):
            return len(self._topic_id.options) - 1
        return self._topic_id.max

    def goto_previous(self, *_):
        self._topic_id.value = (self._topic_id.value - 1) % self.__wc_max_topic_id

    def goto_next(self, *_):
        self._topic_id.value = (self._topic_id.value + 1) % self.__wc_max_topic_id

    def setup(self, **kwargs) -> "NextPrevTopicMixIn":

        if hasattr(super(), "setup"):
            getattr(super(), "setup")(**kwargs)

        self._prev_topic_id.on_click(self.goto_previous)
        self._next_topic_id.on_click(self.goto_next)

        if hasattr(self, "inferred_topics"):
            self.topic_id = (0, getattr(self, "inferred_topics").n_topics - 1)

        return self

    @property
    def topic_id(self) -> tuple | int:
        return self._topic_id.value

    @topic_id.setter
    def topic_id(self, value: tuple | int) -> None:
        """Set current topic ID. If tuple (value, max) is given then both value and max are set"""
        if isinstance(value, tuple):
            if isinstance(self._topic_id, w.IntSlider):
                self._topic_id.value = value[0]
                self._topic_id.max = value[1]
            elif isinstance(self._topic_id, w.Dropdown):
                self._topic_id.value = None
                self._topic_id.options = [(str(i), i) for i in range(0, value[1])]
                self._topic_id.value = value[0]

        else:
            self._topic_id.value = value


class AlertMixIn:
    def __init__(self, **kwargs) -> None:
        self._alert: w.HTML = w.HTML()
        super().__init__(**kwargs)

    def alert(self, msg: str):
        self._alert.value = msg

    def warn(self, msg: str):
        self.alert(f"<span style='color=red'>{msg}</span>")
