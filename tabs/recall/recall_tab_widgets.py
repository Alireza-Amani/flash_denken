'''This module contains the widgets for the recall tab in the Streamlit app.'''
from PIL import Image
import streamlit as st
from db_operations import (
    load_word_analyses_by_ids, load_n_prompts_for_words,
    load_user_media,
)
from ebisu_tools import calculate_all_recall_probabilities_from_db, update_ebisu_parameters_in_db
from utils import wrap_around_index, categorize_content
from html_generation import generate_prompt_card_html, embed_video, generate_word_html_design


def recall_prob_threshold_input():
    """Renders a number input for the recall probability threshold."""

    st.number_input(
        label="Recall Probability Threshold (%)",
        min_value=0,
        max_value=100,
        value=60,
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
    calculate_all_recall_probabilities_from_db()

    # sort by `recall_probability` in ascending order
    st.session_state.recall_probabilities_df.sort_values(
        by="recall_probability", ascending=True, inplace=True
    )

    # print the dataframe
    print("Recall probabilities DataFrame:")
    print(st.session_state.recall_probabilities_df)

    # pick the top N words (ids) based on the recall probability threshold
    recall_prob_threshold = st.session_state["recall_prob_threshold_key"] / 100.0
    selected_ids = st.session_state.recall_probabilities_df[
        st.session_state.recall_probabilities_df["recall_probability"] <= recall_prob_threshold
    ].head(
        st.session_state["number_of_words_to_recall_key"]
    )["word_id"].tolist()

    print(f"Selected word IDs for recall: {selected_ids}")

    st.session_state.word_ids_to_recall_list = selected_ids

    # lets populate `recall_words_ebisu_dict` key -> id, values -> ebisu parameters + result
    st.session_state.recall_words_ebisu_dict = {
        word_id: {
            "ebisu_alpha": row["ebisu_alpha"],
            "ebisu_beta": row["ebisu_beta"],
            "ebisu_halflife": row["ebisu_halflife"],
            "time_elapsed_hours": row["time_elapsed_hours"],

            "result": None,  # 0 or 1
            "new_ebisu_alpha": None,
            "new_ebisu_beta": None,
            "new_ebisu_halflife": None,
        }
        for word_id, row in st.session_state.recall_probabilities_df.set_index("word_id").iterrows()
    }

    # load prompts
    st.session_state.prompts_to_recall_dict = load_n_prompts_for_words(
        st.session_state.word_ids_to_recall_list,
        st.session_state["number_of_prompts_per_word_key"]
    )


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
        not len(st.session_state.word_ids_to_recall_list) > 0
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
    st.session_state.word_ids_to_recall_list.clear()

    # set the current recall word index to 0
    st.session_state.current_recall_word_idx = 0

    # empty the prompts to recall dict
    st.session_state.prompts_to_recall_dict.clear()

    # empty the recall words ebisu dict
    st.session_state.recall_words_ebisu_dict.clear()

    # clear the current recall word media dict
    st.session_state.current_recall_word_media_dict.clear()


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
        st.session_state["word_ids_to_recall_list"]))
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


def get_user_media(word_id: int):
    """
    Retrieves user-uploaded media for a given word ID.

    Parameters
    ----------
    word_id : int
        The ID of the word for which to retrieve user media.

    Returns
    -------
    list
        A list of user-uploaded media items.
    """
    try:
        user_media = load_user_media(word_id)
        categorized_media = categorize_content(user_media)
        st.session_state["current_recall_word_media_dict"] = categorized_media
        print(f"User media loaded for word ID {word_id}: {categorized_media}")
    except Exception as e:
        print(f"Error loading user media: {e}")


def display_user_images():
    """Displays user-uploaded images."""

    # display images
    user_media = st.session_state.get("current_recall_word_media_dict", {})

    if user_media.get("images"):
        st.subheader("Afbeeldingen")
        for image in user_media["images"]:
            # open the image
            image = Image.open(image)
            # display the image
            st.image(image, use_container_width=True)


def display_user_videos():
    """Displays user-uploaded videos."""
    user_media = st.session_state.get("current_recall_word_media_dict", {})

    if user_media.get("video"):
        st.subheader("Video's")
        for video in user_media["video"]:
            # embed the video
            st.markdown(embed_video(video), unsafe_allow_html=True)


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

    if st.session_state.prompts_to_recall_dict:
        word_id = st.session_state.word_ids_to_recall_list[
            st.session_state.current_recall_word_idx
        ]
        get_user_media(word_id)

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


def word_analysis_material():
    """Displays the word analysis material for the current recall word."""
    # display user media first
    with st.expander("Gebruikersmedia", expanded=True):
        display_user_images()
        display_user_videos()

    # display the current word analysis
    with st.expander("Analyse van het woord", expanded=False):
        word_id = st.session_state.word_ids_to_recall_list[
            st.session_state.current_recall_word_idx
        ]
        word_analyses = load_word_analyses_by_ids([word_id])[0]
        st.html(generate_word_html_design(word_analyses))


def remember_buttons_callback(remember: bool):
    """
    Callback function to handle the remember and don't remember buttons.

    Parameters
    ----------
    remember : bool
        If True, the word is remembered; if False, it is not remembered.
    """
    word_id = st.session_state.word_ids_to_recall_list[
        st.session_state.current_recall_word_idx
    ]

    # update the `result` in the Ebisu parameters for the current word
    st.session_state.recall_words_ebisu_dict[word_id]["result"] = 1 if remember else 0

    # update the current word's Ebisu parameters
    update_ebisu_parameters_in_db(word_id)


def remember_buttons():
    """Renders the remember and don't remember buttons."""

    word_id = st.session_state.word_ids_to_recall_list[
        st.session_state.current_recall_word_idx
    ]
    result = st.session_state.recall_words_ebisu_dict[word_id]["result"]
    is_disabled = (
        not st.session_state.get("start_recall_session", False) or
        result is not None  # if the result is already set, disable the buttons
    )
    col1, col2 = st.columns(2)

    with col1:
        st.button(
            "Ik herinner me dit woord niet",
            key="dont_remember_word_button_key",
            on_click=lambda: remember_buttons_callback(False),
            disabled=is_disabled,
            use_container_width=True,
            icon=":material/thumb_down:"
        )
    with col2:
        st.button(
            "Ik herinner me dit woord",
            key="remember_word_button_key",
            on_click=lambda: remember_buttons_callback(True),
            disabled=is_disabled,
            use_container_width=True,
            icon=":material/thumb_up:"
        )
