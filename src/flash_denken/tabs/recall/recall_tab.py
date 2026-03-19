'''Recall tab'''
import streamlit as st
from .recall_tab_widgets import (
    display_widgets_recall_tab, present_prompts_for_recall, word_analysis_material,
    remember_buttons,
)


def render_recall_tab():
    """Renders the "Recall" tab."""
    st.header("Herinneringssessie")

    display_widgets_recall_tab()

    # display the prompts for the current recall session
    if st.session_state.start_recall_session:
        present_prompts_for_recall()
        st.divider()
        remember_buttons()
        st.divider()
        word_analysis_material()
