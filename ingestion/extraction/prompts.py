"""
BLACKOUT Claim/Decision Extraction Prompts
"""

EXTRACTION_PROMPT = """Given this {source_system} content, extract:
1. Any concrete organizational claims or decisions stated or implied
   (policy, pricing, architecture, ownership, technical decisions).
2. For each, the exact author and timestamp (if available).
3. Whether it reads as a NEW decision or a correction/update to a prior one.

Content:
{content}

Return JSON in this exact format:
[
  {{
    "claim_text": "The extracted claim or decision text",
    "author_raw": "Author name or identifier",
    "timestamp": "ISO format timestamp or null",
    "type": "decision" | "claim",
    "supersedes_hint": true/false
  }}
]

Only extract clear, concrete claims. Do not extract:
- Questions or discussions without a conclusion
- General chatter or social messages
- Requests or proposals that haven't been decided

If no claims are found, return an empty array [].
"""
