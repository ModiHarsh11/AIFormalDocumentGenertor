"""Prompt builder for Government Circular documents (BISAG-N).

Public API
----------
build_generation_prompt(topic, language)  -> str
build_regeneration_prompt(topic, previous_body, refinement_prompt, language) -> str
"""

from langchain_core.prompts import PromptTemplate

from ._shared import Language, build_generation, build_regeneration

PROMPT_VERSION = "Circular_v1"

# =======================
# GENERATION TEMPLATES
# =======================

GENERATION_TEMPLATE_EN = PromptTemplate(
    input_variables=["topic", "version"],
    template="""
[Prompt Version: {version}]

You are drafting the BODY of an official Government Circular for BISAG-N.

Rules:
- Write 1–2 formal paragraphs.
- Use official government tone.
- The response must read like an officially issued administrative circular.
- Do not include subject, title, reference number, signature, date, From or To.
- No bullet points or numbering.
- Plain text only.

<<<START_TOPIC>>>
{topic}
<<<END_TOPIC>>>
"""
)

GENERATION_TEMPLATE_HI = PromptTemplate(
    input_variables=["topic", "version"],
    template="""
[Prompt Version: {version}]

आप BISAG-N के लिए एक सरकारी परिपत्र (Circular) का मुख्य भाग लिख रहे हैं।

नियम:
- 1–2 औपचारिक अनुच्छेद लिखें।
- सरकारी भाषा का प्रयोग करें।
- उत्तर एक आधिकारिक प्रशासनिक परिपत्र जैसा प्रतीत होना चाहिए।
- विषय, शीर्षक, संदर्भ संख्या, हस्ताक्षर, दिनांक, प्रेषक या प्राप्तकर्ता न लिखें।
- बुलेट या क्रमांक का प्रयोग न करें।
- केवल सादा पाठ में उत्तर दें।

<<<START_TOPIC>>>
{topic}
<<<END_TOPIC>>>
"""
)

# =======================
# REGENERATION TEMPLATES
# =======================

REGENERATION_TEMPLATE_EN = PromptTemplate(
    input_variables=["topic", "previous_body", "refinement_prompt", "today", "version"],
    template="""
[Prompt Version: {version}]

You are refining the BODY of an official Government Circular for BISAG-N.

Today's Date: {today}

Rules:
- Improve the circular using the three inputs below.
- The refined version must be clearer, more formal, and administratively stronger.
- Maintain official government tone.
- The response must read like an officially issued administrative circular.
- Do not include subject, title, reference number, signature, date, From or To.
- No bullet points or numbering.
- Plain text only.
- Write 1–2 formal paragraphs.

<<<ORIGINAL_TOPIC>>>
{topic}
<<<END_TOPIC>>>

<<<PREVIOUS_BODY>>>
{previous_body}
<<<END_PREVIOUS_BODY>>>

<<<REFINEMENT_REQUEST>>>
{refinement_prompt}
<<<END_REFINEMENT_REQUEST>>>
"""
)

REGENERATION_TEMPLATE_HI = PromptTemplate(
    input_variables=["topic", "previous_body", "refinement_prompt", "today", "version"],
    template="""
[Prompt Version: {version}]

आप BISAG-N के लिए एक सरकारी परिपत्र (Circular) के मुख्य भाग को परिष्कृत कर रहे हैं।

आज की तारीख: {today}

नियम:
- नीचे दिए गए तीनों इनपुट के आधार पर एक बेहतर और अधिक औपचारिक संस्करण तैयार करें।
- संशोधित संस्करण अधिक स्पष्ट और प्रशासनिक रूप से सुदृढ़ होना चाहिए।
- सरकारी भाषा का प्रयोग करें।
- उत्तर एक आधिकारिक प्रशासनिक परिपत्र जैसा प्रतीत होना चाहिए।
- विषय, शीर्षक, संदर्भ संख्या, हस्ताक्षर, दिनांक, प्रेषक या प्राप्तकर्ता न लिखें।
- बुलेट या क्रमांक का प्रयोग न करें।
- केवल सादा पाठ में उत्तर दें।
- 1–2 औपचारिक अनुच्छेद लिखें।

<<<ORIGINAL_TOPIC>>>
{topic}
<<<END_TOPIC>>>

<<<PREVIOUS_BODY>>>
{previous_body}
<<<END_PREVIOUS_BODY>>>

<<<REFINEMENT_REQUEST>>>
{refinement_prompt}
<<<END_REFINEMENT_REQUEST>>>
"""
)


# =======================
# BUILD FUNCTIONS
# =======================

def build_generation_prompt(topic: str, language: Language = "en") -> str:
    """Return a formatted generation prompt for a Circular body."""
    return build_generation(
        en_template=GENERATION_TEMPLATE_EN,
        hi_template=GENERATION_TEMPLATE_HI,
        prompt_version=PROMPT_VERSION,
        topic=topic,
        language=language,
        document_type="Circular",
    )


def build_regeneration_prompt(
        topic: str,
        previous_body: str,
        refinement_prompt: str,
        language: Language = "en",
) -> str:
    """Return a formatted regeneration prompt for a Circular body."""
    return build_regeneration(
        en_template=REGENERATION_TEMPLATE_EN,
        hi_template=REGENERATION_TEMPLATE_HI,
        prompt_version=PROMPT_VERSION,
        topic=topic,
        previous_body=previous_body,
        refinement_prompt=refinement_prompt,
        language=language,
        document_type="Circular",
    )