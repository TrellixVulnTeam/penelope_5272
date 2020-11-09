import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import ipyfilechooser
import ipywidgets as widgets
from penelope.corpus.readers import AnnotationOpts
from penelope.corpus.tokens_transformer import TokensTransformOpts
from penelope.utility import flatten
from penelope.utility.tags import SUC_PoS_tag_groups
from penelope.workflows import vectorize_sparv_csv_corpus_workflow, vectorize_tokenized_corpus_workflow

# logger = getLogger('corpus_text_analysis')

# pylint: disable=attribute-defined-outside-init, too-many-instance-attributes
layout_default = widgets.Layout(width='200px')
layout_button = widgets.Layout(width='140px')


@dataclass
class GUI:
    input_filename_chooser = ipyfilechooser.FileChooser(
        path=str(Path.home()),
        filter_pattern='*_vectorizer_data.pickle',
        title='<b>Source corpus file</b>',
        show_hidden=False,
        select_default=False,
        use_dir_icons=True,
        show_only_dirs=False,
    )
    corpus_type = widgets.Dropdown(
        description='', options=['text', 'sparv4-csv'], value='sparv4-csv', layout=layout_default
    )
    output_folder_chooser = ipyfilechooser.FileChooser(
        path=str(Path.home()),
        title='<b>Output folder</b>',
        show_hidden=False,
        select_default=True,
        use_dir_icons=True,
        show_only_dirs=True,
    )
    output_tag = widgets.Text(
        value='',
        placeholder='Tag to prepend filenames',
        description='',
        disabled=False,
        layout=layout_default,
    )
    pos_includes = widgets.SelectMultiple(
        options=SUC_PoS_tag_groups,
        value=[SUC_PoS_tag_groups['Noun'], SUC_PoS_tag_groups['Verb']],
        rows=8,
        description='',
        disabled=False,
        layout=layout_default,
    )
    count_threshold = widgets.IntSlider(description='', min=1, max=1000, step=1, value=1, layout=layout_default)
    filename_fields = widgets.Text(
        value=r"year:prot\_(\d{4}).*",
        placeholder='Fields to extract from filename (regex)',
        description='',
        disabled=False,
        layout=layout_default,
    )
    lemmatize = widgets.ToggleButton(value=True, description='Lemmatize', icon='check', layout=layout_button)
    to_lowercase = widgets.ToggleButton(value=True, description='To Lower', icon='check', layout=layout_button)
    remove_stopwords = widgets.ToggleButton(value=True, description='No Stopwords', icon='check', layout=layout_button)
    only_alphabetic = widgets.ToggleButton(value=False, description='Only Alpha', icon='', layout=layout_button)
    only_any_alphanumeric = widgets.ToggleButton(
        value=False, description='Only Alphanum', icon='', layout=layout_button
    )
    extra_stopwords = widgets.Textarea(
        value='örn',
        placeholder='Enter extra stop words',
        description='',
        disabled=False,
        rows=8,
        layout=widgets.Layout(width='350px'),
    )
    button = widgets.Button(
        description='Vectorize!',
        button_style='Success',
        layout=layout_button,
    )
    output = widgets.Output()

    @property
    def tokens_transform_opts(self):

        extra_stopwords = None

        if self.extra_stopwords.value.strip() != '':
            _words = [x for x in map(str.strip, self.extra_stopwords.value.strip().split()) if x != '']
            if len(_words) > 0:
                extra_stopwords = _words

        return TokensTransformOpts(
            remove_stopwords=self.remove_stopwords.value,
            to_lower=self.to_lowercase.value,
            only_alphabetic=self.only_alphabetic.value,
            only_any_alphanumeric=self.only_any_alphanumeric.value,
            extra_stopwords=extra_stopwords,
        )

    @property
    def annotations_opts(self):
        return AnnotationOpts(
            pos_includes=f"|{'|'.join(flatten(self.pos_includes.value))}|",
            pos_excludes="|MAD|MID|PAD|",
            lemmatize=self.lemmatize.value,
            passthrough_tokens=set()
        )

    def layout(self):

        return widgets.VBox(
            [
                widgets.HBox(
                    [
                        widgets.VBox(
                            [
                                widgets.HTML("<b>Corpus type</b>"),
                                self.corpus_type,
                            ]
                        ),
                        self.input_filename_chooser,
                    ]
                ),
                widgets.HBox(
                    [
                        widgets.VBox(
                            [
                                widgets.HTML("<b>Output tag</b>"),
                                self.output_tag,
                            ]
                        ),
                        self.output_folder_chooser,
                    ]
                ),
                widgets.HBox(
                    [
                        widgets.VBox(
                            [
                                widgets.HTML("<b>Part-Of-Speech tags</b>"),
                                self.pos_includes,
                            ]
                        ),
                        widgets.VBox(
                            [
                                widgets.HTML("<b>Extra stopwords</b>"),
                                self.extra_stopwords,
                            ]
                        ),
                    ]
                ),
                widgets.HBox(
                    [
                        widgets.VBox(
                            [
                                widgets.VBox(
                                    [
                                        widgets.HTML("<b>Filename fields</b>"),
                                        self.filename_fields,
                                    ]
                                ),
                                widgets.VBox(
                                    [
                                        widgets.HTML("<b>Frequency threshold</b>"),
                                        self.count_threshold,
                                    ]
                                ),
                            ]
                        ),
                        widgets.VBox(
                            [
                                widgets.HBox(
                                    [
                                        widgets.VBox(
                                            [
                                                self.lemmatize,
                                                self.to_lowercase,
                                                self.remove_stopwords,
                                            ]
                                        ),
                                        widgets.VBox(
                                            [
                                                self.only_alphabetic,
                                                self.only_any_alphanumeric,
                                                self.button,
                                            ]
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
                self.output,
            ]
        )


def display_gui(
    corpus_pattern: str, generated_callback: Callable[[widgets.Output, str, str], None]
):  # pylint: disable=too-many-statements

    gui = GUI()
    gui.input_filename_chooser.filter_pattern = corpus_pattern

    def on_button_clicked(_):

        try:

            with gui.output:

                if not gui.input_filename_chooser.selected:
                    raise ValueError("please specify corpus file")

                if not gui.output_folder_chooser.selected:
                    raise ValueError("please specify output folder")

                input_filename = gui.input_filename_chooser.selected
                output_folder = gui.output_folder_chooser.selected

                if not os.path.isfile(input_filename):
                    raise FileNotFoundError(input_filename)

                output_tag = gui.output_tag.value.strip()

                if output_tag == "":
                    raise ValueError("please specify a unique string that will be prepended to output file")

                gui.button.disabled = True

                _workflow = (
                    vectorize_sparv_csv_corpus_workflow
                    if gui.corpus_type.value == 'sparv4-csv'
                    else vectorize_tokenized_corpus_workflow
                )

                v_corpus = _workflow(
                    input_filename=input_filename,
                    output_folder=output_folder,
                    output_tag=output_tag,
                    filename_field=gui.filename_fields.value,
                    count_threshold=gui.count_threshold.value,
                    annotation_opts=gui.annotations_opts,
                    tokens_transform_opts=gui.tokens_transform_opts,
                )

                if generated_callback is not None:
                    generated_callback(
                        output=gui.output,
                        corpus=v_corpus,
                        corpus_tag=gui.output_tag.value,
                        corpus_folder=output_folder,
                    )

                gui.button.disabled = False

        except Exception as ex:
            print(ex)

    def corpus_type_changed(*_):
        gui.pos_includes.disabled = gui.corpus_type.value == 'text'
        gui.lemmatize.disabled = gui.corpus_type.value == 'text'

    def toggle_state_changed(event):
        with gui.output:
            try:
                event['owner'].icon = 'check' if event['new'] else ''
            except Exception as ex:
                print(event)
                print(ex)

    def remove_stopwords_state_changed(*_):
        gui.extra_stopwords.disabled = not gui.remove_stopwords.value

    gui.button.on_click(on_button_clicked)
    gui.corpus_type.observe(corpus_type_changed, 'value')
    gui.lemmatize.observe(toggle_state_changed, 'value')
    gui.to_lowercase.observe(toggle_state_changed, 'value')
    gui.remove_stopwords.observe(toggle_state_changed, 'value')
    gui.remove_stopwords.observe(remove_stopwords_state_changed, 'value')
    gui.only_alphabetic.observe(toggle_state_changed, 'value')
    gui.only_any_alphanumeric.observe(toggle_state_changed, 'value')

    return gui.layout()
