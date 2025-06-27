
import streamlit as st
from db_operations import get_ids_given_words, load_word_analyses_by_ids

# i want an input field where user can enter a word or an integer


def word_or_integer_input_explore_tab():
    """Renders an input field for a word or an integer."""
    input_value = st.text_input(
        "Voer een woord of een getal (woord-ID) in:",
        key="word_or_integer_input_key"
    )

    input_value = input_value.strip()
    try:
        int_value = int(input_value)
        st.session_state["word_id_to_explore"] = int_value
        st.session_state["word_to_explore"] = ""
        st.session_state["trigger_retrieve_explore_word_from_db"] = True
    except ValueError:
        st.session_state["word_to_explore"] = input_value
        potential_id = list(get_ids_given_words([input_value]).keys())
        if potential_id:
            st.session_state["word_id_to_explore"] = potential_id[0]
        else:
            st.session_state["word_id_to_explore"] = 0
        st.session_state["trigger_retrieve_explore_word_from_db"] = True
    except Exception as e:
        print(f"Error processing input: {e}")


def retrieve_explore_word_from_db_callback():
    """Callback to retrieve the word to explore from the database."""

    if st.session_state.get("word_id_to_explore", 0):
        word_id = st.session_state["word_id_to_explore"]
        if word_id > 0:
            st.session_state["word_analysis_to_explore"] = load_word_analyses_by_ids(
                [word_id])[0]
        else:
            print("Ongeldige woord-ID opgegeven.")
    else:
        print("Voer een woord of een geldige woord-ID in.")


def retrieve_explore_word_from_db_button():
    """Renders a button to retrieve the word to explore from the database."""
    is_disabled = not st.session_state.get("word_id_to_explore", 0)
    st.button(
        "Haal woord op uit de database",
        key="retrieve_explore_word_from_db_button_key",
        on_click=retrieve_explore_word_from_db_callback,
        disabled=is_disabled
    )
