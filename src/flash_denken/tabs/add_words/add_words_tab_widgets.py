'''The widgets for the "Add Words" tab.'''

import streamlit as st
from flash_denken.gemini import generate_word_analysis, generate_recall_prompts
from flash_denken.db_operations import (
    save_analysis_result_to_db, save_term_prompts_to_db, find_word_without_prompts,
)
from flash_denken.utils import get_unique_new_words, parse_words_input


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
        # report the number of new words
        st.caption(
            f"Er zijn {len(truly_new_words_list)} nieuwe woorden toegevoegd."
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

    # now is the time to populate the `new_words_for_recall_prompts_list`
    # before they are cleaned up
    st.session_state["new_words_for_recall_prompts_list"] = (
        st.session_state["new_words_to_generate_list"]
    )

    # clean up the new words list
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

# similarly, lets have generation and save for the recall prompts


def generate_recall_prompts_button_callback():
    """Callback function for the 'Generate Recall Prompts' button."""
    st.session_state["generated_recall_prompts"] = generate_recall_prompts(
        st.session_state["new_words_for_recall_prompts_list"]
    ).gegenereerde_prompts

    # clean up the list
    st.session_state["new_words_for_recall_prompts_list"] = []


def generate_recall_prompts_button_addtab():
    """Button to generate recall prompts for the new words."""

    is_disabled = not st.session_state.get(
        "new_words_for_recall_prompts_list", []
    )

    st.button(
        "Genereer en sla herinneringsprompts op",
        on_click=generate_recall_prompts_button_callback,
        disabled=is_disabled,
        icon=":material/smart_toy:",
        help="Genereer herinneringsprompts voor de nieuwe woorden en sla ze op in de database.",
        type="primary",
        use_container_width=True,
        key="generate_recall_prompts_button_addtab_key"
    )


def save_recall_prompts_db_callback():
    """Callback function for the 'Save Recall Prompts to DB' button."""
    save_term_prompts_to_db(
        st.session_state["generated_recall_prompts"]
    )
    del st.session_state["generated_recall_prompts"]


def save_recall_prompts_to_db_button_addtab():
    """Button to save the generated recall prompts to the database."""

    is_disabled = not st.session_state.get("generated_recall_prompts", False)

    st.button(
        "Sla herinneringsprompts op in de database",
        on_click=save_recall_prompts_db_callback,
        disabled=is_disabled,
        icon=":material/database:",
        help="Sla de gegenereerde herinneringsprompts op in de database.",
        type="primary",
        use_container_width=True,
        key="save_recall_prompts_to_db_button_addtab_key"
    )


def words_without_prompt_callback():
    """Callback function for the 'Words Without Prompts' button."""
    st.session_state["words_without_prompts"] = find_word_without_prompts()

    # merge it with `new_words_for_recall_prompts_list`, their union
    st.session_state["new_words_for_recall_prompts_list"] = (
        st.session_state["new_words_for_recall_prompts_list"] +
        st.session_state["words_without_prompts"]
    )


def words_without_prompt_button_addtab():
    """Button to find words without prompts."""
    st.button(
        "Zoek woorden zonder prompts",
        on_click=words_without_prompt_callback,
        use_container_width=True,
        key="words_without_prompt_button_addtab_key"
    )


# three input numbers for ebisu parameters
# they will be used to save the words in the database with different parameters

def ebisu_parameters_input_addtab():
    """Input fields for Ebisu parameters."""
    st.caption(
        "Voer de Ebisu parameters in voor de nieuwe woorden. "
        "Deze worden gebruikt om de woorden op te slaan in de database."
    )
    st.number_input(
        "Alpha ",
        min_value=2.0,
        max_value=10.0,
        step=0.1,
        format="%.1f",
        value=st.session_state["parameters"].ebisu_alpha,
        key="ebisu_alpha_input_key",
        help="De alpha parameter voor Ebisu. "
             "Hoe hoger de waarde, hoe sneller de woorden worden geleerd.",
        label_visibility="collapsed",
    )

    st.number_input(
        "Beta ",
        min_value=2.0,
        max_value=10.0,
        step=0.1,
        format="%.1f",
        value=st.session_state["parameters"].ebisu_beta,
        key="ebisu_beta_input_key",
        help="De beta parameter voor Ebisu. "
             "Hoe hoger de waarde, hoe sneller de woorden worden vergeten.",
        label_visibility="collapsed",
    )

    st.number_input(
        "Half-life (in uren) ",
        min_value=1,
        max_value=100,
        step=1,
        format="%d",
        value=st.session_state["parameters"].ebisu_half_life,
        key="ebisu_half_life_input_key",
        help="De half-life parameter voor Ebisu. "
             "Hoe hoger de waarde, hoe langer het duurt voordat de woorden worden vergeten.",
        label_visibility="collapsed",
    )
