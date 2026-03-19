
import re
import html
from typing import List, Optional, Callable
from .output_models import (
    WordAnalysis, CoreMeaning, ContextualInfo, RelationalWeb, Physicality,
    ThoughtScenario, EnkelePrompt
)


def _generate_css() -> str:
    """Generates the main CSS styles for the HTML page, infused with a subtle Dutch touch and playful, soul-pleasing aesthetics."""
    return """
        :root {
            /* Revised Color Palette: Softer, more inviting, a bit more Dutch landscape-inspired */
            --primary-text-color: #2C3E50; /* Darker blue-grey for main text - professional yet warm */
            --secondary-text-color: #7F8C8D; /* Muted grey for supporting info - soft, earthy */
            --background-color-light: #FBFBFB; /* Very light, almost off-white for body background - airy, clean */
            --background-color-card: #FFFFFF; /* Pure white for main content cards - crisp contrast */
            --accent-color: #007bff; /* A slightly brighter, more vibrant Dutch blue, symbolizing clarity & opportunity */
            --secondary-accent-color: #FF7F50; /* Coral/soft orange - a playful, warm complementary color */
            --border-color: #E0E0E0; /* Lighter, softer border */
            --card-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); /* Slightly more prominent but still soft shadow */
            --highlight-bg-color: #F8F9FA; /* A very subtle light grey for element backgrounds, gentle */
        }

        body {
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif; /* Using 'Inter' (or fallback), a modern, friendly sans-serif */
            line-height: 1.8; /* Increased line-height for more breathing room */
            color: var(--primary-text-color);
            background-color: var(--background-color-light);
            /* Add a subtle background texture for depth and playfulness */
            background-image: url("data:image/svg+xml,%3Csvg width='6' height='6' viewBox='0 0 6 6' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23e9e9e9' fill-opacity='0.15' fill-rule='evenodd'%3E%3Cpath d='M5 0h1L0 6V5zm1 6v-1L1 0h1z'/%3E%3C/g%3E%3C/svg%3E"); /* Very subtle diagonal lines */
            margin: 0;
            padding: 60px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }

        .word-container {
            background-color: var(--background-color-card);
            border-radius: 20px; /* Even softer rounded corners */
            box-shadow: var(--card-shadow);
            padding: 60px 70px;
            max-width: 950px;
            width: 100%;
            box-sizing: border-box;
            position: relative; /* For potential future animations */
            overflow: hidden; /* Ensures shadows/transforms are clipped */
        }

        h1 {
            font-family: 'Outfit', sans-serif; /* A clear, modern, slightly more geometric font for impact */
            color: var(--accent-color); /* H1 using accent color for vibrancy */
            font-size: 3.8em; /* Slightly larger, more dominant */
            font-weight: 700;
            margin-bottom: 5px; /* Less margin, bringing POS closer */
            display: inline-block;
            vertical-align: bottom;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.05); /* Subtle text shadow for depth */
        }

        .part-of-speech {
            font-size: 1.6em; /* A bit larger to match the H1 scale */
            color: var(--secondary-text-color);
            font-style: normal;
            font-weight: 400;
            margin-left: 20px; /* Slightly more distinct separation */
            display: inline-block;
            vertical-align: bottom;
        }

        h2 {
            font-family: 'Outfit', sans-serif; /* Consistent header font */
            color: var(--primary-text-color);
            font-size: 2.5em; /* Larger, clearer section headers */
            font-weight: 600;
            border-bottom: 2px solid var(--border-color); /* Slightly thicker, more defined border */
            padding-bottom: 15px; /* More padding */
            margin-top: 50px; /* More vertical space */
            margin-bottom: 35px; /* More vertical space */
            position: relative;
        }
        h2::after { /* A subtle, playful accent under the h2 */
            content: '';
            display: block;
            width: 50px; /* A short accent line */
            height: 4px;
            background-color: var(--secondary-accent-color); /* Using the new accent color */
            position: absolute;
            bottom: -2px; /* Position it slightly overlapping the border */
            left: 0;
            border-radius: 2px;
        }


        h3 {
            font-family: 'Outfit', sans-serif; /* Consistent header font */
            color: var(--primary-text-color);
            font-size: 2em; /* Clearer sub-headings, bolder */
            font-weight: 600;
            margin-top: 40px; /* More space */
            margin-bottom: 20px; /* More space */
        }

        p {
            margin-bottom: 1.5em; /* More space between paragraphs */
            color: var(--primary-text-color); /* Ensure paragraph text color is consistent */
        }

        ul {
            list-style: none;
            padding: 0;
            margin-bottom: 2em; /* More margin */
        }

        li {
            margin-bottom: 1.2em; /* More space between list items */
            padding-left: 2em; /* Ample space for bullet */
            position: relative;
        }
        li::before {
            content: '♦'; /* A slightly more interesting diamond bullet */
            color: var(--secondary-accent-color); /* Bullet in secondary accent color for playfulness */
            font-size: 1.1em; /* Standard size bullet */
            position: absolute;
            left: 0;
            top: 0.1em; /* Fine-tuned alignment */
            font-weight: bold;
        }

        .tag {
            background-color: var(--highlight-bg-color);
            color: var(--primary-text-color); /* Tags use primary text color for readability */
            padding: 10px 18px; /* Slightly larger, more comfortable tags */
            border-radius: 12px; /* Softer pill shape */
            font-size: 1em; /* Slightly larger font */
            font-weight: 500;
            margin-right: 15px; /* More space */
            margin-bottom: 15px; /* More space */
            display: inline-block; /* Ensure they lay out nicely */
            transition: background-color 0.3s ease, transform 0.2s ease; /* Transition for hover */
        }
        .tag:hover {
            background-color: var(--accent-color); /* Hover effect for tags */
            color: white;
            transform: translateY(-2px); /* Subtle lift on hover */
        }


        .pronunciation {
            font-family: 'Fira Mono', monospace; /* A clean, modern monospaced font */
            font-size: 1.2em; /* Slightly larger for clarity */
            background-color: var(--highlight-bg-color);
            padding: 15px 22px; /* More padding */
            border-radius: 12px;
            display: inline-block;
            margin-top: 25px;
            color: var(--primary-text-color);
            box-shadow: 0 2px 8px rgba(0,0,0,0.05); /* Subtle shadow */
        }

        .scenario-grid {
            /* FORCED SINGLE COLUMN: All scenarios will stack vertically */
            display: grid;
            grid-template-columns: 1fr; /* This is the key: forces one column */
            gap: 40px; /* Still maintains vertical space between cards */
            margin-top: 40px; /* More space above */
        }

        .scenario-card {
            background-color: var(--background-color-card);
            border: 1px solid var(--border-color);
            border-radius: 16px; /* Softer radius */
            padding: 35px; /* More internal padding */
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.06); /* Softer initial shadow */
            transition: transform 0.3s ease-out, box-shadow 0.3s ease-out; /* Smoother, longer transition */
        }
        .scenario-card:hover {
            transform: translateY(-6px) scale(1.005); /* More noticeable lift and tiny scale */
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15); /* More prominent shadow on hover */
        }

        .scenario-card h4 {
            font-family: 'Outfit', sans-serif; /* Consistent header font */
            color: var(--accent-color); /* Scenario titles use accent color */
            font-size: 1.6em; /* Clearer scenario titles */
            font-weight: 600;
            margin-top: 0;
            margin-bottom: 18px; /* More margin */
        }

        .scenario-card p {
            margin-bottom: 1.2em;
            font-size: 1.05em; /* Slightly larger text in cards for readability */
            color: var(--secondary-text-color); /* Card text a bit softer */
        }

        .scenario-card .label {
            font-weight: 700; /* Labels even bolder */
            color: var(--primary-text-color);
            margin-right: 12px; /* More space */
        }

        .comparison-item {
            margin-bottom: 30px; /* More space */
            padding-bottom: 30px;
            border-bottom: 1px dashed var(--border-color); /* Dashed border for a lighter, more playful feel */
        }
        .comparison-item strong {
            color: var(--primary-text-color);
            font-weight: 700; /* Even bolder */
            font-size: 1.25em; /* Clearer comparison headings */
        }

        .expression-text {
            font-weight: 500;
            color: var(--primary-text-color);
            background-color: var(--highlight-bg-color);
            padding: 18px 25px; /* More padding for a softer feel */
            border-radius: 14px; /* Softer radius */
            display: block;
            margin-top: 30px; /* More space */
            font-style: italic; /* Subtle italic for expressions, makes them feel distinct */
            box-shadow: inset 0 1px 5px rgba(0,0,0,0.03); /* Inner shadow for subtle depth */
        }
        .expression-text strong {
            color: var(--accent-color); /* The core word accent color */
            font-weight: 800; /* Extra bold for emphasis */
            /* animation: pulse 1.5s infinite alternate; /* Uncomment for continuous subtle pulse */
        }

        /* Keyframes for potential subtle pulse animation on highlighted words */
        @keyframes pulse {
            from { transform: scale(1); }
            to { transform: scale(1.01); }
        }

        /* --- New CSS for user-added sections --- */
        .user-added-section {
            margin-top: 60px; /* More space above this whole section */
            padding-top: 30px;
            border-top: 2px solid var(--secondary-accent-color); /* A clear divider */
        }

        .user-added-section h2 {
            color: var(--secondary-accent-color); /* Make this section's header stand out */
            border-color: var(--accent-color); /* Complementary border */
        }
        .user-added-section h2::after {
            background-color: var(--primary-text-color); /* A different accent for this H2 */
        }

        .user-scenario-card h4 {
            color: var(--accent-color); /* Keep scenario titles consistent */
        }

        .user-media-card {
            text-align: center;
            margin-top: 40px; /* Space between user scenario and media */
        }
        .user-media-card img,
        .user-media-card video,
        .user-media-card audio {
            max-width: 100%;
            width: 80%; /* Make media a bit narrower for better focus */
            min-height: 50px; /* Ensure there's a minimum height for media */
            height: auto;
            display: block;
            margin: 20px auto;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1); /* Subtle shadow for media */
        }
        .user-media-card video {
            max-height: 400px; /* Limit video height */
        }
        .user-media-card audio {
            width: 80%; /* Make audio player a bit narrower */
        }

        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700&family=Fira+Mono:wght@400&display=swap');
    """


