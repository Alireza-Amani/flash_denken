'''Recall tab'''
import streamlit as st
from tabs.recall.recall_tab_widgets import (
    select_recall_words_button,
    start_recall_session_button, end_recall_session_button,
)


def render_recall_tab():
    """Renders the "Recall" tab."""
    st.header("Herinneringssessie")

    select_recall_words_button()
    start_recall_session_button()
    end_recall_session_button()
