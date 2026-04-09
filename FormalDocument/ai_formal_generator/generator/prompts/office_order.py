"""Prompt builder for Government Office Order documents (BISAG-N).

Public API
----------
build_generation_prompt(topic, language)  -> str
build_regeneration_prompt(topic, previous_body, refinement_prompt, language) -> str
"""


from langchain_core.prompts import PromptTemplate

from ._shared import Language, build_generation, build_regeneration

PROMPT_VERSION = "OfficeOrder_v1"

# ---------------------------------------------------------------------------
# Generation templates
# NOTE: No {today} — date context is only meaningful during *regeneration*.
# ---------------------------------------------------------------------------

GENERATION_TEMPLATE_EN = PromptTemplate(
    input_variables=["topic", "version"],
    template="""[Prompt Version: {version}]

You are drafting the BODY of an official government Office Order for BISAG-N.

Rules:
- Write one formal paragraph (minimum 2–3 sentences).
- Use official government tone.
- The response must read like an officially issued administrative document.
- Do not include title, reference, date, From or To.
- No bullet points or numbering.
- Plain text only.

<<<START_TOPIC>>>
{topic}
<<<END_TOPIC>>>
""",
)

GENERATION_TEMPLATE_HI = PromptTemplate(
    input_variables=["topic", "version"],
    template="""[Prompt Version: {version}]

आप BISAG-N के लिए एक आधिकारिक कार्यालय आदेश की मुख्य सामग्री लिख रहे हैं।

नियम:
- कम से कम 2–3 वाक्यों का एक औपचारिक अनुच्छेद लिखें।
- सरकारी भाषा का प्रयोग करें।
- उत्तर एक आधिकारिक प्रशासनिक दस्तावेज़ की तरह प्रतीत होना चाहिए।
- कोई शीर्षक, संदर्भ, दिनांक, प्रेषक या प्राप्तकर्ता न लिखें।
- बुलेट या क्रमांक का प्रयोग न करें।
- केवल सादा पाठ में उत्तर दें।

<<<START_TOPIC>>>
{topic}
<<<END_TOPIC>>>
""",
)

# ---------------------------------------------------------------------------
# Regeneration templates
# {today} is provided here — the date grounds the refined version in time.
# ---------------------------------------------------------------------------

REGENERATION_TEMPLATE_EN = PromptTemplate(
    input_variables=["topic", "previous_body", "refinement_prompt", "today", "version"],
    template="""[Prompt Version: {version}]

You are refining the BODY of an official government Office Order for BISAG-N.

Today's Date: {today}

Rules:
- Create an improved version based on the three inputs below.
- Must be better and more formal than the previous version.
- Use official government tone.
- The response must read like an officially issued administrative document.
- Do not include title, reference, date, From or To.
- Plain text only.
- Write one formal paragraph (minimum 2–3 sentences).

<<<ORIGINAL_TOPIC>>>
{topic}
<<<END_TOPIC>>>

<<<PREVIOUS_BODY>>>
{previous_body}
<<<END_PREVIOUS_BODY>>>

<<<REFINEMENT_REQUEST>>>
{refinement_prompt}
<<<END_REFINEMENT_REQUEST>>>
""",
)

REGENERATION_TEMPLATE_HI = PromptTemplate(
    input_variables=["topic", "previous_body", "refinement_prompt", "today", "version"],
    template="""[Prompt Version: {version}]

आप BISAG-N के लिए एक आधिकारिक कार्यालय आदेश की मुख्य सामग्री को परिष्कृत और अनुकूलित कर रहे हैं।

आज की तारीख: {today}

नियम:
- नीचे दिए गए तीनों इनपुट के आधार पर एक बेहतर, परिष्कृत संस्करण बनाएं।
- पिछले संस्करण की तुलना में बेहतर और अधिक औपचारिक होना चाहिए।
- सरकारी भाषा का प्रयोग करें।
- उत्तर एक आधिकारिक प्रशासनिक दस्तावेज़ की तरह प्रतीत होना चाहिए।
- कोई शीर्षक, संदर्भ, दिनांक, प्रेषक या प्राप्तकर्ता न लिखें।
- केवल सादा पाठ में उत्तर दें।
- कम से कम 2–3 वाक्यों का एक औपचारिक अनुच्छेद लिखें।

<<<ORIGINAL_TOPIC>>>
{topic}
<<<END_TOPIC>>>

<<<PREVIOUS_BODY>>>
{previous_body}
<<<END_PREVIOUS_BODY>>>

<<<REFINEMENT_REQUEST>>>
{refinement_prompt}
<<<END_REFINEMENT_REQUEST>>>
""",
)


# ---------------------------------------------------------------------------
# Build functions
# ---------------------------------------------------------------------------

def build_generation_prompt(topic: str, language: Language = "en") -> str:
    """Return a formatted generation prompt for an Office Order body."""
    return build_generation(
        en_template=GENERATION_TEMPLATE_EN,
        hi_template=GENERATION_TEMPLATE_HI,
        prompt_version=PROMPT_VERSION,
        topic=topic,
        language=language,
        document_type="Office Order",
    )


def build_regeneration_prompt(
    topic: str,
    previous_body: str,
    refinement_prompt: str,
    language: Language = "en",
) -> str:
    """Return a formatted regeneration prompt for an Office Order body."""
    return build_regeneration(
        en_template=REGENERATION_TEMPLATE_EN,
        hi_template=REGENERATION_TEMPLATE_HI,
        prompt_version=PROMPT_VERSION,
        topic=topic,
        previous_body=previous_body,
        refinement_prompt=refinement_prompt,
        language=language,
        document_type="Office Order",
    )