def _generate_header_html(analysis: 'WordAnalysis') -> str:
    """Generates the main word and part of speech header."""
    return f"""
        <h1>{analysis.word}</h1>
        <span class="part-of-speech">({analysis.part_of_speech})</span>
        <p class="definition">{analysis.definition}</p>
    """


def _generate_core_meaning_html(meaning: 'CoreMeaning') -> str:
    """Generates the HTML for the Core Meaning section with Dutch subheaders."""
    translations_html = "".join(f"<li>{t}</li>" for t in meaning.translation)
    return f"""
        <h2>Kernbetekenis</h2>
        <h3>Vertalingen</h3>
        <ul>
            {translations_html}
        </ul>
        <h3>Nuance</h3>
        <p>{meaning.nuance}</p>
    """


def _generate_grammar_html(analysis: 'WordAnalysis') -> str:
    """Generates the HTML for the Grammar section with Dutch subheaders."""
    return f"""
        <h2>Grammatica</h2>
        <p><span class="label">Lidwoord:</span> {analysis.article}</p>
        <p><span class="label">Verleden Tijd:</span> {analysis.simple_past}</p>
        <p><span class="label">Voltooid Deelwoord:</span> {analysis.past_participle}</p>
    """


def _generate_contextual_info_html(context: 'ContextualInfo') -> str:
    """Generates the HTML for the Contextual Information section with Dutch subheaders."""
    comparisons_html = ""
    if context.comparisons:
        for synonym, explanation in context.comparisons.items():
            comparisons_html += f"""
            <div class="comparison-item">
                <strong>{synonym}</strong>: {explanation}
            </div>
            """
    else:
        comparisons_html = "<p>Geen specifieke vergelijkingen beschikbaar.</p>"

    return f"""
        <h2>Contextuele Informatie</h2>
        <p><span class="label">Formaliteit:</span> <span class="tag">{context.formality}</span></p>
        <h3>Typisch Gebruik</h3>
        <p>{context.typical_usage}</p>
        <h3>Veelgemaakte Fouten</h3>
        <p>{context.common_mistake}</p>
        <h3>Vergelijkingen</h3>
        {comparisons_html}
    """


