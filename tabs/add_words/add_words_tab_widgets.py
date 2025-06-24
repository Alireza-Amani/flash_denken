'''The widgets for the "Add Words" tab.'''

import streamlit as st
from gemini import generate_word_analysis
from db_operations import save_analysis_result_to_db
from utils import get_unique_new_words, parse_words_input


def word_input_addtab():
    """Input box for entering a word."""
    label = "Voer je woorden in"
    help_text = (
        "Je kunt meerdere woorden toevoegen door ze te scheiden met komma's of "
        "door ze op nieuwe regels te plaatsen."
    )
    st.caption(help_text)
    user_new_words_list = parse_words_input(st.text_area(
        label, placeholder="bijv. 'huis'", key="word_input_addtab"
    ))

    # only keep unique new words
    truly_new_words_list = get_unique_new_words(
        st.session_state["words_already_in_db_list"],
        user_new_words_list
    )

    repeated_words = set(user_new_words_list) & set(
        st.session_state["words_already_in_db_list"]
    )

    # mention which words are already in the database
    if repeated_words:
        st.caption(
            f"Deze woorden zijn al in de database: {', '.join(repeated_words)}"
        )

    # show the unique new words
    if truly_new_words_list:
        st.caption(
            f"Deze woorden zijn nieuw: {', '.join(truly_new_words_list)}"
        )
    else:
        st.caption("Er zijn geen nieuwe woorden toegevoegd.")

    # store the unique new words in the session state
    st.session_state["new_words_to_generate_list"] = truly_new_words_list

# a button to generate the analyses


def generate_analyses_button_callback():
    """Callback function for the 'Generate Analyses' button."""
    st.session_state["generated_analyses"] = generate_word_analysis(
        st.session_state["new_words_to_generate_list"]
    )
    st.session_state["trigger_save_db"] = True
    st.session_state["trigger_cleanup_after_gemini"] = True


def generate_analyses_button_addtab():
    """Button to generate analyses for the new words."""

    is_disabled = not st.session_state.get("new_words_to_generate_list", [])

    st.button(
        "Genereer en sla analyses op",
        on_click=generate_analyses_button_callback,
        disabled=is_disabled,
        icon=":material/smart_toy:",
        help="Genereer analyses voor de nieuwe woorden en sla ze op in de database.",
        type="primary",
        use_container_width=True,
        key="generate_analyses_button_addtab_key"
    )


def save_analyses_db_callback():
    """Callback function for the 'Save Analyses to DB' button."""

    save_analysis_result_to_db(
        st.session_state["generated_analyses"]
    )
    st.session_state["trigger_save_db"] = False
    st.session_state["trigger_cleanup_after_db_save"] = True


def save_analyses_to_db_button_addtab():
    """Button to save the generated analyses to the database."""

    is_disabled = not st.session_state.get("trigger_save_db", False)

    st.button(
        "Sla analyses op in de database",
        on_click=save_analyses_db_callback,
        disabled=is_disabled,
        icon=":material/database:",
        help="Sla de gegenereerde analyses op in de database.",
        type="primary",
        use_container_width=True,
        key="save_analyses_to_db_button_addtab_key"
    )
