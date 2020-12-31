# type: ignore
from ._color_utility import (
    DEFAULT_ALL_PALETTES,
    DEFAULT_LINE_PALETTE,
    DEFAULT_PALETTE,
    ColorGradient,
    StaticColorMap,
    get_static_color_map,
    static_color_map,
)
from ._decorators import ExpectException, deprecated, try_catch
from .file_utility import (
    DataFrameFilenameTuple,
    compress_file,
    create_iterator,
    default_data_folder,
    excel_to_csv,
    find_folder,
    find_parent_folder,
    find_parent_folder_with_child,
    list_filenames,
    pandas_read_csv_zip,
    pandas_to_csv_zip,
    pickle_compressed_to_file,
    pickle_to_file,
    read_excel,
    read_from_archive,
    read_json,
    read_textfile,
    save_excel,
    store_to_archive,
    unpickle_compressed_from_file,
    unpickle_from_file,
    write_json,
    zip_get_filenames,
    zip_get_text,
)
from .filename_fields import (
    FilenameFieldSpec,
    FilenameFieldSpecs,
    extract_filename_metadata,
    extract_filenames_metadata,
)
from .filename_utils import (
    VALID_CHARS,
    assert_that_path_exists,
    data_path_ts,
    filename_satisfied_by,
    filename_whitelist,
    filter_names_by_pattern,
    now_timestamp,
    path_add_date,
    path_add_sequence,
    path_add_suffix,
    path_add_timestamp,
    path_of,
    replace_extension,
    replace_path,
    strip_path_and_add_counter,
    strip_path_and_extension,
    strip_paths,
    suffix_filename,
    timestamp_filename,
    ts_data_path,
)
from .mixins import PropsMixIn
from .pos_tags import Known_PoS_Tag_Schemes, PoS_Tag_Scheme, PoS_Tag_Schemes, PoS_TAGS_SCHEMES, get_pos_schema
from .utils import (
    LOG_FORMAT,
    DummyContext,
    ListOfDicts,
    assert_is_strictly_increasing,
    chunks,
    clamp_values,
    complete_value_range,
    dataframe_to_tuples,
    dict_of_key_values_inverted_to_dict_of_value_key,
    dict_of_lists_to_list_of_dicts,
    dict_split,
    dict_subset,
    dict_to_list_of_tuples,
    extend,
    extend_single,
    extract_counter_items_within_threshold,
    filter_dict,
    filter_kwargs,
    flatten,
    get_func_args,
    get_logger,
    getLogger,
    ifextend,
    inspect_default_opts,
    inspect_filter_args,
    is_platform_architecture,
    is_strictly_increasing,
    isint,
    iter_windows,
    lazy_flatten,
    left_chop,
    list_of_dicts_to_dict_of_lists,
    list_to_unique_list_with_preserved_order,
    lists_of_dicts_merged_by_key,
    ls_sorted,
    noop,
    normalize_array,
    normalize_sparse_matrix_by_vector,
    normalize_values,
    nth,
    pretty_print_matrix,
    project_series_to_range,
    project_to_range,
    project_values_to_range,
    remove_snake_case,
    right_chop,
    slim_title,
    sort_chained,
    split,
    take,
    timecall,
    timestamp,
    to_text,
    trunc_year_by,
    tuple_of_lists_to_list_of_tuples,
    uniquify,
)
