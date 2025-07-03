'''The main entry point for the Streamlit app.'''

import streamlit as st
from state_manager import initialize_state
from tabs.add_words.add_words_tab import render_add_words_tab
from tabs.db_status.db_status_tab import render_db_status_tab
from tabs.explore_words.explore_words_tab import render_explore_words_tab
from tabs.learning.learning_tab import render_learning_tab
from tabs.recall.recall_tab import render_recall_tab

# configure the page
st.set_page_config(
    page_title="Woorden in hun context",
    page_icon=":material/school:",
    layout="centered",
    initial_sidebar_state="collapsed",
)
# initialize the state variables
initialize_state()

# recall in dutch is "herinnering"

tabs = st.tabs(["Woorden Toevoegen", "Leersessie", "Herinnering",
               "Woorden Ontdekken", "Databasestatus"])

with tabs[0]:
    st.header("Voeg nieuwe woorden toe")
    render_add_words_tab()

with tabs[1]:
    render_learning_tab()

with tabs[2]:
    render_recall_tab()

with tabs[3]:
    st.header("Ontdek nieuwe woorden")
    render_explore_words_tab()

with tabs[4]:
    render_db_status_tab()


# add a sidebar with a text area in;  default hidden

st.sidebar.header("Notities")
st.sidebar.text_area(
    "Voeg hier je notities toe",
    key="sidebar_notes",
    placeholder="Schrijf hier je gedachten..."
)
