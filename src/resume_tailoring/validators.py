import re


def extract_entities(text: str) -> set[str]:
    # Simple token entity extractor placeholder.
    # Replace with robust NER if needed.
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9+#./-]{2,}", text)
    return {t.lower() for t in tokens}


def validate_claims_supported(generated_text: str, source_resume: str, candidate_profile: str, job_title: str) -> list[str]:
    allowed = extract_entities(source_resume) | extract_entities(candidate_profile) | extract_entities(job_title)
    generated = extract_entities(generated_text)
    unsupported = sorted(token for token in generated if token not in allowed)
    return unsupported