def _generate_relational_web_html(relations: 'RelationalWeb') -> str:
    """Generates the HTML for the Relational Web section with Dutch subheaders."""
    synonyms_html = "".join(
        f'<span class="tag">{s}</span>' for s in relations.synonyms) if relations.synonyms else "Geen synoniemen beschikbaar."
    antonyms_html = "".join(
        f'<span class="tag">{a}</span>' for a in relations.antonyms) if relations.antonyms else "Geen antoniemen beschikbaar."
    collocations_html = "".join(
        f'<span class="tag">{c}</span>' for c in relations.collocations) if relations.collocations else "Geen collocaties beschikbaar."

    return f"""
        <h2>Relationeel Netwerk</h2>
        <h3>Synoniemen</h3>
        <p>{synonyms_html}</p>
        <h3>Antoniemen</h3>
        <p>{antonyms_html}</p>
        <h3>Collocaties</h3>
        <p>{collocations_html}</p>
    """


def _generate_physicality_html(physicality: 'Physicality') -> str:
    """Generates the HTML for the Physicality section with Dutch subheaders."""
    return f"""
        <h2>Uitspraak & Vorm</h2>
        <h3>Uitspraak (IPA)</h3>
        <p class="pronunciation">{physicality.pronunciation_ipa}</p>
    """


