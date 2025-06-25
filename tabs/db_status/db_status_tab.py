'''The "Database Status" tab.'''

import streamlit as st
from db_operations import get_words_practice_tables
from tabs.db_status.db_status_tab_widgets import show_dataframes_button_db_status_tab


def render_db_status_tab():
    """Renders the "Database Status" tab."""
    show_dataframes_button_db_status_tab()

    if st.session_state.get("trigger_show_dataframes", False):
        words_df, practice_df, recall_prompts_df = get_words_practice_tables()
        st.write("Words DataFrame:")
        st.dataframe(words_df)
        st.write("Practice Sessions DataFrame:")
        st.dataframe(practice_df)
        st.write("Recall Prompts DataFrame:")
        st.dataframe(recall_prompts_df)
    else:
        st.write("Klik op de knop hieronder om de dataframes te tonen.")


# this tab could use another table, where the user will select a learning package,
#  grounded on SRS.
