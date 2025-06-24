'''The "Add Words" tab.'''
import streamlit as st
from tabs.add_words.add_words_tab_widgets import (
    word_input_addtab, generate_analyses_button_addtab,
    save_analyses_to_db_button_addtab,
)


def render_add_words_tab():
    """Renders the "Add Words" tab."""

    if st.session_state.get("trigger_cleanup_after_gemini", False):
        st.session_state["trigger_cleanup_after_gemini"] = False
        st.session_state["new_words_to_generate_list"] = []
        st.rerun()

    if st.session_state.get("trigger_cleanup_after_db_save", False):
        st.session_state["trigger_cleanup_after_db_save"] = False
        del st.session_state["generated_analyses"]
        del st.session_state["words_already_in_db_list"]
        st.rerun()

    # input box for entering a word
    word_input_addtab()

    # a button to generate the analyses
    generate_analyses_button_addtab()

    # a button to save the analyses to the database
    save_analyses_to_db_button_addtab()
