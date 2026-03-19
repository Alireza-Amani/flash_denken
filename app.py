'''The main entry point for the Streamlit app.'''

import sys
import os
from dotenv import load_dotenv

import streamlit as st

# Load environment variables from .env file
loaded = load_dotenv()
print(f".env loaded: {loaded}")
print(f"GEMINI_API_KEY from os: {os.getenv('GEMINI_API_KEY')}")

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from flash_denken.state_manager import initialize_state
from flash_denken.tabs.add_words.add_words_tab import render_add_words_tab
from flash_denken.tabs.db_status.db_status_tab import render_db_status_tab
from flash_denken.tabs.explore_words.explore_words_tab import \
    render_explore_words_tab
from flash_denken.tabs.learning.learning_tab import render_learning_tab
from flash_denken.tabs.recall.recall_tab import render_recall_tab

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
