'''Explore Words Tab'''
import streamlit as st
from html_generation import generate_word_html_design
from tabs.explore_words.explore_words_tab_widgets import (
    word_or_integer_input_explore_tab, retrieve_explore_word_from_db_button,
    fetch_thought_scenario_button, display_thought_scenario, save_thought_scenario_button,
    fetch_user_images_button, save_user_images_button, display_user_images,
)
from tabs.learning.learning_tab_widgets import (
    get_user_media, display_user_images, display_user_videos,
)


def render_explore_words_tab():
    """Renders the "Explore Words" tab."""
    word_or_integer_input_explore_tab()
    retrieve_explore_word_from_db_button()
    get_user_media(
        st.session_state.get("word_id_to_explore", None)
    )

    if st.session_state.get("word_analysis_to_explore", None):
        st.html(generate_word_html_design(
            st.session_state["word_analysis_to_explore"],))

        st.divider()
        # display each image, if any
        display_user_images()
        st.divider()
        # display each video, if any
        display_user_videos()
        st.divider()

        # an expander for content modification
        with st.expander("Gedachte Scenario", expanded=True):
            fetch_thought_scenario_button()
            save_thought_scenario_button()
            display_thought_scenario()

        with st.expander("Media", expanded=False):
            fetch_user_images_button()
            save_user_images_button()
            display_user_images()
