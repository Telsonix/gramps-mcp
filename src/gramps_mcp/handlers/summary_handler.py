# gramps-mcp - AI-Powered Genealogy Research & Management
# Copyright (C) 2025 cabout.me
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Summary formatters for search result display.

These are pure synchronous functions that operate on the dict already returned
by list API responses. They make zero extra API calls and produce 1-3 lines of
output per record. Used by all search/find tools so that only get_entity
triggers full detail fetching.
"""

from .date_handler import format_date


def _person_name(primary_name: dict) -> str:
    """Extract 'Given Surname' from a primary_name dict."""
    given = primary_name.get("first_name", "")
    surnames = primary_name.get("surname_list", [])
    surname = surnames[0].get("surname", "") if surnames else ""
    return f"{given} {surname}".strip() or "Unknown"


def _gender_letter(gender) -> str:
    """Convert gender int (0=F, 1=M, 2=U) to single letter."""
    return {0: "F", 1: "M", 2: "U"}.get(gender, "U")


def _confidence_label(level) -> str:
    """Convert confidence int to label."""
    return {0: "Very Low", 1: "Low", 2: "Normal", 3: "High", 4: "Very High"}.get(
        int(level) if level is not None else 2, "Normal"
    )


# ---------------------------------------------------------------------------
# Public summary formatters — each returns a single newline-terminated string
# ---------------------------------------------------------------------------


def format_person_summary(obj: dict) -> str:
    """
    Format a person record as a compact summary line.

    Args:
        obj (dict): Person object dict from list API response.

    Returns:
        str: 1-3 line summary.
    """
    gramps_id = obj.get("gramps_id", "")
    handle = obj.get("handle", "")
    gender = _gender_letter(obj.get("gender", 2))

    primary_name = obj.get("primary_name", {})
    name = _person_name(primary_name) if primary_name else "Unknown"

    line = f"{name} ({gender}) - {gramps_id} - [{handle}]"

    # Birth/death — prefer profile fields if present (returned by search API),
    # otherwise fall back to indexed event refs in extended data
    birth_str = obj.get("birth_year", "") or obj.get("profile", {}).get("birth_year", "")
    death_str = obj.get("death_year", "") or obj.get("profile", {}).get("death_year", "")

    # Try extended events if profile fields absent
    if not birth_str or not death_str:
        extended = obj.get("extended", {})
        events = extended.get("events", [])
        birth_ref = obj.get("birth_ref_index", -1)
        death_ref = obj.get("death_ref_index", -1)

        if not birth_str and birth_ref >= 0 and birth_ref < len(events):
            birth_str = format_date(events[birth_ref].get("date", {}))
            if birth_str == "date unknown":
                birth_str = ""

        if not death_str and death_ref >= 0 and death_ref < len(events):
            death_str = format_date(events[death_ref].get("date", {}))
            if death_str == "date unknown":
                death_str = ""

    result = line + "\n"
    if birth_str:
        result += f"  Born: {birth_str}\n"
    if death_str:
        result += f"  Died: {death_str}\n"

    return result


def format_family_summary(obj: dict) -> str:
    """
    Format a family record as a compact summary line.

    Args:
        obj (dict): Family object dict from list API response.

    Returns:
        str: 1-3 line summary.
    """
    gramps_id = obj.get("gramps_id", "")
    handle = obj.get("handle", "")

    extended = obj.get("extended", {})

    father = extended.get("father") or {}
    mother = extended.get("mother") or {}

    father_name = _person_name(father.get("primary_name", {})) if father else ""
    mother_name = _person_name(mother.get("primary_name", {})) if mother else ""

    if father_name and mother_name:
        members = f"{father_name} & {mother_name}"
    elif father_name:
        members = father_name
    elif mother_name:
        members = mother_name
    else:
        members = "Unknown"

    result = f"{members} - {gramps_id} - [{handle}]\n"

    # Marriage event (first match in event_ref_list / extended.events)
    events = extended.get("events", [])
    event_ref_list = obj.get("event_ref_list", [])
    for i, event_ref in enumerate(event_ref_list):
        if i < len(events):
            event = events[i]
            if str(event.get("type", "")).lower() == "marriage":
                date_str = format_date(event.get("date", {}))
                if date_str and date_str != "date unknown":
                    result += f"  Married: {date_str}\n"
                break

    return result


def format_event_summary(obj: dict) -> str:
    """
    Format an event record as a compact summary line.

    Args:
        obj (dict): Event object dict from list API response.

    Returns:
        str: 1-2 line summary.
    """
    gramps_id = obj.get("gramps_id", "")
    handle = obj.get("handle", "")
    event_type = obj.get("type", "Event")
    if isinstance(event_type, dict):
        event_type = event_type.get("string", "Event")

    date_str = format_date(obj.get("date", {}))
    place_handle = obj.get("place", "")
    description = obj.get("description", "")

    parts = [event_type]
    if date_str and date_str != "date unknown":
        parts.append(date_str)
    if description:
        parts.append(description[:60])

    line = " - ".join(parts) + f" - {gramps_id} - [{handle}]"
    result = line + "\n"

    if place_handle and not isinstance(place_handle, dict):
        # place_handle is just a handle string — note it without extra API call
        result += f"  Place handle: [{place_handle}]\n"

    return result


def format_place_summary(obj: dict) -> str:
    """
    Format a place record as a compact summary line.

    Args:
        obj (dict): Place object dict from list API response.

    Returns:
        str: 1 line summary.
    """
    gramps_id = obj.get("gramps_id", "")
    handle = obj.get("handle", "")

    place_type = obj.get("place_type", {})
    if isinstance(place_type, dict):
        place_type = place_type.get("string", "Place")
    if not place_type:
        place_type = "Place"

    # Primary name
    name_list = obj.get("name", []) if isinstance(obj.get("name"), list) else []
    if name_list:
        primary_name = name_list[0].get("value", "") if isinstance(name_list[0], dict) else str(name_list[0])
    else:
        primary_name = obj.get("name", {}).get("value", "") if isinstance(obj.get("name"), dict) else ""

    if not primary_name:
        primary_name = obj.get("title", "") or gramps_id

    return f"{place_type}: {primary_name} - {gramps_id} - [{handle}]\n"


def format_source_summary(obj: dict) -> str:
    """
    Format a source record as a compact summary line.

    Args:
        obj (dict): Source object dict from list API response.

    Returns:
        str: 1 line summary.
    """
    gramps_id = obj.get("gramps_id", "")
    handle = obj.get("handle", "")
    title = obj.get("title", "") or "Untitled"
    author = obj.get("author", "")

    line = title
    if author:
        line += f", {author}"
    line += f" - {gramps_id} - [{handle}]"
    return line + "\n"


def format_citation_summary(obj: dict) -> str:
    """
    Format a citation record as a compact summary line.

    Args:
        obj (dict): Citation object dict from list API response.

    Returns:
        str: 1-2 line summary.
    """
    gramps_id = obj.get("gramps_id", "")
    handle = obj.get("handle", "")
    page = obj.get("page", "")
    confidence = _confidence_label(obj.get("confidence", 2))

    # Source title from extended if available
    extended = obj.get("extended", {})
    source = extended.get("source", {}) if extended else {}
    source_title = source.get("title", "") if source else ""

    parts = []
    if source_title:
        parts.append(source_title[:60])
    if page:
        parts.append(f"p.{page}")
    parts.append(confidence)

    line = ", ".join(parts) + f" - {gramps_id} - [{handle}]"
    return line + "\n"


def format_media_summary(obj: dict) -> str:
    """
    Format a media record as a compact summary line.

    Args:
        obj (dict): Media object dict from list API response.

    Returns:
        str: 1 line summary.
    """
    gramps_id = obj.get("gramps_id", "")
    handle = obj.get("handle", "")
    desc = obj.get("desc", "") or "Media"
    mime = obj.get("mime", "")

    line = desc[:60]
    if mime:
        line += f" ({mime})"
    line += f" - {gramps_id} - [{handle}]"
    return line + "\n"


def format_note_summary(obj: dict) -> str:
    """
    Format a note record as a compact summary line.

    Args:
        obj (dict): Note object dict from list API response.

    Returns:
        str: 1 line summary.
    """
    gramps_id = obj.get("gramps_id", "")
    handle = obj.get("handle", "")

    note_type = obj.get("type", "Note")
    if isinstance(note_type, dict):
        note_type = note_type.get("string", "Note")

    text_field = obj.get("text", "")
    if isinstance(text_field, dict):
        text_field = text_field.get("string", "")
    text = str(text_field)[:120]
    if len(str(obj.get("text", ""))) > 120:
        text += "…"

    return f"{note_type}: {text} - {gramps_id} - [{handle}]\n"


def format_repository_summary(obj: dict) -> str:
    """
    Format a repository record as a compact summary line.

    Args:
        obj (dict): Repository object dict from list API response.

    Returns:
        str: 1 line summary.
    """
    gramps_id = obj.get("gramps_id", "")
    handle = obj.get("handle", "")

    repo_type = obj.get("type", {})
    if isinstance(repo_type, dict):
        repo_type = repo_type.get("string", "Repository")
    if not repo_type:
        repo_type = "Repository"

    name = obj.get("name", "") or gramps_id

    return f"{repo_type}: {name} - {gramps_id} - [{handle}]\n"


# Dispatch map — maps entity type string to summary formatter
SUMMARY_FORMATTERS = {
    "person": format_person_summary,
    "family": format_family_summary,
    "event": format_event_summary,
    "place": format_place_summary,
    "source": format_source_summary,
    "citation": format_citation_summary,
    "media": format_media_summary,
    "note": format_note_summary,
    "repository": format_repository_summary,
}


def format_summary(entity_type: str, obj: dict) -> str:
    """
    Dispatch to the correct summary formatter by entity type string.

    Args:
        entity_type (str): Entity type key (e.g. 'person', 'family').
        obj (dict): Entity object dict.

    Returns:
        str: Formatted summary line(s).
    """
    formatter = SUMMARY_FORMATTERS.get(entity_type.lower())
    if formatter:
        return formatter(obj)
    # Fallback for unknown types
    gramps_id = obj.get("gramps_id", "N/A")
    handle = obj.get("handle", "")
    title = obj.get("title", "") or obj.get("desc", "") or entity_type.title()
    return f"{title} - {gramps_id} - [{handle}]\n"