def _generate_scenarios_html(scenarios: List['ThoughtScenario'], target_word: str) -> str:
    """
    Generates the HTML for the Thought Scenarios section with Dutch subheaders,
    ensuring the target word is consistently highlighted.
    """
    scenarios_cards_html = ""
    for scenario in scenarios:
        # First, remove any existing '**' markers from the expression to prevent conflicts
        # with our new automatic highlighting logic.
        cleaned_expression = scenario.expression.replace('**', '')

        # Highlight the target_word (analysis.word) within the cleaned expression.
        # This regex performs a case-insensitive replacement of the exact word, respecting word boundaries.
        # It replaces the matched text with the target word wrapped in strong tags.
        highlighted_expression = re.sub(
            # Escape special regex characters in target_word
            r'\b' + re.escape(target_word) + r'\b',
            # Replace with the target word wrapped in strong
            f'<strong>{target_word}</strong>',
            cleaned_expression,
            flags=re.IGNORECASE
        )

        if highlighted_expression:
            scenarios_cards_html += f"""
                <div class="scenario-card">
                    <h4>{scenario.title}</h4>
                    <p><span class="label">Situatie:</span> {scenario.situation}</p>
                    <p><span class="label">Interne Monoloog:</span> {scenario.internal_monologue}</p>
                    <div class="expression-text">
                        <span class="label">Uitdrukking:</span> {highlighted_expression}
                    </div>
                </div>
            """
        else:  # put an input field for the user to fill in
            scenarios_cards_html += f"""
                <div class="scenario-card">
                    <h4>{scenario.title}</h4>
                    <p><span class="label">Situatie:</span> {scenario.situation}</p>
                    <p><span class="label">Interne Monoloog:</span> {scenario.internal_monologue}</p>
                    <div class="expression-text">
                        <span class="label">Uitdrukking:</span>
                        <input type="text" placeholder="Vul hier de uitdrukking in met '{target_word}'" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--border-color);">
                    </div>
                </div>
            """
    return f"""
        <h2>Gedachtescenario's</h2>
        <div class="scenario-grid">
            {scenarios_cards_html}
        </div>
    """


