'''The main entry point for the Streamlit app.'''

import streamlit as st
from state_manager import initialize_state
from tabs.add_words.add_words_tab import render_add_words_tab
from tabs.db_status.db_status_tab import render_db_status_tab
from tabs.explore_words.explore_words_tab import render_explore_words_tab
from tabs.learning.learning_tab import render_learning_tab

# configure the page
st.set_page_config(
    page_title="Woorden in hun context",
    page_icon=":material/school:",
    layout="centered",
    initial_sidebar_state="expanded"
)
# initialize the state variables
initialize_state()

tabs = st.tabs(["Woorden Toevoegen", "Leersessie",
               "Woorden Ontdekken", "Databasestatus"])

with tabs[0]:
    st.header("Voeg nieuwe woorden toe")
    render_add_words_tab()

with tabs[1]:
    render_learning_tab()

with tabs[2]:
    render_explore_words_tab()

with tabs[3]:
    render_db_status_tab()


# do something about the Vergelijkingen part, make sure the model produces something, use synonyms, etc. 
