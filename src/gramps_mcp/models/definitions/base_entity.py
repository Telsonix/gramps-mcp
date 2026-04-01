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
Base entity models for Gramps API objects.

This module provides reusable base classes for all primary entities in the Gramps database.
Entities can inherit from these classes to share common fields and behaviors:

- BaseEntity: Core identity and metadata fields (handle, gramps_id, _class, private, change).
- Referenceable: Extends BaseEntity; adds reference lists (citations, notes, tags, media).
- ExtendedEntity: Extends Referenceable; adds backlinks and extended dereferencing (generic type).
"""

import json
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .references import Backlinks

# Generic type variable for Extended fields (EventExtended, FamilyExtended, etc.)
ExtendedT = TypeVar("ExtendedT")


class BaseEntity(BaseModel):
    """
    Base class for all primary Gramps entities (Event, Family, Person, Place, etc.).

    Provides core identity and metadata fields shared across all entities.

    Attributes:
        handle: Unique database identifier (handle) for this object. Required field, typically 20-50
            alphanumeric characters. Examples: 'GNUJQCL9MD64AM56OH', 'EZUJQC8YM5EGRG868J'.
        gramps_id: User-managed alternate identifier (optional, usually unique but not guaranteed).
            Examples: 'P0001', 'F0002', 'E01658', 'S0000'. Useful for cross-reference with external systems.
        change: Unix epoch timestamp (seconds since 1970-01-01 00:00:00 UTC) indicating when this
            object record was last modified. Used for change tracking and synchronization.
        private: Privacy/confidentiality indicator. When True, this record should not be shared or
            published without explicit permission. Useful for protecting sensitive personal information.
        class_field: Object class identifier indicating the semantic type of this object.
            Expected values: 'Person', 'Family', 'Event', 'Place', 'Source', 'Citation', 'Repository',
            'Media', 'Note', 'Tag'. Aliased from '_class' in JSON payloads.

    Config:
        populate_by_name: Allow both field names and aliases in input (e.g., _class or class_field).
    """

    handle: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique database identifier (handle). Required, 1-50 characters. Examples: 'GNUJQCL9MD64AM56OH', 'P0001'.",
    )
    gramps_id: Optional[str] = Field(
        None,
        max_length=50,
        description="User-managed alternate identifier (optional). Examples: 'P0001', 'F0002', 'E01658'.",
    )
    change: Optional[float] = Field(
        None,
        description="Unix epoch timestamp of last modification (seconds since 1970-01-01). Example: 1431174904.",
    )
    private: Optional[bool] = Field(
        None,
        description="Privacy indicator. True = record is confidential; False or null = record is public.",
    )
    class_field: Optional[str] = Field(
        None,
        alias="_class",
        description="Object class name: 'Person', 'Family', 'Event', 'Place', 'Source', 'Citation', 'Repository', 'Media', 'Note', 'Tag'.",
    )

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("handle", mode="before")
    @classmethod
    def validate_handle(cls, v: Any) -> str:
        """Validate and coerce handle to non-empty string, max 50 chars."""
        if v is None:
            raise ValueError("handle is required (cannot be None)")
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            raise ValueError("handle cannot be empty or whitespace-only")
        if len(v) > 50:
            raise ValueError(f"handle exceeds maximum length of 50 characters (got {len(v)})")
        return v

    @field_validator("gramps_id", mode="before")
    @classmethod
    def validate_gramps_id(cls, v: Any) -> Optional[str]:
        """Validate and coerce gramps_id: optional, non-empty if provided, max 50 chars."""
        if v is None or v == "":
            return None
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            return None
        if len(v) > 50:
            raise ValueError(f"gramps_id exceeds maximum length of 50 characters (got {len(v)})")
        return v

    @field_validator("change", mode="before")
    @classmethod
    def validate_change(cls, v: Any) -> Optional[float]:
        """Validate and coerce change to float (Unix timestamp)."""
        if v is None or v == "":
            return None
        try:
            change_float = float(v)
            if change_float < 0:
                raise ValueError(f"change timestamp cannot be negative: {change_float}")
            return change_float
        except (TypeError, ValueError) as e:
            raise ValueError(f"change must be a valid Unix timestamp (float/int): {e}")

    @field_validator("private", mode="before")
    @classmethod
    def validate_private(cls, v: Any) -> Optional[bool]:
        """Validate and coerce private to bool."""
        if v is None or v == "":
            return None
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            v_lower = v.lower().strip()
            if v_lower in ("true", "1", "yes", "y"):
                return True
            elif v_lower in ("false", "0", "no", "n"):
                return False
            else:
                raise ValueError(f"private must be a boolean (got '{v}')")
        raise ValueError(f"private must be a boolean or coercible to bool (got {type(v).__name__})")

    @field_validator("class_field", mode="before")
    @classmethod
    def validate_class_field(cls, v: Any) -> Optional[str]:
        """Validate and coerce class_field to valid class name."""
        if v is None or v == "":
            return None
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            return None
        valid_classes = {"Person", "Family", "Event", "Place", "Source", "Citation", "Repository", "Media", "Note", "Tag"}
        if v not in valid_classes:
            raise ValueError(f"class_field must be one of {valid_classes}, got '{v}'")
        return v


class Referenceable(BaseEntity):
    """
    Extends BaseEntity with reference lists for citations, notes, tags, and media.

    Used for entities that can be cited, tagged, or have attached notes and media.

    Attributes:
        citation_list: List of handles (IDs) referencing Citation objects that provide evidence,
            sources, or citations for information contained in this object. Each handle is a string
            pointing to a Citation record. Empty list if no citations exist.
        note_list: List of handles referencing Note objects containing research notes, transcriptions,
            commentaries, or interpretations about this object. Empty list if no research notes attached.
        tag_list: List of handles referencing Tag objects used for categorization, marking, or
            organizational purposes. Empty list if not tagged.
        media_list: List of media handles or MediaReference objects attached to this object.
            Can be plain strings (handles) or structured objects with additional metadata. Contents
            vary by entity type (e.g., Person might have photo handles, Event might have document refs).
    """

    citation_list: Optional[List[str]] = Field(
        None,
        description="List of citation handles supporting this object. Each is a reference to a Citation record. Accepts: list of strings, single string, or JSON array string (e.g. '[\"handle1\", \"handle2\"]').",
    )
    note_list: Optional[List[str]] = Field(
        None,
        description="List of research note handles. Each is a reference to a Note record containing commentary or evidence. Accepts: list, single string, or JSON array string.",
    )
    tag_list: Optional[List[str]] = Field(
        None,
        description="List of tag handles for categorization. Each is a reference to a Tag record. Accepts: list, single string, or JSON array string.",
    )
    media_list: Optional[List] = Field(
        None,
        description="List of media handles or MediaReference objects. Can include photos, documents, digital files, etc. Accepts: list of strings/objects, single string, or JSON array string.",
    )

    @field_validator("citation_list", mode="before")
    @classmethod
    def validate_citation_list(cls, v: Any) -> Optional[List[str]]:
        """Validate and coerce citation_list: list of strings (handles), coerce single values."""
        return cls._validate_handle_list(v, "citation_list")

    @field_validator("note_list", mode="before")
    @classmethod
    def validate_note_list(cls, v: Any) -> Optional[List[str]]:
        """Validate and coerce note_list: list of strings (handles), coerce single values."""
        return cls._validate_handle_list(v, "note_list")

    @field_validator("tag_list", mode="before")
    @classmethod
    def validate_tag_list(cls, v: Any) -> Optional[List[str]]:
        """Validate and coerce tag_list: list of strings (handles), coerce single values."""
        return cls._validate_handle_list(v, "tag_list")

    @staticmethod
    def _validate_handle_list(v: Any, field_name: str) -> Optional[List[str]]:
        """
        Helper to validate handle lists: coerce single strings to list, ensure all items are strings.
        Supports JSON strings: '["handle1", "handle2"]' → ["handle1", "handle2"]
        """
        if v is None or v == "":
            return None

        # Attempt JSON parsing if input is a string that looks like JSON
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("["):
                try:
                    v = json.loads(v_stripped)
                except json.JSONDecodeError as e:
                    raise ValueError(f"{field_name}: Invalid JSON string: {e}")
            else:
                # Regular string handle, coerce to list
                v = [v_stripped]

        if not isinstance(v, list):
            raise ValueError(f"{field_name} must be a list of strings (handles), got {type(v).__name__}")

        # Validate all items are strings (handles)
        validated = []
        for i, item in enumerate(v):
            if isinstance(item, str):
                item = item.strip()
                if item:  # Only add non-empty items
                    validated.append(item)
            else:
                raise ValueError(f"{field_name}[{i}]: Each handle must be a string, got {type(item).__name__}")
        return validated if validated else None


class ExtendedEntity(Referenceable, Generic[ExtendedT]):
    """
    Extends Referenceable with backlinks and extended dereferencing (generic type).

    Used for entities that support full object dereferencing via an Extended model.
    Subclasses specify the Extended type parameter (e.g., Event[EventExtended]).

    Type Parameters:
        ExtendedT: The extended (dereferenced) version of this entity.

    Attributes:
        backlinks: Mapping of object types to lists of handles of objects that refer to this object.
            Allows bidirectional navigation: "What objects reference this one?" Structure: {'person': [handles],
            'family': [handles], ...}. Null if nothing refers to this object.
        extended: Full dereferenced version of this entity containing complete details of all
            referenced objects. Only populated on request (readOnly). Contains nested objects for
            citations, media, notes, tags, and backlinks with full details. Type varies by entity
            (PersonExtended, EventExtended, etc.).
    """

    backlinks: Optional[Backlinks] = Field(
        None,
        description="Mapping of object types to lists of handles referring to this object. Enables backreferences.",
    )
    extended: Optional[ExtendedT] = Field(
        None,
        description="Full dereferenced version with complete details of referenced objects. Read-only; type varies by entity.",
    )