def _generate_user_scenario_html(user_scenario: 'ThoughtScenario', target_word: str) -> str:
    """Generates HTML for a single user-provided thought scenario."""
    # Ensure user-provided scenario's expression also highlights the target word
    cleaned_expression = user_scenario.expression.replace('**', '')
    highlighted_expression = re.sub(
        r'\b' + re.escape(target_word) + r'\b',
        f'<strong>{target_word}</strong>',
        cleaned_expression,
        flags=re.IGNORECASE
    )

    statement = f"""
        <div class="user-added-section">
            <h2>Jouw Eigen Gedachtescenario</h2>
            <div class="scenario-grid">
                <div class="scenario-card user-scenario-card">
                    <h4>{user_scenario.title}</h4>
                    <p><span class="label">Situatie:</span> {user_scenario.situation}</p>
                    <p><span class="label">Interne Monoloog:</span> {user_scenario.internal_monologue}</p>
                    <div class="expression-text">
                        <span class="label">Uitdrukking:</span> {highlighted_expression}
                    </div>
                </div>
            </div>
        </div>
    """

    return statement


def _generate_user_media_html(image_url: Optional[str] = None,
                              audio_url: Optional[str] = None,
                              video_url: Optional[str] = None) -> str:
    """Generates HTML for user-provided media (image, audio, video)."""
    media_content = []
    if image_url:
        media_content.append(
            f'<img src="{image_url}" alt="Door gebruiker toegevoegde afbeelding">')
    if audio_url:
        media_content.append(f"""
            <audio controls>
                <source src="{audio_url}" type="audio/mpeg">
                <source src="{audio_url}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
        """)
    if video_url:
        media_content.append(f"""
            <video controls>
                <source src="{video_url}" type="video/mp4">
                <source src="{video_url}" type="video/webm">
                Your browser does not support the video tag.
            </video>
        """)

    if not media_content:
        return ""  # Return empty string if no media is provided

    return f"""
        <div class="user-added-section user-media-card">
            <h2>Jouw Eigen Media</h2>
            {"".join(media_content)}
        </div>
    """


def generate_word_html_design(
    analysis: 'WordAnalysis',
    user_scenario: Optional['ThoughtScenario'] = None,
    user_image_url: Optional[str] = None,
    user_audio_url: Optional[str] = None,
    user_video_url: Optional[str] = None
) -> str:
    """
    Generates a beautiful HTML/CSS design for a given WordAnalysis object,
    with Dutch subheaders and consistent highlighting, and translation at the end.
    Optionally includes user-provided scenarios and media.

    Args:
        analysis: A Pydantic WordAnalysis object containing all word details.
        user_scenario: An optional ThoughtScenario object provided by the user.
        user_image_url: An optional URL for a user-provided image.
        user_audio_url: An optional URL for a user-provided audio file.
        user_video_url: An optional URL for a user-provided video file.

    Returns:
        A string containing the full HTML document with embedded CSS.
    """
    css_content = _generate_css()
    header_html = _generate_header_html(analysis)
    grammar_html = _generate_grammar_html(analysis)
    contextual_info_html = _generate_contextual_info_html(analysis.context)
    relational_web_html = _generate_relational_web_html(analysis.relations)
    physicality_html = _generate_physicality_html(analysis.physicality)
    scenarios_html = _generate_scenarios_html(
        analysis.thought_scenarios, analysis.word)
    core_meaning_html = _generate_core_meaning_html(analysis.meaning)

    # Conditional generation of user-provided content
    user_content_html = ""
    if user_scenario:
        user_content_html += _generate_user_scenario_html(
            user_scenario, analysis.word)

    # Combine all media into one section if any is provided
    if user_image_url or user_audio_url or user_video_url:
        user_content_html += _generate_user_media_html(
            user_image_url, user_audio_url, user_video_url)

    html_template = f"""
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Woordanalyse: {analysis.word}</title>
    <style>
        {css_content}
    </style>
</head>
<body>
    <div class="word-container">
        {header_html}
        {grammar_html}
        {contextual_info_html}
        {relational_web_html}
        {physicality_html}
        {scenarios_html}
        {core_meaning_html}
        {user_content_html} </div>
</body>
</html>
    """
    return html_template


