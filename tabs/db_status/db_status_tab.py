'''The "Database Status" tab.'''

import streamlit as st
from db_operations import get_words_practice_tables
from tabs.db_status.db_status_tab_widgets import (
    show_dataframes_button_db_status_tab, show_danger_zone
)
from ebisu_tools import calculate_all_recall_probabilities_from_db


def render_db_status_tab():
    """Renders the "Database Status" tab."""
    show_dataframes_button_db_status_tab()

    if st.session_state.get("trigger_show_dataframes", False):
        get_words_practice_tables()
        # lets add recall probabilities to the words_df
        calculate_all_recall_probabilities_from_db()
        st.write("Words DataFrame:")
        st.dataframe(st.session_state.get("words_table_df"))
        st.divider()
        st.write("Practice Sessions DataFrame:")
        st.dataframe(st.session_state.get("practice_table_df"))
        st.divider()
        st.write("Recall Probabilities DataFrame:")
        st.dataframe(st.session_state.get("recall_probabilities_df"))
        st.divider()
        st.write("Recall Prompts DataFrame:")
        st.dataframe(st.session_state.get("recall_prompts_table_df"))
    else:
        st.write("Klik op de knop hieronder om de dataframes te tonen.")

    # this st.empty() is used to create space between the dataframes and the next section
    st.empty()
    # a danger area, for removing some data from database, based on ID or word
    with st.expander(
        "Gevarenzone: Verwijder Woorden uit de Database", expanded=False,
        icon=":material/delete:"
    ):
        show_danger_zone()

# this tab could use another table, where the user will select a learning package,
#  grounded on SRS.
