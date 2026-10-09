import re
from datetime import date
from typing import Optional


def _extract_deadline(text: str) -> Optional[date]:
    match = re.search(
        r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b",
        text,
    )

    if not match:
        return None

    day = int(match.group(1))
    month = int(match.group(2))
    year_text = match.group(3)

    if year_text:
        year = int(year_text)
        if year < 100:
            year += 2000
    else:
        year = date.today().year

    try:
        return date(year, month, day)
    except ValueError:
        return None


def _extract_number(
    text: str,
    patterns: list[str],
) -> Optional[int]:

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return int(match.group(1))

    return None


def _extract_duration_minutes(
    text: str,
) -> Optional[int]:
    """
    Extract duration from phrases such as:

        3 hours
        2.5 hours
        90 minutes
        2 hr
        2 hrs
        2 hrours  <- common typo
    """

    # Normalize common typo.
    normalized = re.sub(
        r"\bhrours\b",
        "hours",
        text,
        flags=re.IGNORECASE,
    )

    hour_match = re.search(
        r"\b(?:for\s+)?(\d+(?:\.\d+)?)\s*"
        r"(?:hours?|hrs?|hr)\b",
        normalized,
        re.IGNORECASE,
    )

    if hour_match:
        hours = float(hour_match.group(1))
        return int(hours * 60)

    minute_match = re.search(
        r"\b(?:for\s+)?(\d+)\s*"
        r"(?:minutes?|mins?|min)\b",
        normalized,
        re.IGNORECASE,
    )

    if minute_match:
        return int(minute_match.group(1))

    return None


def _extract_subject(
    text: str,
    assignment_type: str,
) -> Optional[str]:

    patterns = []

    if assignment_type == "study":

        patterns = [
            r"\bpractice\s+(.+?)(?=\s+(?:for|upto|until|by|daily)\b|$)",
            r"\bstudy\s+(.+?)(?=\s+(?:for|upto|until|by|daily)\b|$)",
            r"\blearn\s+(.+?)(?=\s+(?:for|upto|until|by|daily)\b|$)",
            r"\bprepare\s+(?:for\s+)?(.+?)(?=\s+(?:for|upto|until|by|daily)\b|$)",
        ]

    elif assignment_type == "writing":

        patterns = [
            r"(?:paper|essay|report|article)"
            r"\s+(?:about|on|regarding)\s+"
            r"(.+?)(?=\s+(?:by|due|upto|until)\b|$)",
        ]

    elif assignment_type == "presentation":

        patterns = [
            r"(?:presentation|slides?)"
            r"\s+(?:about|on|regarding)\s+"
            r"(.+?)(?=\s+(?:by|due|upto|until)\b|$)",
        ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:

            subject = match.group(1).strip()
            subject = subject.rstrip(".,!?")

            if subject:
                return subject

    return None


def analyze_assignment(text: str) -> dict:

    if not text or not text.strip():
        raise ValueError(
            "Assignment text cannot be empty."
        )

    text = " ".join(text.strip().split())
    lower_text = text.lower()

    # -----------------------------------------------------
    # Assignment type
    # -----------------------------------------------------

    project_words = [
        "project",
        "build",
        "develop",
        "application",
        "app",
        "program",
        "implement",
        "code",
        "website",
    ]

    presentation_words = [
        "presentation",
        "slides",
        "ppt",
        "powerpoint",
    ]

    writing_words = [
        "paper",
        "essay",
        "research paper",
        "report",
        "article",
    ]

    study_words = [
        "study",
        "practice",
        "learn",
        "revise",
        "revision",
        "prepare for",
        "exam preparation",
        "prepare",
    ]

    if any(word in lower_text for word in project_words):

        assignment_type = "project"

    elif any(word in lower_text for word in presentation_words):

        assignment_type = "presentation"

    elif any(word in lower_text for word in writing_words):

        assignment_type = "writing"

    elif any(word in lower_text for word in study_words):

        assignment_type = "study"

    elif re.search(
        r"\b(?:exam|quiz|test)\b",
        lower_text,
    ):

        assignment_type = "study"

    elif "write" in lower_text:

        assignment_type = "writing"

    else:

        assignment_type = "general"

    # -----------------------------------------------------
    # Extract information
    # -----------------------------------------------------

    pages = _extract_number(
        lower_text,
        [
            r"\b(\d+)\s*[-]?\s*pages?\b",
        ],
    )

    slides = _extract_number(
        lower_text,
        [
            r"\b(\d+)\s*[-]?\s*slides?\b",
        ],
    )

    sources_required = _extract_number(
        lower_text,
        [
            r"\bat\s+least\s+(\d+)\s+(?:sources?|references?)\b",
            r"\b(\d+)\s+(?:sources?|references?)\b",
        ],
    )

    requested_duration_minutes = _extract_duration_minutes(text)

    deadline = _extract_deadline(text)

    # -----------------------------------------------------
    # Detect DAILY requirement
    # -----------------------------------------------------

    daily = bool(
        re.search(
            r"\b(?:daily|every\s+day|per\s+day)\b",
            lower_text,
        )
    )

    # -----------------------------------------------------
    # Requirements
    # -----------------------------------------------------

    presentation_required = any(
        word in lower_text
        for word in [
            "presentation",
            "slides",
            "ppt",
            "powerpoint",
        ]
    )

    research_required = any(
        word in lower_text
        for word in [
            "research",
            "sources",
            "references",
            "cite",
            "citations",
        ]
    )

    deployment_required = any(
        word in lower_text
        for word in [
            "deploy",
            "deployment",
            "publish",
            "host",
            "hosting",
        ]
    )

    testing_required = any(
        word in lower_text
        for word in [
            "test",
            "testing",
            "unit test",
            "integration test",
        ]
    )

    # -----------------------------------------------------
    # Subject
    # -----------------------------------------------------

    subject = _extract_subject(
        text,
        assignment_type,
    )

    # -----------------------------------------------------
    # Estimated work
    # -----------------------------------------------------

    if requested_duration_minutes:

        estimated_hours = round(
            requested_duration_minutes / 60,
            1,
        )

    elif pages:

        estimated_hours = pages * 0.75

    elif slides:

        estimated_hours = slides * 0.25

    elif assignment_type == "study":

        estimated_hours = 2.0

    elif assignment_type == "project":

        estimated_hours = 4.0

    elif assignment_type == "presentation":

        estimated_hours = 3.0

    else:

        estimated_hours = 1.0

    if sources_required:
        estimated_hours += sources_required * 0.15

    if deployment_required:
        estimated_hours += 0.5

    if testing_required:
        estimated_hours += 0.5

    estimated_hours = round(
        estimated_hours,
        1,
    )

    return {
        "raw_text": text,
        "assignment_type": assignment_type,
        "subject": subject,
        "requested_duration_minutes": requested_duration_minutes,
        "daily": daily,
        "pages": pages,
        "slides": slides,
        "sources_required": sources_required,
        "presentation_required": presentation_required,
        "research_required": research_required,
        "deployment_required": deployment_required,
        "testing_required": testing_required,
        "deadline": deadline,
        "estimated_hours": estimated_hours,
    }