# embed for streamlit, use iframe
def embed_video(video_url: str) -> str:
    """Generates an HTML iframe for embedding a video in Streamlit.
    Parameters
    ----------
        video_url: The URL of the video to embed
    Returns
    -------
        A string containing the HTML iframe code for the video.
    """
    return f"""
    <iframe width="80%" height="500" src="{video_url}" frameborder="0" allowfullscreen></iframe>
    """


def generate_single_prompt_card_html(prompt: 'EnkelePrompt') -> str:
    """
    Generates highly stylized HTML for a single prompt card, designed to be
    conspicuous, elegant, and interactive.

    This version uses a modern CSS approach with a nested div structure to create a
    gradient border, along with advanced hover effects and decorative pseudo-elements.

    Args:
        prompt: An EnkelePrompt object containing the prompt details.

    Returns:
        A string containing the self-contained HTML and CSS for the prompt card.
    """
    # --- Input Validation and Sanitization ---
    if not hasattr(prompt, 'prompt_tekst'):
        return "<p style='color: red; font-family: sans-serif;'>Fout: Invoerobject heeft geen 'prompt_tekst' attribuut.</p>"

    # Clean the text and escape it to prevent HTML injection
    cleaned_prompt_text = html.escape(prompt.prompt_tekst.strip('"'))

    # --- HTML & CSS block ---
    html_content = f"""
    <style>
        /* Import Google Font for the card */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

        /* The main container acts as the gradient border and shadow holder */
        .prompt-card-container {{
            max-width: 800px;
            margin: 40px auto; /* Provides vertical spacing */
            padding: 3px; /* This padding with the gradient background creates the border effect */
            background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
            border-radius: 24px;
            box-shadow: 0 10px 30px -15px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease-in-out;
        }}

        /* The hover effect is applied to the container, making everything inside react */
        .prompt-card-container:hover {{
            transform: translateY(-8px) scale(1.03); /* Lift and grow effect */
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.4);
        }}

        /* The inner content box with the white background */
        .prompt-card-content {{
            padding: 40px 45px;
            background-color: #ffffff;
            border-radius: 21px; /* Slightly smaller radius to sit inside the container */
            position: relative; /* Needed for the pseudo-element */
            overflow: hidden;   /* Hides the overflowing parts of the pseudo-element */
        }}

        /* A decorative glowing orb in the background for a bit of fun */
        .prompt-card-content::before {{
            content: '';
            position: absolute;
            top: -100px;
            right: -100px;
            width: 250px;
            height: 250px;
            background: radial-gradient(circle, rgba(102, 166, 255, 0.2), transparent 70%);
            transition: all 0.5s ease;
            opacity: 0.7;
            z-index: 1; /* Sits below the text */
        }}

        /* Animate the orb on hover for a dynamic feel */
        .prompt-card-container:hover .prompt-card-content::before {{
            transform: scale(1.2);
            opacity: 1;
        }}

        /* The actual text styling */
        .prompt-text-embedded {{
            font-family: 'Poppins', sans-serif;
            font-size: 1.5rem; /* Larger and more prominent */
            font-weight: 500;  /* Medium weight is elegant and readable */
            line-height: 1.7;
            color: #2a3342; /* A softer, more professional dark color */
            text-align: center;
            margin: 0;
            position: relative; /* Ensures text is on top of the pseudo-element */
            z-index: 2;
        }}
    </style>

    <div class="prompt-card-container" role="alert" aria-live="polite">
        <div class="prompt-card-content">
            <p class="prompt-text-embedded">{cleaned_prompt_text}</p>
        </div>
    </div>
    """
    return html_content


