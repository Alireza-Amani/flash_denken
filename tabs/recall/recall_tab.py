'''Recall tab'''
import streamlit as st
from tabs.recall.recall_tab_widgets import display_widgets_recall_tab, present_prompts_for_recall
from html_generation import generate_prompt_card_html, generate_word_html_design


def render_recall_tab():
    """Renders the "Recall" tab."""
    st.header("Herinneringssessie")

    display_widgets_recall_tab()

    # display the prompts for the current recall session
    if st.session_state.start_recall_session:
        present_prompts_for_recall()
