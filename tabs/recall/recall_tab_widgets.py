
import streamlit as st
from db_operations import load_word_analyses_by_ids
from ebisu_tools import calculate_all_recall_probabilities_from_db

# a button to sample words to recall


def select_recall_words_callback():
    """Callback function to select words for recall."""

    # for now, simply get the word with id 1
    word_analyses = load_word_analyses_by_ids([1])
    st.session_state.word_analyses_to_recall_list.extend(word_analyses)

    st.session_state.recall_probabilities_df = calculate_all_recall_probabilities_from_db()


def select_recall_words_button():
    """Renders a button to select words for recall."""

    st.button(
        "Selecteer woorden om te herinneren",
        key="select_recall_words_button_key",
        on_click=select_recall_words_callback,
        help="Selecteer woorden om te herinneren. "
             "Als er nog geen woorden zijn geselecteerd, "
             "worden de woorden met id 1 geselecteerd.",
        use_container_width=True,
        icon=":material/precision_manufacturing:",  # icon size
    )


def start_recall_session_callback():
    """Callback function to start the recall session."""
    st.session_state.start_recall_session = True


def start_recall_session_button():
    """Renders a button to start the recall session."""

    is_disabled = (
        st.session_state.start_recall_session or
        not st.session_state.word_analyses_to_recall_list
    )
    st.button(
        "Start Herinneringsessie",
        key="start_recall_session_button_key",
        on_click=start_recall_session_callback,
        disabled=is_disabled,
        help="Start de herinneringsessie. "
             "Als er nog geen woorden zijn geselecteerd, "
             "wordt de herinneringsessie niet gestart.",
        use_container_width=True,
        icon=":material/play_circle:",  # icon size
    )


def end_recall_session_callback():
    """Callback function to end the recall session."""
    st.session_state.start_recall_session = False

    # empty the list of word analyses to recall
    st.session_state.word_analyses_to_recall_list.clear()


def end_recall_session_button():
    """Renders a button to end the recall session."""

    is_disabled = not st.session_state.start_recall_session
    st.button(
        "Eindig Herinneringsessie",
        key="end_recall_session_button_key",
        on_click=end_recall_session_callback,
        disabled=is_disabled,
        help="Eindig de herinneringsessie.",
        use_container_width=True,
        icon=":material/stop_circle:",  # icon size
    )