def _generate_card_scholarly(prompt_text: str) -> str:
    """Generates an elegant, academic-themed card."""
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500&display=swap');
        .card-scholar {{
            background: #fdfaf3;
            border-left: 5px solid #a88562;
            padding: 30px 40px;
            margin: 30px auto;
            max-width: 750px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border-radius: 4px;
            font-family: 'Lora', serif;
            color: #4a4a4a;
            transition: all 0.3s ease;
            position: relative;
        }}
        .card-scholar:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
            border-left-color: #c49a6c;
        }}
        .card-scholar p {{
            font-size: 1.25rem;
            line-height: 1.8;
            margin: 0;
            text-align: center;
        }}
    </style>
    <div class="card-scholar">
        <p>{prompt_text}</p>
    </div>
    """

# -----------------------------------------------------------------------------
#  DESIGN 2: NEON WAVE
# -----------------------------------------------------------------------------


def _generate_card_neon_wave(prompt_text: str) -> str:
    """Generates a futuristic, dark-mode card with a neon glow."""
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@500&display=swap');
        .card-neon-container {{
            padding: 2px;
            background: linear-gradient(135deg, #ff00c1, #9b00e9);
            border-radius: 18px;
            max-width: 750px;
            margin: 30px auto;
            box-shadow: 0 0 25px rgba(255, 0, 193, 0.4);
            transition: all 0.3s ease-out;
        }}
        .card-neon-container:hover {{
             box-shadow: 0 0 40px rgba(155, 0, 233, 0.6);
        }}
        .card-neon {{
            background: #1a1a2e;
            color: #e0e0e0;
            padding: 40px;
            border-radius: 16px;
            font-family: 'Fira Code', monospace;
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);
            transition: background 0.3s ease;
        }}
        .card-neon p {{
            font-size: 1.15rem;
            line-height: 1.7;
            text-align: center;
            margin: 0;
            color: #a7d1ff;
        }}
        .card-neon-container:hover .card-neon {{
            background: #24243e;
        }}
    </style>
    <div class="card-neon-container">
        <div class="card-neon">
            <p>&gt; {prompt_text}</p>
        </div>
    </div>
    """

# -----------------------------------------------------------------------------
#  DESIGN 3: CALM GARDEN
# -----------------------------------------------------------------------------


