'''The widgets for the "Database Status" tab.'''

import streamlit as st

# a button to trigger showing the dataframes


def show_dataframes_callback():
    """Renders a button to trigger showing the dataframes."""
    st.session_state["trigger_show_dataframes"] = True


def show_dataframes_button_db_status_tab():
    """Renders a button to show the dataframes in the "Database Status" tab."""
    st.button(
        "Toon DataFrames",
        key="show_dataframes_button_db_status_tab_key",
        on_click=show_dataframes_callback
    )
