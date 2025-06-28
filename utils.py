'''utility functions'''

from typing import List, Dict, Any, Generator, Optional
import ast
import re
import json
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import requests
from requests.exceptions import RequestException


def get_unique_new_words(already_there: List[str], new_addition: List[str]) -> List[str]:
    """
    Compares two lists of words and returns a list of unique words
    from 'new_addition' that are not present in 'already_there'.

    Parameters
    ----------
    already_there : List[str]
        A list of words that are already known or present.
    new_addition : List[str]
        A list of words that are being added, which may contain duplicates.

    Returns
    -------
    List[str]
        A sorted list of unique words from 'new_addition' that are not in 'already_there'.
    """

    # Convert lists to sets for efficient comparison.
    # Sets are great for unique items and fast lookups (checking if an item exists).
    # We also convert words to lowercase to ensure case-insensitive comparison.
    # 'Huis' and 'huis' should be treated as the same word.
    known_words = set(word.lower() for word in already_there)
    incoming_words = set(word.lower() for word in new_addition)

    # Find the difference: words in incoming_words that are not in known_words.
    # The '-' operator for sets gives us exactly this.
    truly_new_words = incoming_words - known_words

    # Convert the set back to a list (optional, but often more convenient for output).
    # We can also sort them to get a consistent order, which can be nice for review.
    return sorted(list(truly_new_words))


# return a list of words, that are separated by commas or new lines
def parse_words_input(input_string: str) -> List[str]:
    """
    Parses a string of words separated by commas or new lines into a list of words.

    Parameters
    ----------
    input_string : str
        The input string containing words separated by commas or new lines.

    Returns
    -------
    List[str]
        A list of words extracted from the input string.
    """
    # Split the input string by commas and new lines, then strip whitespace.
    return [word.strip() for word in re.split(r'[,\n]', input_string) if word.strip()]


def assert_model_presence(
    client: 'genai.Client',
    expected_model_name: str,
    raise_exception: bool = True
) -> bool:
    """
    Asserts the presence of a specific model name within the list of models
    available via the Google Generative AI client.

    Parameters
    ----------
    client (genai.Client)
        An instance of the Google Generative AI client to interact with the API.
    expected_model_name (str)
        The name of the model to check for presence.
    raise_exception (bool)
        If True, raises an AssertionError if the model is not found.
        If False, prints an error message and returns False.

    Returns
    -------
    bool
        True if the model is present, False otherwise.
        If `raise_exception` is True and the model is not found, an AssertionError is raised.

    Raises
    ------
    AssertionError
        If `raise_exception` is True and the model is not found.
    Exception
        For any other unexpected errors during the API call.
    """
    try:
        # Get all available model names from the client
        # only get the part after `models/` in the model name
        available_model_names = [
            re.sub(r'^models/', '', str(model.name)) for model in client.models.list()]

        # Check if the expected_model_name is in the list
        if expected_model_name in available_model_names:
            print(f"Success: Model '{expected_model_name}' is present.")
            return True
        else:
            message = (
                f"Error: Model '{expected_model_name}' not found. "
                f"Available models: {available_model_names}"
            )
            if raise_exception:
                raise AssertionError(message)
            else:
                print(message)
                return False

    except Exception as e:
        # Catch any other unexpected errors (network, permissions, etc.)
        print(f"An unexpected error occurred while listing models: {e}")
        if raise_exception:
            raise
        return False


# NOTE: probably dont need this, one can use `json.dumps` directly
def serialize_comparisons_dict_to_string(comparisons_dict: Dict[str, str]) -> str:
    """
    Serializes a dictionary of comparisons back into the specific string format
    expected by the LLM generation: "key1: value1.key2: value2."

    Parameters
    ----------
    comparisons_dict : Dict[str, str]
        A dictionary where keys are comparison terms and values are their explanations.

    Returns
    -------
    str
        A string formatted as "key1: value1.key2: value2." with each value ending with a period.
        Returns an empty string if the input dictionary is empty.
    """
    if not comparisons_dict:
        return ""

    parts = []
    for key, value in comparisons_dict.items():
        # Ensure key and value are stripped of leading/trailing whitespace
        cleaned_key = key.strip()
        cleaned_value = value.strip()

        # Add a period if the value doesn't already end with one,
        # or if it's not a period already there. This mimics the LLM's output.
        if not cleaned_value.endswith('.'):
            cleaned_value += '.'

        parts.append(f"{cleaned_key}: {cleaned_value}")

    # Join all parts. No separator needed between parts as the period from the value acts as one.
    # The regex in your parser expects "key: value.key: value."
    # So we simply concatenate them.
    return "".join(parts)


