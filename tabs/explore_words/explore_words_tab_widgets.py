
import streamlit as st
from db_operations import (
    get_ids_given_words, load_word_analyses_by_ids, load_thought_scenarios_by_word_id,
    save_thought_scenarios_by_word_id, load_user_images_by_word_id, save_user_images_by_word_id,
)


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


def fetch_thought_scenario_callback():
    """Callback to fetch the thought scenario for the word to explore."""
    word_id = st.session_state.get("word_id_to_explore", 0)
    thought_scenario = load_thought_scenarios_by_word_id(word_id)
    st.session_state["explore_word_thought_scenarios_dict"] = thought_scenario


def fetch_thought_scenario_button():
    """Renders a button to fetch the thought scenario for the word to explore."""
    is_disabled = not st.session_state.get("word_id_to_explore", 0)
    st.button(
        "Haal gedachte scenario op",
        key="fetch_thought_scenario_button_key",
        on_click=fetch_thought_scenario_callback,
        disabled=is_disabled
    )


def save_thought_scenario_callback():
    """Callback to save the thought scenario for the word to explore."""
    thought_scenarios = st.session_state.get(
        "explore_word_thought_scenarios_dict", {})
    for id_ in thought_scenarios:
        thought_scenario = thought_scenarios[id_]
        thought_scenario.title = st.session_state.get(
            f"thought_scenario_title_{id_}", "")
        thought_scenario.situation = st.session_state.get(
            f"thought_scenario_description_{id_}", "")
        thought_scenario.internal_monologue = st.session_state.get(
            f"thought_scenario_content_{id_}", "")
        thought_scenario.expression = st.session_state.get(
            f"thought_scenario_expression_{id_}", "")
    save_thought_scenarios_by_word_id(
        st.session_state["word_id_to_explore"], thought_scenarios
    )


def save_thought_scenario_button():
    """Renders a button to save the thought scenario for the word to explore."""
    is_disabled = not st.session_state.get("word_id_to_explore", 0)
    st.button(
        "Sla gedachte scenario op",
        key="save_thought_scenario_button_key",
        on_click=save_thought_scenario_callback,
        disabled=is_disabled
    )


def display_thought_scenario():
    """Displays the thought scenario for the word to explore."""
    # every key is a id, which is a record in the thought_scenario table
    # put every field of the object in a text area, so that the user can modify it
    thought_scenarios = st.session_state.get(
        "explore_word_thought_scenarios_dict", {})
    for id_ in thought_scenarios:
        thought_scenario = thought_scenarios[id_]
        st.subheader(f"Thought Scenario ID: {id_}")
        st.text_area(
            "title",
            value=thought_scenario.title,
            key=f"thought_scenario_title_{id_}",
        )
        st.text_area(
            "description",
            value=thought_scenario.situation,
            key=f"thought_scenario_description_{id_}",
        )
        st.text_area(
            "content",
            value=thought_scenario.internal_monologue,
            key=f"thought_scenario_content_{id_}",
        )
        st.text_area(
            "expression",
            value=thought_scenario.expression,
            key=f"thought_scenario_expression_{id_}",
        )
        st.divider()

# same for user media


def fetch_user_images_callback():
    """Callback to fetch user images for the word to explore."""
    word_id = st.session_state.get("word_id_to_explore", 0)
    if word_id > 0:
        st.session_state["current_word_user_media_dict"] = load_user_images_by_word_id(
            word_id)
    else:
        print("Ongeldige woord-ID opgegeven.")


def fetch_user_images_button():
    """Renders a button to fetch user images for the word to explore."""
    is_disabled = not st.session_state.get("word_id_to_explore", 0)
    st.button(
        "Haal gebruikersafbeeldingen op",
        key="fetch_user_images_button_key",
        on_click=fetch_user_images_callback,
        disabled=is_disabled
    )


def display_user_media():
    """Displays user media for the word to explore."""
    user_media = st.session_state.get("current_word_user_media_dict", {})
    print(f"{user_media=}")
    user_images = user_media.get("images", [])
    if not user_images:
        st.write("Geen gebruikersafbeeldingen gevonden.")
        return

    user_videos = user_media.get("video", [])

    for idx, image_url in enumerate(user_images):
        st.text_input(
            "Image path",
            value=image_url,
            key=f"user_image_path_{idx}",
        )
        st.image(image_url)
        st.divider()

    for idx, video_url in enumerate(user_videos):
        st.text_input(
            "Video path",
            value=video_url,
            key=f"user_video_path_{idx}",
        )
        st.video(video_url)
        st.divider()


def save_user_media_callback():
    """Callback to save user media for the word to explore."""
    user_media = st.session_state.get("current_word_user_media_dict", {})
    user_images = user_media.get("images", [])
    user_videos = user_media.get("video", [])

    for idx_, image_path in enumerate(user_images):
        images_dict = {
            int(idx_): image_path
        }
        save_user_images_by_word_id(
            st.session_state["word_id_to_explore"],
            images_dict
        )


def save_user_images_button():
    """Renders a button to save user images for the word to explore."""
    is_disabled = not st.session_state.get("word_id_to_explore", 0)
    st.button(
        "Sla gebruikersafbeeldingen op",
        key="save_user_images_button_key",
        on_click=save_user_media_callback,
        disabled=is_disabled
    )
