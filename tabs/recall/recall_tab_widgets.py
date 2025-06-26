
import streamlit as st
from db_operations import load_word_analyses_by_ids, load_n_prompts_for_words
from ebisu_tools import calculate_all_recall_probabilities_from_db
from utils import wrap_around_index
from html_generation import generate_prompt_card_html


def recall_prob_threshold_input():
    """Renders a number input for the recall probability threshold."""

    st.number_input(
        label="Recall Probability Threshold (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=1,
        key="recall_prob_threshold_key",
        help="Stel de drempelwaarde in voor de herinneringskans. "
             "Alleen woorden met een herinneringskans lager dan deze waarde worden weergegeven.",
    )


def recall_number_input():
    """Renders a number input for the number of words to recall."""

    st.number_input(
        label="Aantal te herinneren woorden",
        min_value=1,
        max_value=100,  # arbitrary upper limit
        value=10,  # default value
        step=1,
        key="number_of_words_to_recall_key",
        help="Stel het aantal woorden in dat je wilt herinneren tijdens de sessie.",
    )


def recall_number_of_prompts_input():
    """Renders a number input for the number of prompts per word."""

    st.number_input(
        label="Aantal prompts per woord",
        min_value=1,
        max_value=5,  # arbitrary upper limit
        value=3,  # default value
        step=1,
        key="number_of_prompts_per_word_key",
        help="Stel het aantal prompts in dat je wilt genereren voor elk woord.",
    )


def select_recall_words_callback():
    """Callback function to select words for recall."""

    # estimate the recall probabilities for all words in the database
    st.session_state.recall_probabilities_df = calculate_all_recall_probabilities_from_db()

    # sort by `recall_probability` in ascending order
    st.session_state.recall_probabilities_df.sort_values(
        by="recall_probability", ascending=True, inplace=True
    )

    # print the dataframe
    print("Recall probabilities DataFrame:")
    print(st.session_state.recall_probabilities_df)
    print("Inside select_recall_words_callback")
    print("threshold:", st.session_state.recall_prob_threshold)

    # pick the top N words (ids) based on the recall probability threshold
    recall_prob_threshold = st.session_state["recall_prob_threshold_key"] / 100.0
    print(f"Recall probability threshold: {recall_prob_threshold}")
    selected_ids = st.session_state.recall_probabilities_df[
        st.session_state.recall_probabilities_df["recall_probability"] <= recall_prob_threshold
    ].head(
        st.session_state["number_of_words_to_recall_key"]
    )["word_id"].tolist()

    st.session_state.word_ids_to_recall_list = selected_ids

    # load the word analyses for the selected ids
    st.session_state.word_analyses_to_recall_list = load_word_analyses_by_ids(
        selected_ids
    )

    # load prompts
    st.session_state.prompts_to_recall_dict = load_n_prompts_for_words(
        st.session_state.word_ids_to_recall_list,
        st.session_state["number_of_prompts_per_word_key"]
    )
    print("Prompts to recall:")
    print(st.session_state.prompts_to_recall_dict)


def select_recall_words_button():
    """Renders a button to select words for recall."""

    st.button(
        "Selecteer woorden om te herinneren",
        key="select_recall_words_button_key",
        on_click=select_recall_words_callback,
        help="Selecteer woorden om te herinneren. "
             "Als er nog geen woorden zijn geselecteerd, "
             "worden de woorden met id 1 geselecteerd.",
        use_container_width=True,
        icon=":material/precision_manufacturing:",  # icon size
    )


def start_recall_session_callback():
    """Callback function to start the recall session."""
    st.session_state.start_recall_session = True


def start_recall_session_button():
    """Renders a button to start the recall session."""

    is_disabled = (
        st.session_state.start_recall_session or
        not st.session_state.word_analyses_to_recall_list
    )
    st.button(
        "Start Herinneringsessie",
        key="start_recall_session_button_key",
        on_click=start_recall_session_callback,
        disabled=is_disabled,
        help="Start de herinneringsessie. "
             "Als er nog geen woorden zijn geselecteerd, "
             "wordt de herinneringsessie niet gestart.",
        use_container_width=True,
        icon=":material/play_circle:",  # icon size
    )


def end_recall_session_callback():
    """Callback function to end the recall session."""
    st.session_state.start_recall_session = False

    # empty the list of word analyses to recall
    st.session_state.word_analyses_to_recall_list.clear()


def end_recall_session_button():
    """Renders a button to end the recall session."""

    is_disabled = not st.session_state.start_recall_session
    st.button(
        "Eindig Herinneringsessie",
        key="end_recall_session_button_key",
        on_click=end_recall_session_callback,
        disabled=is_disabled,
        help="Eindig de herinneringsessie.",
        use_container_width=True,
        icon=":material/stop_circle:",  # icon size
    )


def next_prev_callback(direction: int):
    """
    Callback to navigate to the next or previous word in the learning session.

    Parameters
    ----------
    direction : int
        The direction to navigate: -1 for previous, 1 for next.
    """
    current_idx = st.session_state["current_recall_word_idx"]
    new_idx = wrap_around_index(current_idx, direction, len(
        st.session_state["word_analyses_to_recall_list"]))
    st.session_state["current_recall_word_idx"] = new_idx


def next_word_button():
    """
    Renders a button to go to the next word in the learning session.
    This function creates a button that, when clicked, will increment the current word index
    and update the session state accordingly.
    """
    is_disabled = not st.session_state.get("start_recall_session", False)
    st.button(
        "Volgend woord",
        key="next_word_button_recall_key",
        on_click=lambda: next_prev_callback(1),
        disabled=is_disabled,
        use_container_width=True,
        icon=":material/arrow_forward:"
    )


def previous_word_button():
    """
    Renders a button to go to the previous word in the learning session.
    This function creates a button that, when clicked, will decrement the current word index
    and update the session state accordingly.
    """
    is_disabled = not st.session_state.get("start_recall_session", False)
    st.button(
        "Vorige woord",
        key="previous_word_button_recall_key",
        on_click=lambda: next_prev_callback(-1),
        disabled=is_disabled,
        use_container_width=True,
        icon=":material/arrow_back:"
    )


def display_widgets_recall_tab():
    """Displays the widgets for the recall tab."""
    select_recall_words_button()
    with st.expander("Herinneringsinstellingen", expanded=True):
        recall_prob_threshold_input()
        recall_number_input()
        recall_number_of_prompts_input()
    st.divider()
    start_recall_session_button()
    end_recall_session_button()
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        previous_word_button()
    with col2:
        next_word_button()
    st.divider()


def present_prompts_for_recall():
    """Displays the prompts for the current recall session."""
    if st.session_state.start_recall_session:
        if st.session_state.prompts_to_recall_dict:
            word_id = st.session_state.word_ids_to_recall_list[
                st.session_state.current_recall_word_idx
            ]

            prompts = st.session_state.prompts_to_recall_dict[word_id]
            for idx, prompt in enumerate(prompts):
                st.markdown(
                    generate_prompt_card_html(prompt, int(5 - idx)),
                    unsafe_allow_html=True
                )
                st.html("<br>" * 2)
        else:
            print("Er zijn geen herinneringsprompts beschikbaar. "
                  "Selecteer woorden om te herinneren en start de sessie.")
