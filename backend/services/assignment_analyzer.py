import re
from datetime import date
from typing import Optional


MONTH_NAME_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12,
}


def _extract_deadline(text: str) -> Optional[date]:
    # 1. Numeric with optional ordinals: 26/10/26, 26-10-2026, 26th 10, 26th
    match = re.search(
        r"\b(\d{1,2})(?:st|nd|rd|th)?[\s/,-]+(\d{1,2})(?:st|nd|rd|th)?(?:[\s/,-]+(\d{2,4})(?:st|nd|rd|th)?)?\b",
        text,
        re.IGNORECASE,
    )

    if match:
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
            pass

    # 2. Text month: 26 Oct 2026, 26th October 2026, Oct 26 2026
    text_month_match = re.search(
        r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([a-zA-Z]+)(?:[\s,]+(\d{2,4})(?:st|nd|rd|th)?)?\b",
        text,
        re.IGNORECASE,
    )

    if text_month_match:
        month_str = text_month_match.group(2).lower()
        if month_str in MONTH_NAME_MAP:
            day = int(text_month_match.group(1))
            month = MONTH_NAME_MAP[month_str]
            year_text = text_month_match.group(3)
            if year_text:
                year = int(year_text)
                if year < 100:
                    year += 2000
            else:
                year = date.today().year

            try:
                return date(year, month, day)
            except ValueError:
                pass

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


def _clean_subject(candidate: str) -> Optional[str]:
    """Clean extracted subject and normalize common subject names."""
    if not candidate:
        return None

    # Remove leading prepositions/articles/page descriptors
    candidate = re.sub(
        r"^(?:for|in|about|regarding|on|to|the|a|an|\d+[- ]pages?|page)\s+",
        "",
        candidate.strip(),
        flags=re.IGNORECASE,
    ).strip()

    # Remove trailing date or deadline remnants
    candidate = re.sub(
        r"\s+(?:in|by|on|due|upto|until)\s+.*$",
        "",
        candidate,
        flags=re.IGNORECASE,
    ).strip()

    candidate = candidate.rstrip(".,!?")

    if not candidate or candidate.lower() in [
        "daily", "placement", "exam", "test", "interview", "homework",
    ]:
        return candidate.capitalize() if candidate else None

    # Specific common subjects normalization
    if candidate.lower() == "dsa":
        return "DSA"

    return candidate


def _extract_subject(
    text: str,
    assignment_type: str,
) -> Optional[str]:
    if assignment_type == "study":
        # 1. Subject before practice/study/prep (e.g. "Dsa practice", "Python study", "Math revision")
        prefix_match = re.search(
            r"\b([a-zA-Z0-9+#]+(?:\s+[a-zA-Z0-9+#]+)?)\s+(?:practice|study|prep|preparation|revision|learning)\b",
            text,
            re.IGNORECASE,
        )
        if prefix_match:
            sub = _clean_subject(prefix_match.group(1))
            if sub and sub.lower() not in ["daily", "every", "per"]:
                return sub

        # 2. Subject after practice/study/learn/prepare (e.g. "practice DSA for placement")
        postfix_match = re.search(
            r"\b(?:practice|study|learn|prepare|revise)\s+(?:for\s+)?([a-zA-Z0-9+#]+(?:\s+[a-zA-Z0-9+#]+)?)\b(?:\s+(?:for|upto|until|by|in|before|due|daily)\b|$)",
            text,
            re.IGNORECASE,
        )
        if postfix_match:
            sub = _clean_subject(postfix_match.group(1))
            if sub and sub.lower() not in ["daily", "every", "per"]:
                return sub

        # 3. Purpose as fallback (e.g. "practice for placement in 26/10/26")
        purpose_match = re.search(
            r"\b(?:for|towards)\s+([a-zA-Z0-9+#]+(?:\s+[a-zA-Z0-9+#]+)?)\b",
            text,
            re.IGNORECASE,
        )
        if purpose_match:
            sub = _clean_subject(purpose_match.group(1))
            if sub:
                return sub

    elif assignment_type == "writing":
        # Before or after paper/essay/report
        patterns = [
            r"\b([a-zA-Z0-9+#]+(?:\s+[a-zA-Z0-9+#]+)?)\s+(?:paper|essay|report|article)\b",
            r"(?:paper|essay|report|article)\s+(?:about|on|regarding)\s+([a-zA-Z0-9+#]+(?:\s+[a-zA-Z0-9+#]+)?)(?=\s+(?:by|due|upto|until)\b|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sub = _clean_subject(match.group(1))
                if sub:
                    return sub

    elif assignment_type == "presentation":
        patterns = [
            r"\b([a-zA-Z0-9+#]+(?:\s+[a-zA-Z0-9+#]+)?)\s+(?:presentation|slides?|ppt)\b",
            r"(?:presentation|slides?|ppt)\s+(?:about|on|regarding)\s+([a-zA-Z0-9+#]+(?:\s+[a-zA-Z0-9+#]+)?)(?=\s+(?:by|due|upto|until)\b|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sub = _clean_subject(match.group(1))
                if sub:
                    return sub

    elif assignment_type == "project":
        patterns = [
            r"\b([a-zA-Z0-9+#]+(?:\s+[a-zA-Z0-9+#]+)?)\s+(?:project|app|application|website)\b",
            r"(?:build|develop|create)\s+(?:a\s+|an\s+)?([a-zA-Z0-9+#]+(?:\s+[a-zA-Z0-9+#]+)?)(?=\s+(?:by|due|upto|until|project)\b|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sub = _clean_subject(match.group(1))
                if sub:
                    return sub

    return None


def analyze_assignment(
    text: str,
    start_date: Optional[date] = None,
) -> dict:

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

    start = start_date if start_date else date.today()
    total_days = (deadline - start).days + 1 if deadline else None

    # -----------------------------------------------------
    # Detect DAILY requirement
    # -----------------------------------------------------

    explicit_daily = bool(
        re.search(
            r"\b(?:daily|every\s+day|per\s+day|each\s+day)\b",
            lower_text,
        )
    )

    if explicit_daily:
        daily = True
    elif deadline and assignment_type == "study" and total_days and total_days > 2:
        # Multi-day study or practice routine up to a deadline
        daily = True
    else:
        daily = False

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
        "start_date": start,
        "total_days": total_days,
        "estimated_hours": estimated_hours,
    }
