from typing import List, Dict
from app.configs.config import settings
from google import genai

MODEL = "gemini-2.0-flash-exp"


def _get_genai_client():
    if genai is None:
        raise RuntimeError("google-genai not installed")
    return genai.Client(api_key=settings.GOOGLE_API_KEY)


def generate_linkedin_post(topic: str, context_snippets: List[str], length: str = "short") -> Dict:
    client = _get_genai_client()
    
    prompt = (
        f"You are a social media copywriter. Create a LinkedIn post about '{topic}'.\n\n"
        "Context (recent news snippets):\n"
    )
    for i, s in enumerate(context_snippets, 1):
        prompt += f"{i}. {s}\n"
    
    prompt += (
        "\nRequirements:\n"
        "- Hook in first line (attention grabbing)\n"
        "- 2-4 lines max for short, 4-8 lines for long\n"
        "- Add 3 relevant hashtags at the end\n"
        "- Add 1 short CTA (e.g., 'Thoughts?')\n"
    )
    
    if length == "short":
        prompt += "\nTone: professional, concise\n"
    else:
        prompt += "\nTone: professional, slightly detailed\n"

    resp = client.models.generate_content(model=MODEL, contents=prompt)
    text = _extract_text_from_response(resp)
    
    if not isinstance(text, str):
        text = str(text)

    return {
        "content": text,
        "summary": context_snippets[0] if context_snippets else ""
    }


def _extract_text_from_response(resp) -> str:
    try:
        if hasattr(resp, 'text'):
            return str(resp.text)
        
        if hasattr(resp, 'candidates') and resp.candidates:
            candidate = resp.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                parts = candidate.content.parts
                if parts and hasattr(parts[0], 'text'):
                    return str(parts[0].text)
        
        return str(resp)
        
    except Exception as e:
        print(f"Error extracting text: {e}")
        return str(resp)