def parse_comparisons_string_to_dict(comparisons_string: str) -> Dict[str, str]:
    """
    Intelligently parses a comparison string from the LLM into a dictionary.

    The expected format is: "key1: value1.key2: value2." where values
    can contain periods, but keys are followed by a colon.

    Parameters
    ----------
    comparisons_string : str
        A string containing comparisons in the format "key1: value1.key2: value2."

    Returns
    -------
    Dict[str, str]
        A dictionary where keys are the comparison terms and values are their explanations.
        Returns an empty dictionary if the input string is empty or not a string.
    """
    if not comparisons_string:  # or not isinstance(comparisons_string, str):
        return {}

    # first try simple json parsing
    try:
        parsed_dict = json.loads(comparisons_string)
        if isinstance(parsed_dict, dict):
            # Ensure all keys and values are strings, as expected by your original function's return type
            print("successfully parsed stringified dictionary using json.loads")
            return {str(k): str(v) for k, v in parsed_dict.items()}
        else:
            print(
                f"Warning: Input string evaluated to a {type(parsed_dict)}, not a dictionary.")

    except Exception as e:
        print("inside parse_comparisons_string_to_dict")
        print(f"Error parsing stringified dictionary: {e}")

    parsed_dict = {}
    # Pattern: Captures a group of word characters (the key), followed by a colon,
    # then captures everything else (the value) non-greedily, until it hits another
    # word character sequence followed by a colon, OR the end of the string.
    pattern = re.compile(r'([\w\s]+?):\s*(.+?)(?=[\w\s]+?:|\Z)', re.DOTALL)

    matches = pattern.findall(comparisons_string.strip())

    for key, value in matches:
        cleaned_key = key.strip()
        cleaned_value = value.strip()

        if cleaned_value.endswith('.'):
            cleaned_value = cleaned_value[:-1].strip()

        if cleaned_key:
            parsed_dict[cleaned_key] = cleaned_value

    return parsed_dict


def parse_stringified_dict(s: str) -> Dict[str, str]:
    """
    Parses a string that represents a Python dictionary literal into an actual dictionary.

    Parameters
    ----------
    s : str
        A string containing a Python dictionary literal (e.g., "{'key': 'value'}").

    Returns
    -------
    Dict[str, str]
        An actual Python dictionary. Returns an empty dictionary if parsing fails
        or if the input is not a string.
    """
    if not isinstance(s, str) or not s.strip():
        return {}
    try:
        # ast.literal_eval safely evaluates a string containing a Python literal
        parsed_data = ast.literal_eval(s)
        if isinstance(parsed_data, dict):
            # Ensure all keys and values are strings, as expected by your original function's return type
            return {str(k): str(v) for k, v in parsed_data.items()}
        else:
            # If it's not a dictionary (e.g., "[1, 2, 3]"), return empty or raise an error
            print(
                f"Warning: Input string evaluated to a {type(parsed_data)}, not a dictionary.")
            return {}
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing stringified dictionary: {e}")
        return {}


def chunk_list(input_list: List[Any], chunk_size: int) -> Generator[List[Any], None, None]:
    """
    Chunks a list into smaller lists of a specified size using a generator.

    This function is designed for memory efficiency, especially with very
    large input lists, as it yields one chunk at a time instead of creating
    all chunks in memory at once.

    Parameters
    ----------
    input_list : List[Any]
        The list to be chunked.
    chunk_size : int
        The size of each chunk. Must be a positive integer.

    Yields
    ------
    List[Any]
        A chunk of the input list of size `chunk_size`. The last chunk may be smaller if the total
        number of elements is not divisible by `chunk_size`.

    Raises
    ------
    ValueError
        If `chunk_size` is not a positive integer.
    """
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")

    # Iterate through the list, stepping by chunk_size
    for i in range(0, len(input_list), chunk_size):
        # Slice the list to get the current chunk
        # This handles the last chunk gracefully, even if it's smaller than chunk_size
        yield input_list[i:i + chunk_size]