def _generate_card_calm_garden(prompt_text: str) -> str:
    """Generates a soft, nature-inspired card."""
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600&display=swap');
        .card-garden {{
            background: #f0f7f1;
            border: 2px solid #a3c9a8;
            border-radius: 30px;
            padding: 40px;
            max-width: 750px;
            margin: 30px auto;
            font-family: 'Nunito Sans', sans-serif;
            color: #3e5641;
            position: relative;
            box-shadow: 0 5px 10px -5px rgba(0,0,0,0.05);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }}
        .card-garden:hover {{
            transform: scale(1.02);
            box-shadow: 0 10px 20px -10px rgba(62, 86, 65, 0.2);
            border-color: #84b38a;
        }}
        .card-garden p {{
            font-size: 1.3rem;
            line-height: 1.7;
            text-align: center;
            font-weight: 400;
            margin: 0;
        }}
    </style>
    <div class="card-garden">
        <p>{prompt_text}</p>
    </div>
    """

# -----------------------------------------------------------------------------
#  DESIGN 4: BOLD MINIMALIST
# -----------------------------------------------------------------------------


def _generate_card_bold_minimalist(prompt_text: str) -> str:
    """Generates a high-contrast, minimalist card with a bold accent."""
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@700&display=swap');
        .card-minimalist {{
            background: #ffffff;
            border: 3px solid #111;
            padding: 50px;
            max-width: 750px;
            margin: 30px auto;
            border-radius: 0;
            font-family: 'Inter', sans-serif;
            color: #111;
            box-shadow: 8px 8px 0px #e44d26; /* The accent color */
            transition: all 0.2s ease-in-out;
            text-align: center;
        }}
        .card-minimalist:hover {{
            box-shadow: 12px 12px 0px #e44d26;
            transform: translate(-4px, -4px);
        }}
        .card-minimalist p {{
            font-size: 1.6rem;
            line-height: 1.6;
            margin: 0;
            font-weight: 700;
        }}
    </style>
    <div class="card-minimalist">
        <p>{prompt_text}</p>
    </div>
    """

# -----------------------------------------------------------------------------
#  DESIGN 5: SKETCHBOOK IDEA
# -----------------------------------------------------------------------------


def _generate_card_sketchbook(prompt_text: str) -> str:
    """Generates a card that looks like a hand-drawn sketchbook entry."""
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Kalam:wght@400&display=swap');
        .card-sketch {{
            background: #fffcf5;
            padding: 35px;
            max-width: 750px;
            margin: 30px auto;
            font-family: 'Kalam', cursive;
            color: #333;
            border: 2px solid #555;
            /* Creates a sketchy border effect using border-radius */
            border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
            position: relative;
            box-shadow: 3px 3px 5px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
        }}
        .card-sketch:hover {{
             transform: rotate(1deg);
             box-shadow: 5px 5px 8px rgba(0,0,0,0.15);
        }}
        .card-sketch p {{
            font-size: 1.4rem;
            line-height: 1.7;
            text-align: center;
            margin: 0;
        }}
    </style>
    <div class="card-sketch">
        <p>{prompt_text}</p>
    </div>
    """


# -----------------------------------------------------------------------------
#  THE MOTHER FUNCTION (DISPATCHER)
# -----------------------------------------------------------------------------
def generate_prompt_card_html(prompt: EnkelePrompt, design_choice: int = 1) -> str:
    """
    Generates and returns stylized HTML for a prompt card based on a chosen design.

    This function acts as a dispatcher, calling one of several specialized
    functions to generate the card's HTML and CSS.

    Args:
        prompt: An EnkelePrompt object containing the prompt details.
        design_choice: An integer from 1 to 5 to select the design theme:
                       1: Scholarly (Default)
                       2: Neon Wave
                       3: Calm Garden
                       4: Bold Minimalist
                       5: Sketchbook Idea

    Returns:
        A string containing the self-contained HTML and CSS for the prompt card.
    """
    # --- Input Validation and Sanitization ---
    if not isinstance(prompt, EnkelePrompt) or not hasattr(prompt, 'prompt_tekst'):
        return "<p style='color: red; font-family: sans-serif;'>Fout: Ongeldig invoerobject.</p>"

    # Securely escape the text to prevent HTML injection.
    cleaned_prompt_text = html.escape(prompt.prompt_tekst.strip('"'))

    # --- Design Dispatcher ---
    # A dictionary mapping the design choice to the appropriate function.
    design_functions: Dict[int, Callable[[str], str]] = {
        1: _generate_card_scholarly,
        2: _generate_card_neon_wave,
        3: _generate_card_calm_garden,
        4: _generate_card_bold_minimalist,
        5: _generate_card_sketchbook,
    }

    # Get the function for the chosen design, or default to the first one.
    selected_function = design_functions.get(
        design_choice, _generate_card_scholarly)

    return selected_function(cleaned_prompt_text)
