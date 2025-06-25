'''Initializes the state variables for the Streamlit app.'''

from pandas import DataFrame
from parameters import Parameters
from db_operations import get_words_already_in_db
import streamlit as st
from output_models import HerinneringsTest, AnalysisResult

stvar_list = [
    "new_words_to_generate_list",  # List[str]
    "new_words_for_recall_prompts_list",  # List[str]
    "word_analyses_to_learn_list",  # List[WordAnalysis]
    "word_ids_to_learn_list",  # List[int]
    "uploaded_images_list",  # List[UploadedFile]
    "video_urls_list",  # List[str]
    "current_word_user_media_list",  # List[Dict[str, str]]
    "word_analyses_to_recall_list",  # List[WordAnalysis]
]

stvar_str = [

    "word_to_explore",

    # related to user written thought scenario in the learning session
    "user_thought_title",
    "user_thought_situation",
    "user_thought_internal_monologue",
    "user_thought_expression",
]

stvar_int = [
    "word_id_to_explore",
    "number_of_words_to_learn",
    "current_word_idx_to_learn",
]

stvar_bool = [
    # related to the process of generating/saving words
    "trigger_save_db",
    "trigger_save_recall_prompts_db",
    "trigger_cleanup_after_gemini",
    "trigger_cleanup_after_db_save",

    # database status
    "trigger_show_dataframes",

    # related to the process of exploring words
    "trigger_retrieve_explore_word_from_db",

    # related to the process of learning words
    "start_learning_session",
    "current_word_is_learned",

    # a couple of flags to finalize learning of a word
    "thought_scenario_created",
    "image_added",
    "video_added",

    "save_user_thought_scenario",
    "trigger_redisplay_learning_word_thought",

    # recall tab
    "start_recall_session",
    "current_recall_word_idx",
    "current_recall_word_is_studied",



]

stvar_df = [
    "words_table_df",
    "practice_table_df",
    "recall_prompts_table_df",
    "recall_probabilities_df",
]


def initialize_state():
    """Initializes the state variables for the Streamlit app."""

    print("Initializing state variables...")

    # lists
    for var in stvar_list:
        if var not in st.session_state:
            st.session_state[var] = []

    # strings
    for var in stvar_str:
        if var not in st.session_state:
            st.session_state[var] = ""

    # integers
    for var in stvar_bool:
        if var not in st.session_state:
            st.session_state[var] = False

    # booleans
    for var in stvar_df:
        if var not in st.session_state:
            st.session_state[var] = DataFrame()

    # dataframes
    for var in stvar_int:
        if var not in st.session_state:
            st.session_state[var] = 0

    # custom classes
    # Parameters
    if "parameters" not in st.session_state:
        st.session_state["parameters"] = Parameters()

    # generated analyses
    if "generated_analyses" not in st.session_state:
        st.session_state["generated_analyses"] = AnalysisResult(
            analyses=[])

    # generated recall prompts
    if "generated_recall_prompts" not in st.session_state:
        st.session_state["generated_recall_prompts"] = HerinneringsTest(
            gegenereerde_prompts=[])

    # word to explore
    if "word_analysis_to_explore" not in st.session_state:
        st.session_state["word_analysis_to_explore"] = None  # `WordAnalysis`

    # word to learn
    if "word_analysis_to_learn" not in st.session_state:
        st.session_state["word_analysis_to_learn"] = None  # `WordAnalysis`

    # manual initialization
    if "words_already_in_db_list" not in st.session_state:
        st.session_state["words_already_in_db_list"] = get_words_already_in_db()

        print(
            f"Words already in DB: {st.session_state['words_already_in_db_list']}"
        )
