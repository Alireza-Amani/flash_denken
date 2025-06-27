'''The widgets for the "Database Status" tab.'''

import streamlit as st
from db_operations import remove_words_by_ids, remove_words_by_terms

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

# input area for ids and words
# they will be turned into lists of ids and words


def show_input_area():
    """Renders an input area for IDs and words in the "Database Status" tab."""

    st.write("Voer IDs of woorden in om ze te verwijderen uit de database.")
    st.text_input(
        "ID (optioneel):",
        key="ids_input_verwijderen_key",
        placeholder="Voer een ID in, of meerdere IDs gescheiden door komma's of nieuwe regels.",
        help="Voer een ID in, of meerdere IDs gescheiden door komma's of nieuwe regels."
    )
    st.text_input(
        "Woord (optioneel):",
        key="woorden_input_verwijderen_key",
        placeholder="Voer een woord in, of meerdere woorden gescheiden door komma's of nieuwe regels.",
        help="Voer een woord in, of meerdere woorden gescheiden door komma's of nieuwe regels."
    )


def remove_words_callback(ids: str = "", words: str = ""):
    """Callback function to remove words by IDs or words."""
    # ids or words are separated by commas or new lines
    if ids:
        ids_list = [int(id.strip()) for id in ids.split(",") if id.strip()]
        remove_words_by_ids(ids_list)
        print(
            f"De volgende IDs zijn verwijderd: {', '.join(map(str, ids_list))}")

    if words:
        words_list = [word.strip()
                      for word in words.split(",") if word.strip()]
        remove_words_by_terms(words_list)
        print(f"De volgende woorden zijn verwijderd: {', '.join(words_list)}")

    # clear the input fields after removing words
    st.session_state["ids_input_verwijderen_key"] = ""
    st.session_state["woorden_input_verwijderen_key"] = ""


def show_danger_zone():
    """Renders the danger zone in the "Database Status" tab."""
    st.subheader("Danger Zone")
    st.write(
        "Wees voorzichtig met het verwijderen van woorden of IDs. "
        "Dit kan niet ongedaan worden gemaakt."
    )
    show_input_area()
    ids = st.session_state.get("ids_input_verwijderen_key", "")
    words = st.session_state.get("woorden_input_verwijderen_key", "")

    is_disabled = not (ids or words)
    st.button(
        "Verwijder Woorden",
        key="remove_words_button_key",
        on_click=remove_words_callback,
        args=(ids, words),
        help="Klik om de opgegeven woorden of IDs te verwijderen uit de database.",
        disabled=is_disabled
    )
