'''Learning tab widgets for Streamlit app'''
import io
from PIL import Image
import streamlit as st
from db_operations import (
    save_user_thought_scenario, sample_words_to_learn, save_user_media_to_db,
    get_ids_given_words, load_user_media, mark_word_as_learned,
)
from output_models import ThoughtScenario
from utils import (
    wrap_around_index, categorize_content, is_valid_video_url,
    prepare_youtube_url_for_streamlit,
)
from html_generation import embed_video


def next_prev_callback(direction: int):
    """
    Callback to navigate to the next or previous word in the learning session.

    Parameters
    ----------
    direction : int
        The direction to navigate: -1 for previous, 1 for next.
    """
    current_idx = st.session_state["current_word_idx_to_learn"]
    new_idx = wrap_around_index(current_idx, direction, len(
        st.session_state["word_analyses_to_learn_list"]))
    st.session_state["current_word_idx_to_learn"] = new_idx


def next_word_button():
    """
    Renders a button to go to the next word in the learning session.
    This function creates a button that, when clicked, will increment the current word index
    and update the session state accordingly.
    """
    is_disabled = not st.session_state.get("start_learning_session", False)
    st.button(
        "Volgend woord",
        key="next_word_button_key",
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
    is_disabled = not st.session_state.get("start_learning_session", False)
    st.button(
        "Vorige woord",
        key="previous_word_button_key",
        on_click=lambda: next_prev_callback(-1),
        disabled=is_disabled,
        use_container_width=True,
        icon=":material/arrow_back:"
    )


def input_number_of_words_to_learn():
    """
    Renders an input field for the number of words to learn.
    This function creates an input field where the user can specify the number of words they want to learn.
    The input is stored in the session state under the key "number_of_words_to_learn".
    """
    st.session_state["number_of_words_to_learn"] = st.number_input(
        "Aantal woorden om te leren",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
        key="number_of_words_to_learn_input_key"
    )


def sample_words_to_learn_callback():
    """
    Callback to sample words to learn.
    This function samples a specified number of words from the `word_analyses_to_learn_list`
    and updates the session state with the sampled words.
    """
    number_of_words = st.session_state.get("number_of_words_to_learn", 0)
    st.session_state["word_analyses_to_learn_list"] = sample_words_to_learn(
        number_of_words=number_of_words
    )

    st.session_state["word_ids_to_learn_list"] = get_ids_given_words(
        [wa.word for wa in st.session_state["word_analyses_to_learn_list"]]
    )


def sample_words_to_learn_button():
    """
    Renders a button to sample words to learn.
    This function creates a button that, when clicked, will sample words based on the number specified
    in the session state under "number_of_words_to_learn".
    """
    is_disabled = (
        not st.session_state.get("number_of_words_to_learn", 0) or
        st.session_state.get("start_learning_session", False)
    )
    st.button(
        "Sample woorden om te leren",
        key="sample_words_to_learn_button_key",
        on_click=sample_words_to_learn_callback,
        disabled=is_disabled,
        use_container_width=True,
        icon=":material/filter_alt:"
    )


def start_learning_session_callback():
    """
    Callback to start the learning session.
    This function sets the session state variable "start_learning_session" to True,
    indicating that the learning session should begin.
    It also resets the current word index to 0 to start from the first word.
    """
    st.session_state["start_learning_session"] = True
    st.session_state["current_word_idx_to_learn"] = 0


def start_learning_session_button():
    """
    Renders a button to start the learning session.
    This function creates a button that, when clicked, will initiate the learning session
    by sampling words to learn and updating the session state accordingly.
    """
    is_disabled = (
        not st.session_state.get("word_analyses_to_learn_list", None) or
        st.session_state.get("start_learning_session", False)
    )
    st.button(
        "Start leer sessie",
        key="start_learning_session_button_key",
        on_click=start_learning_session_callback,
        disabled=is_disabled,
        use_container_width=True,
        icon=":material/play_circle:"
    )


def end_learning_session_callback():
    """
    Callback to end the learning session.
    This function resets the session state variables related to the learning session,
    effectively ending the current session.
    """
    st.session_state["start_learning_session"] = False
    st.session_state["current_word_idx_to_learn"] = 0
    st.session_state["word_analyses_to_learn_list"] = []

    # save ...


def end_learning_session_button():
    """
    Renders a button to end the learning session.
    This function creates a button that, when clicked, will end the current learning session
    by resetting the relevant session state variables.
    """
    is_disabled = not st.session_state.get("start_learning_session", False)
    st.button(
        "Eindig leer sessie",
        key="end_learning_session_button_key",
        on_click=end_learning_session_callback,
        disabled=is_disabled,
        use_container_width=True,
        icon=":material/stop_circle:"
    )


def user_thought_input_callback(wkey: str, state_variable: str) -> None:
    """
    Callback to update the session state with user input.

    Parameters
    ----------
    wkey : str
        The key for the input field in the session state.
    state_variable : str
        The state variable to update with the input value.
    """
    st.session_state[state_variable] = st.session_state[wkey]


def user_thought_scenario_input():
    """
    Renders input fields for the user thought scenario.
    This function creates input fields for the title, situation, internal monologue,
    and expression of the user's thought scenario. It also sets up callbacks to update
    the session state when the input changes.
    """
    st.text_input(
        "Titel van de gedachtegang", value=st.session_state.get("user_thought_title", ""),
        help="Een korte, beschrijvende titel voor de gedachtegang.",
        key="user_thought_title_input_key",
        on_change=user_thought_input_callback,
        args=("user_thought_title_input_key", "user_thought_title")
    )
    st.text_area(
        "Situatie", value=st.session_state.get("user_thought_situation", ""),
        help="De objectieve feiten van het mini-verhaal.",
        key="user_thought_situation_input_key",
        on_change=user_thought_input_callback,
        args=("user_thought_situation_input_key", "user_thought_situation")
    )
    st.text_area(
        "Interne monoloog", value=st.session_state.get("user_thought_internal_monologue", ""),
        help="De pre-linguistische interne gedachte, oordeel of gevoel van de persoon in het verhaal.",
        key="user_thought_internal_monologue_input_key",
        on_change=user_thought_input_callback,
        args=("user_thought_internal_monologue_input_key",
              "user_thought_internal_monologue")
    )
    st.text_area(
        "Expressie", value=st.session_state.get("user_thought_expression", ""),
        help="De uiteindelijke gearticuleerde zinnen in het Nederlands, waarin het doelwoord op een natuurlijke manier naar voren komt. Het doelwoord moet worden omgeven door **dubbele sterretjes**.",
        key="user_thought_expression_input_key",
        on_change=user_thought_input_callback,
        args=("user_thought_expression_input_key", "user_thought_expression")
    )

# user input cleanup


def user_thought_input_cleanup():
    """Cleans up the user thought input fields by resetting their values."""
    st.session_state["user_thought_title"] = ""
    st.session_state["user_thought_situation"] = ""
    st.session_state["user_thought_internal_monologue"] = ""
    st.session_state["user_thought_expression"] = ""


def save_user_thought_callback():
    """Callback to save the user thought scenario."""
    thought_scenario = ThoughtScenario(
        title=st.session_state["user_thought_title"],
        situation=st.session_state["user_thought_situation"],
        internal_monologue=st.session_state["user_thought_internal_monologue"],
        expression=st.session_state["user_thought_expression"],
    )
    idx = st.session_state.get("current_word_idx_to_learn", 0)
    word_id = st.session_state["word_ids_to_learn_list"][idx]
    save_user_thought_scenario(
        word_id, thought_scenario)
    st.session_state["thought_scenario_created"] = True
    user_thought_input_cleanup()


def save_user_thought_button():
    """Renders a button to save the user thought scenario."""
    is_disabled = not all([
        # st.session_state.get("user_thought_title", ""),
        st.session_state.get("user_thought_situation", ""),
        st.session_state.get("user_thought_internal_monologue", ""),
        st.session_state.get("user_thought_expression", "")
    ])
    st.button(
        "Sla je gedachtegang op",
        key="save_user_thought_button_key",
        on_click=save_user_thought_callback,
        disabled=is_disabled
    )


def mark_word_learned_callback():
    """Callback to mark the current word as learned."""
    word_id_idx = st.session_state.get("current_word_idx_to_learn", 0)
    word_id = st.session_state["word_ids_to_learn_list"][word_id_idx]
    if word_id is not None:
        mark_word_as_learned(word_id)
    st.session_state["current_word_is_learned"] = True


def mark_word_learned_button():
    """Renders a button to mark the current word as learned."""
    is_disabled = (
        not st.session_state.get("start_learning_session", False) or
        st.session_state.get("current_word_is_learned", False)  # or
        # not st.session_state.get("thought_scenario_created", False) or
        # not st.session_state.get("image_added", False) or
        # not st.session_state.get("video_added", False)
    )
    st.button(
        "Markeer woord als geleerd",
        key="mark_word_learned_button_key",
        on_click=mark_word_learned_callback,
        disabled=is_disabled,
        use_container_width=True,
        icon=":material/check_circle:"
    )


def image_uploader_callback(wkey: str):
    """Callback function to handle the uploaded image (on change)"""

    uploaded_image = st.session_state.get(wkey)
    if uploaded_image:
        st.session_state["uploaded_images_list"].extend(uploaded_image)


def image_uploader():
    """
    Renders an image uploader for the word illustration.
    This function creates a file uploader that allows the user to upload an image
    illustrating the word being learned. The uploaded image is stored in the session state.
    """
    st.file_uploader(
        "Upload een afbeelding die het woord illustreert",
        type=["jpg", "jpeg", "png"],
        key="image_uploader_key",
        on_change=image_uploader_callback,
        args=("image_uploader_key",),
        accept_multiple_files=True,
    )


def save_resize_image_callback():
    """Callback function to save and resize the uploaded image."""
    uploaded_images = st.session_state.get("uploaded_images_list", [])
    for idx, uploaded_image in enumerate(uploaded_images):

        # no resizing for now
        # bytes_data = uploaded_image.getvalue()
        # image = Image.open(io.BytesIO(bytes_data))

        image = Image.open(uploaded_image)

        # new_dim = (
        #     int(image.width * st.session_state.get("image_resize_coefficient", 0.8)),
        #     int(image.height * st.session_state.get("image_resize_coefficient", 0.8))
        # )
        # resized_image = image.resize(new_dim, Image.Resampling.LANCZOS)

        # save the image, with its name being the dutch entry
        save_name = (
            st.session_state["word_analysis_to_learn"].word +
            (f"_{idx}" if idx > 0 else "")
        )
        save_path = (
            st.session_state["parameters"].image_dir /
            f"{save_name}.jpg"
        )
        image.save(save_path)

        # save the image to the database
        word_id = st.session_state["word_ids_to_learn_list"][st.session_state["current_word_idx_to_learn"]]
        save_user_media_to_db(
            word_id=word_id,
            content_url=save_path,
            content_type="image",
            description=f"Illustration for {st.session_state['word_analysis_to_learn'].word}"
        )

    st.session_state["image_added"] = True

    # cleanup
    st.session_state["uploaded_images_list"].clear()


def save_resize_image_button():
    """Renders a button to save and resize the uploaded image."""
    is_disabled = not st.session_state.get("uploaded_images_list", [])
    st.button(
        "Sla afbeelding op",
        key="save_resize_image_button_key",
        on_click=save_resize_image_callback,
        disabled=is_disabled,
        use_container_width=True,
        icon=":material/save:"
    )


def video_urls_input_callback(wkey: str):
    """
    Callback function to handle the input of video URLs.

    Parameters
    ----------
    wkey : str
        The key for the input field in the session state.
    """
    st.session_state["video_urls_list"] = st.session_state[wkey].splitlines()

    # only keep the valid ones
    for url_ in st.session_state["video_urls_list"]:
        if not is_valid_video_url(url_):
            print(f"Invalid video URL: {url_}")
            st.session_state["video_urls_list"].remove(url_)

        else:  # if valid, prepare it for Streamlit
            prepared_url = prepare_youtube_url_for_streamlit(url_)
            if prepared_url:
                st.session_state["video_urls_list"][st.session_state["video_urls_list"].index(
                    url_)] = prepared_url


def video_urls_input():
    """
    Renders an input area for video URLs.
    This function creates a text area where the user can paste multiple video URLs,
    each on a new line. The input is stored in the session state under the key "video_urls_list".
    """
    st.text_area(
        "Voeg video URL's toe (één per regel)",
        value="\n".join(st.session_state.get("video_urls_list", [])),
        key="video_urls_input_key",
        on_change=video_urls_input_callback,
        args=("video_urls_input_key",),
        help="Voeg hier de URL's van video's toe die gerelateerd zijn aan het woord."
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
        st.session_state["current_word_user_media_list"] = categorized_media
    except Exception as e:
        print(f"Error loading user media: {e}")


def save_video_urls_callback():
    """Callback function to save video URLs to the database."""
    word_id = st.session_state["word_ids_to_learn_list"][st.session_state["current_word_idx_to_learn"]]
    for video_url in st.session_state.get("video_urls_list", []):
        if is_valid_video_url(video_url):
            save_user_media_to_db(
                word_id=word_id,
                content_url=video_url,
                content_type="video",
                description=f"Video for {st.session_state['word_analysis_to_learn'].word}"
            )

    st.session_state["video_added"] = True

    st.session_state["video_urls_list"] = []  # clear the list after saving


def save_video_urls_button():
    """Renders a button to save video URLs."""
    is_disabled = not st.session_state.get("video_urls_list", [])
    st.button(
        "Sla video URL's op",
        key="save_video_urls_button_key",
        on_click=save_video_urls_callback,
        disabled=is_disabled,
        use_container_width=True,
        icon=":material/save:"
    )


def display_user_images():
    """Displays user-uploaded images."""

    # display images
    user_media = st.session_state.get("current_word_user_media_list", {})

    if user_media.get("images"):
        st.subheader("Afbeeldingen")
        for image in user_media["images"]:
            # open the image
            image = Image.open(image)
            # display the image
            st.image(image, use_container_width=True)


def display_user_videos():
    """Displays user-uploaded videos."""
    user_media = st.session_state.get("current_word_user_media_list", {})

    if user_media.get("video"):
        st.subheader("Video's")
        for video in user_media["video"]:
            # embed the video
            st.markdown(embed_video(video), unsafe_allow_html=True)


# # lets have an expander for personal thought scenario
#         with st.expander("Jouw persoonlijke gedachte scenario", expanded=False):
#             user_thought_scenario_input()
#             save_user_thought_button()
#             st.divider()

#         # another expander for the word image
#         with st.expander("Afbeelding van het woord", expanded=False):
#             image_uploader()
#             save_resize_image_button()

#             if st.session_state.get("uploaded_images_list"):
#                 for uploaded_image in st.session_state["uploaded_images_list"]:
#                     image = Image.open(uploaded_image)
#                     st.image(image, caption="Uploaded Image",
#                              use_container_width=True)

#         # another expander to provide url to a video
#         with st.expander("Video URL", expanded=False):
#             video_urls_input()
#             save_video_urls_button()

#             if st.session_state.get("video_urls_list"):
#                 for video_url in st.session_state["video_urls_list"]:
#                     st.markdown(embed_video(video_url), unsafe_allow_html=True)

# widgets for personalization
def user_personalization_widgets():
    """
    Renders widgets for user personalization.
    This function creates input fields and buttons for the user to personalize their learning experience.
    """

    with st.expander("Jouw persoonlijke gedachte scenario", expanded=False):
        user_thought_scenario_input()
        save_user_thought_button()
        st.divider()

    with st.expander("Afbeelding van het woord", expanded=False):
        image_uploader()
        save_resize_image_button()

        if st.session_state.get("uploaded_images_list"):
            for uploaded_image in st.session_state["uploaded_images_list"]:
                image = Image.open(uploaded_image)
                st.image(image, caption="Uploaded Image",
                         use_container_width=True)

    with st.expander("Video URL", expanded=False):
        video_urls_input()
        save_video_urls_button()

        if st.session_state.get("video_urls_list"):
            for video_url in st.session_state["video_urls_list"]:
                st.markdown(embed_video(video_url), unsafe_allow_html=True)