def wrap_around_index(current_index: int, increment: int, length: int) -> int:
    """
    Increments or decrements an index with wrap-around behavior.

    Parameters
    ----------
    current_index : int
        The current index to be modified.
    increment : int
        The amount to increment (positive) or decrement (negative) the index.
    length : int
        The length of the list or the maximum index value.

    Returns
    -------
    int
        The new index after applying the increment, wrapped around if necessary.
    """
    new_index = (current_index + increment) % length
    return new_index


def categorize_content(content_list: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Categorizes a list of content dictionaries into separate lists for images, audio, and video.

    Args:
        content_list (list): A list of dictionaries, where each dictionary
                             is expected to have 'content_type' and 'content_url' keys.
                             'content_type' can only be "image", "audio", or "video".

    Returns:
        dict: A dictionary with three keys: 'images', 'audio', and 'video'.
              Each key's value is a list of content URLs belonging to that type.
              Returns empty lists for content types not found or if input is invalid.
    """
    categorized_data = {
        "images": [],
        "audio": [],
        "video": []
    }

    if not isinstance(content_list, list):
        print("Warning: Input is not a list. Returning empty categorized data.")
        return categorized_data

    for item in content_list:
        if not isinstance(item, dict):
            print(
                f"Warning: Found non-dictionary item in content_list: {item}. Skipping.")
            continue

        content_type = item.get("content_type")
        content_url = item.get("content_url")

        if content_type is None or content_url is None:
            print(
                f"Warning: Item missing 'content_type' or 'content_url' key: {item}. Skipping.")
            continue

        # Convert to lowercase to handle potential case variations (e.g., "Image" vs "image")
        content_type = content_type.lower()

        if content_type == "image":
            categorized_data["images"].append(content_url)
        elif content_type == "audio":
            categorized_data["audio"].append(content_url)
        elif content_type == "video":
            categorized_data["video"].append(content_url)
        else:
            print(
                f"Warning: Unknown content_type '{content_type}' for URL '{content_url}'. Skipping.")

    return categorized_data


def is_valid_video_url(url: str, check_content_type: bool = False) -> bool:
    """
    Checks if a given URL is a syntactically valid URL and potentially points to a common video file
    or a known video streaming service.

    This function performs a basic validation of the URL's structure, its file
    extension, or its domain for popular video streaming services. Optionally,
    it can make an HTTP HEAD request to check if the server responds and reports
    a video content type for direct file links.

    Parameters
    ----------
    url : str
        The URL string to validate.
    check_content_type : bool, optional
        If True, and the URL is not from a recognized video streaming service,
        the function will attempt to make an HTTP HEAD request to the URL
        to verify if the server reports a 'video/' content type. This requires
        the 'requests' library and can be slower. Default is False.

    Returns
    -------
    bool
        True if the URL is considered valid (syntactically and by extension
        or known domain, and optionally by content type for direct links),
        False otherwise.

    Notes
    -----
    This function relies on common video file extensions and a predefined list
    of popular video streaming domains. For direct video file links, it can
    optionally use the 'Content-Type' header from an HTTP HEAD request. It does not
    guarantee that the content at the URL is definitively a playable video,
    as server configurations or malformed files can exist.

    Examples
    --------
    >>> is_valid_video_url("https://example.com/video.mp4")
    True
    >>> is_valid_video_url("http://cdn.videos.net/clip.avi")
    True
    >>> is_valid_video_url("https://www.youtube.com/watch?v=Ql7tmIVaK30")
    True
    >>> is_valid_video_url("invalid-url")
    False
    >>> is_valid_video_url("https://example.com/document.pdf")
    False
    >>> is_valid_video_url("https://example.com/video.mp4", check_content_type=True) # Assuming URL is reachable and serves video
    True # (Actual result depends on server response)
    """
    if not isinstance(url, str):
        print(f"Warning: URL input must be a string, got {type(url)}.")
        return False

    # 1. Basic URL parsing for scheme and netloc
    parsed_url = urlparse(url)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        return False

    # Check for valid schemes
    if parsed_url.scheme not in ['http', 'https']:
        return False

    # Normalize netloc for comparison (remove 'www.' and get base domain)
    netloc = parsed_url.netloc.lower()
    if netloc.startswith('www.'):
        netloc = netloc[4:]

    # 2. Check common video file extensions
    # This is a heuristic and can be expanded.
    video_extensions = [
        '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.ogg', '.ogv', '.3gp'
    ]
    path = parsed_url.path.lower()
    is_direct_video_file = any(path.endswith(ext) for ext in video_extensions)

    # 3. Check for popular video streaming service domains
    popular_video_domains = [
        'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com', 'twitch.tv',
        'facebook.com', 'instagram.com', 'tiktok.com'  # These can host videos
    ]
    is_popular_video_domain = any(
        domain in netloc for domain in popular_video_domains)

    # If it's a popular video domain, we consider it a valid video URL based on domain alone.
    if is_popular_video_domain:
        return True

    # If it's not a popular video domain, proceed to check for direct video file extension.
    if not is_direct_video_file:
        return False  # Neither a popular domain nor a direct video file extension

    # 4. Optional: HTTP HEAD request to check content type (only for direct video files,
    # as streaming service content types are often 'text/html' for the page itself)
    if check_content_type and is_direct_video_file:
        try:
            # Use a timeout to prevent the function from hanging indefinitely
            response = requests.head(url, allow_redirects=True, timeout=5)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            content_type = response.headers.get('Content-Type', '').lower()
            # Check if the content type indicates a video.
            # Some servers might send "application/octet-stream" or similar for videos
            # so this check might not be exhaustive, but 'video/' is a good start.
            if not content_type.startswith('video/'):
                print(
                    f"Debug: URL '{url}' has extension but Content-Type is '{content_type}'.")
                return False

        except RequestException as e:
            print(f"Debug: Could not verify URL '{url}' via HEAD request: {e}")
            return False
        except Exception as e:
            # Catch other potential errors during request
            print(
                f"Debug: An unexpected error occurred during HEAD request for '{url}': {e}")
            return False

    return True


def _parse_time_string(time_str: str) -> int:
    """
    Helper function to parse time strings like '1h2m3s', '90s', '1m30s' into total seconds.

    Parameters
    ----------
    time_str : str
        The time string to parse.

    Returns
    -------
    int
        The total number of seconds represented by the time string.
    """
    total_seconds = 0
    parts = re.findall(r'(\d+)([hms]?)', time_str)

    for value, unit in parts:
        value = int(value)
        if unit == 'h':
            total_seconds += value * 3600
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 's' or not unit:  # If no unit, assume seconds
            total_seconds += value
    return total_seconds


def get_youtube_start_time(url: str) -> int:
    """
    Recognizes and extracts the starting second from a YouTube video URL.
    (See docstring in 'get_youtube_start_time_util' immersive for full details)
    """
    if not isinstance(url, str):
        # In a combined utility, we might raise an error or return 0,
        # but for this specific context, we'll return 0 as per previous design.
        return 0

    parsed_url = urlparse(url)

    # Check query parameters first (e.g., ?t= or ?start=)
    query_params = parse_qs(parsed_url.query)
    if 't' in query_params:
        time_str = query_params['t'][0]
        return _parse_time_string(time_str)
    if 'start' in query_params:
        try:
            return int(query_params['start'][0])
        except ValueError:
            pass  # Fall through if 'start' parameter is not a valid integer

    # Check fragment identifier (e.g., #t=)
    if parsed_url.fragment.startswith('t='):
        time_str = parsed_url.fragment[2:]
        return _parse_time_string(time_str)

    # If no start time parameter is found, return 0
    return 0


def prepare_youtube_url_for_streamlit(original_url: str, desired_start_seconds: Optional[int] = None) -> str:
    """
    Prepares a YouTube video URL for use with Streamlit's st.video(),
    ensuring correct embed format and applying a specified or extracted start time.

    This function takes a YouTube URL, extracts its video ID, and converts it
    to the 'embed' format (e.g., https://www.youtube.com/embed/VIDEO_ID).
    It then applies a `start` parameter:
    - If `desired_start_seconds` is provided (not None), that value is used.
    - If `desired_start_seconds` is None, the function attempts to automatically
      extract a start time from the `original_url` (e.g., from `&t=90s` or `?start=15`).
    - If no start time is found or provided, the video will start from 0 seconds.
    Unnecessary tracking parameters like 'si' are removed for cleaner URLs.

    Parameters
    ----------
    original_url : str
        The original YouTube video URL (e.g., 'https://www.youtube.com/watch?v=VIDEO_ID',
        'https://youtu.be/SHORT_ID', or 'https://www.youtube.com/embed/VIDEO_ID').
    desired_start_seconds : int, optional
        The specific start time in seconds you want the video to begin at.
        If None (default), the function will attempt to detect a start time
        from the `original_url`. If detected, that time is used; otherwise,
        it defaults to 0 seconds.

    Returns
    -------
    str
        The formatted YouTube URL ready for Streamlit's st.video().

    Raises
    ------
    ValueError
        If the video ID cannot be extracted from the provided URL.

    Examples
    --------
    >>> prepare_youtube_url_for_streamlit("https://www.youtube.com/watch?v=Ql7tmIVaK30", 120)
    'https://www.youtube.com/embed/Ql7tmIVaK30?start=120'

    >>> prepare_youtube_url_for_streamlit("https://www.youtube.com/watch?v=jQha6__qOw4?si=a-eZ9wATeLmX6hWs&t=15s")
    'https://www.youtube.com/embed/jQha6__qOw4?start=15'

    >>> prepare_youtube_url_for_streamlit("https://youtu.be/another_video", 0)
    'https://www.youtube.com/embed/another_video?start=0'

    >>> prepare_youtube_url_for_streamlit("https://www.youtube.com/embed/existing_embed_url", 30)
    'https://www.youtube.com/embed/existing_embed_url?start=30'

    >>> prepare_youtube_url_for_streamlit("https://www.youtube.com/watch?v=video_without_start_param")
    'https://www.youtube.com/embed/video_without_start_param?start=0'
    """
    if not isinstance(original_url, str) or not original_url:
        raise ValueError("Original URL must be a non-empty string.")

    parsed_url = urlparse(original_url)
    query_params = parse_qs(parsed_url.query)

    video_id = None
    if 'v' in query_params:
        video_id = query_params['v'][0]
    elif parsed_url.path.startswith('/embed/'):
        path_segments = [s for s in parsed_url.path.split('/') if s]
        if len(path_segments) >= 2 and path_segments[0] == 'embed':
            video_id = path_segments[1]
    elif parsed_url.netloc == 'youtu.be' and parsed_url.path:
        video_id = parsed_url.path.lstrip('/')

    # for shorts
    elif parsed_url.netloc == 'www.youtube.com' and 'shorts' in parsed_url.path:
        path_segments = [s for s in parsed_url.path.split('/') if s]
        if len(path_segments) >= 2 and path_segments[0] == 'shorts':
            video_id = path_segments[1]

    if not video_id:
        print(f"Error: Could not extract video ID from URL: {original_url}")
        return ''

    # Determine the effective start time
    effective_start_seconds = 0
    if desired_start_seconds is not None:
        if not isinstance(desired_start_seconds, int) or desired_start_seconds < 0:
            raise ValueError(
                "Desired start seconds must be a non-negative integer or None.")
        effective_start_seconds = desired_start_seconds
    else:
        # If no desired_start_seconds, try to extract from the original URL
        effective_start_seconds = get_youtube_start_time(original_url)

    # Always use the 'embed' path for consistency
    new_path = f'/embed/{video_id}'

    # Prepare query parameters for the new URL
    # Start with a fresh dictionary for query params to avoid carrying over unwanted ones
    # but selectively keep 'autoplay', 'controls', etc. if they are needed and valid
    new_query_params = {}

    # Copy over some common embed-relevant parameters if they exist in the original URL
    for param in ['autoplay', 'controls', 'loop', 'modestbranding', 'rel', 'playsinline']:
        if param in query_params:
            new_query_params[param] = query_params[param][0]

    # Add the start parameter
    new_query_params['start'] = str(effective_start_seconds)

    # Reconstruct the query string
    new_query = urlencode(new_query_params, doseq=True)

    # Reconstruct the URL with the new path and query
    new_netloc = 'www.youtube.com'
    new_scheme = 'https'  # Ensure HTTPS

    reconstructed_url = urlunparse(
        (new_scheme, new_netloc, new_path, '', new_query, ''))
    return reconstructed_url
