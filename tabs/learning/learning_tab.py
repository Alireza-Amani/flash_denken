'''This module defines the "Learning" tab for the Streamlit application.'''
from PIL import Image
import io
import streamlit as st
from html_generation import generate_word_html_design, embed_video
from tabs.learning.learning_tab_widgets import (
    input_number_of_words_to_learn, start_learning_session_button,
    sample_words_to_learn_button, end_learning_session_button,
    next_word_button, previous_word_button,
    mark_word_learned_button, display_user_videos, user_personalization_widgets,
    get_user_media, display_user_images,
    add_words_to_learning_list,

)


def render_learning_tab():
    """Renders the "Learning" tab."""

    add_words_to_learning_list()
    st.divider()
    input_number_of_words_to_learn()
    sample_words_to_learn_button()
    start_learning_session_button()
    end_learning_session_button()
    st.divider()
    col1, col2 = st.columns([1, 1])
    with col1:
        previous_word_button()
    with col2:
        next_word_button()
    st.divider()

    if st.session_state.get("start_learning_session", None):
        idx = st.session_state.get("current_word_idx_to_learn", 0)
        word_id = list(
            st.session_state["words_in_learning_status_dict"].keys())[idx]
        get_user_media(word_id)

        word_analysis = st.session_state["words_in_learning_status_dict"][word_id]["word_analysis"]
        st.session_state["word_analysis_to_learn"] = word_analysis
        st.html(generate_word_html_design(word_analysis))
        st.divider()

        # display each image, if any
        display_user_images()
        st.divider()

        # display each video, if any
        display_user_videos()
        st.divider()

        user_personalization_widgets()

        if st.session_state.get("user_thought_scenario_saved", False):
            st.session_state["user_thought_scenario_saved"] = False
            st.rerun()

        st.divider()
        mark_word_learned_button()
