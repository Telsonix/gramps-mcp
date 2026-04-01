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
Tag and Note model definitions for the Gramps API.

This module contains Tag objects for categorizing genealogical data,
and Note objects for storing research notes.
"""

import re
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

from .base_entity import BaseEntity, ExtendedEntity
from .core_types import StyledText
from .references import BacklinksExtended


class Tag(BaseEntity):
    """
    Represents a tag for categorizing and organizing genealogical objects.

    Inherits core identity and metadata from BaseEntity.

    Tags are used to group, mark, or label Gramps objects (people, families, events, etc.) for
    organizational, research, or workflow purposes. Each tag has a user-visible name, optional
    color for UI display, and optional priority for ordering.

    Attributes:
        name: Tag name/label (required). User-visible text used to identify the tag purpose.
            Examples: 'Research Needed', 'Verified', 'Photo Available', 'ToDo', 'Important'.
            Non-empty string, 1-100 characters, whitespace trimmed.
        color: Optional hex color code for UI display. Expected format: '#RRGGBB' or '#RRGGBBAA'
            (with or without alpha channel). Examples: '#FF0000' (red), '#00FF00' (green),
            '#0000FF80' (semi-transparent blue). Defaults to None (use application default color).
        priority: Optional integer for tag ordering/importance within tag lists. Positive integers
            recommended for sorting (e.g., 0-255 or 0-1000 depending on application). Lower numbers
            typically display first. Null if no priority-based ordering is needed.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Tag name/label (required). 1-100 characters, whitespace trimmed. Examples: 'Verified', 'Research Needed'.",
    )
    color: Optional[str] = Field(
        None,
        description="Hex color code for UI display. Format: '#RRGGBB' or '#RRGGBBAA'. Examples: '#FF0000', '#0000FF80'.",
    )
    priority: Optional[int] = Field(
        None,
        ge=0,
        le=1000,
        description="Integer priority for tag ordering. 0-1000 recommend. Lower numbers typically display first.",
    )

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: Any) -> str:
        """Validate and coerce name: required, non-empty, max 100 chars, trimmed."""
        if v is None or v == "":
            raise ValueError("name is required (cannot be None or empty)")
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty or whitespace-only")
        if len(v) > 100:
            raise ValueError(f"name exceeds maximum length of 100 characters (got {len(v)})")
        return v

    @field_validator("color", mode="before")
    @classmethod
    def validate_color(cls, v: Any) -> Optional[str]:
        """Validate and coerce color: optional hex color code (#RRGGBB or #RRGGBBAA)."""
        if v is None or v == "":
            return None
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v or v.lower() == "none":
            return None

        # Validate hex color format: #RRGGBB or #RRGGBBAA
        hex_color_pattern = r"^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$"
        if not re.match(hex_color_pattern, v):
            raise ValueError(
                f"color must be a valid hex color code (#RRGGBB or #RRGGBBAA), got '{v}'. "
                f"Examples: '#FF0000', '#0000FF80'."
            )
        # Normalize to uppercase for consistency
        return v.upper()

    @field_validator("priority", mode="before")
    @classmethod
    def validate_priority(cls, v: Any) -> Optional[int]:
        """Validate and coerce priority: optional integer 0-1000."""
        if v is None or v == "":
            return None
        try:
            priority_int = int(v)
            if priority_int < 0 or priority_int > 1000:
                raise ValueError(f"priority must be between 0 and 1000, got {priority_int}")
            return priority_int
        except (TypeError, ValueError) as e:
            raise ValueError(f"priority must be an integer 0-1000: {e}")


class NoteExtended(BaseModel):
    """
    Extended note data with fully dereferenced objects instead of just handles.

    Populated only when the extended query parameter is requested. Contains complete
    records for all objects referenced by the note.

    Attributes:
        tags: Full Tag records for each tag applied to this note.
        backlinks: Full records of all objects (people, events, families) that reference this note.
    """

    tags: Optional[List[Any]] = Field(None, description="Full Tag records for each tag applied to this note.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Full records of all objects (people, events, families, places) that reference this note.")


class Note(ExtendedEntity["NoteExtended"]):
    """
    Represents a research note in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Notes store researcher commentary, transcriptions, analysis, interpretations, source excerpts,
    or other textual information relevant to genealogical research. Each note has content (text),
    an optional type/category, and an optional format indicator.

    Attributes:
        text: Note content with optional rich text styling (StyledText object). Can be plain text
            or formatted text with markup/styling information. Empty or null if note has no content.
        type: Optional note type/category (string). Examples: 'Source text', 'Transcript', 'Research note',
            'Translation', 'Commentary', 'Analysis'. Non-empty if provided, max 50 characters.
        format: Note content format indicator (integer). Expected values: 0 (plain text, default),
            1 (Rich Text Format/RTF). Other values may be supported by extended implementations.
    """

    text: Optional[StyledText] = Field(
        None,
        description="Note content (StyledText). Can be plain or formatted text. Examples: transcriptions, research notes, source excerpts.",
    )
    type: Optional[str] = Field(
        None,
        max_length=50,
        description="Note type/category. Examples: 'Source text', 'Transcript', 'Research note'. Max 50 characters.",
    )
    format: Optional[int] = Field(
        None,
        ge=0,
        le=1,
        description="Content format: 0 = plain text (default), 1 = Rich Text Format (RTF).",
    )

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v: Any) -> Optional[str]:
        """Validate and coerce type: optional, non-empty if provided, max 50 chars, trimmed."""
        if v is None or v == "":
            return None
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            return None
        if len(v) > 50:
            raise ValueError(f"type exceeds maximum length of 50 characters (got {len(v)})")
        return v

    @field_validator("format", mode="before")
    @classmethod
    def validate_format(cls, v: Any) -> Optional[int]:
        """Validate and coerce format: optional, must be 0 (plain) or 1 (RTF)."""
        if v is None or v == "":
            return None
        try:
            fmt = int(v)
            if fmt not in (0, 1):
                raise ValueError(f"format must be 0 (plain text) or 1 (RTF), got {fmt}")
            return fmt
        except (TypeError, ValueError) as e:
            raise ValueError(f"format must be an integer 0 or 1: {e}")
