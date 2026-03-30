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
Base parameter classes for common patterns across Gramps API operations.
"""

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

# Common choices for validation
PROFILE_CHOICES = [
    "all",
    "self",
    "families",
    "events",
    "age",
    "span",
    "ratings",
    "references",
]

EXTEND_CHOICES = [
    "all",
    "citation_list",
    "event_ref_list",
    "family_list",
    "media_list",
    "note_list",
    "parent_family_list",
    "person_ref_list",
    "primary_parent_family",
    "tag_list",
    "backlinks",
]


class BaseGetMultipleParams(BaseModel):
    """Common parameters for GET operations that return multiple objects."""

    gramps_id: Optional[str] = Field(
        None, description="An alternate user managed identifier"
    )
    page: Optional[int] = Field(
        None, description="Page number representing a subset of results"
    )
    pagesize: Optional[int] = Field(
        None, description="The number of items that constitute a page"
    )
    sort: Optional[str] = Field(
        None, description="Comma delimited list of keys to sort the result set by"
    )
    gql: Optional[str] = Field(
        None, description="A Gramps QL query string that is used to filter the objects"
    )
    backlinks: Optional[bool] = Field(
        None, description="Include handles to objects referring to the object"
    )
    extend: Optional[str] = Field(
        None, description="Enables the return of extended record information"
    )
    profile: Optional[str] = Field(
        None,
        description="Enables the return of summarized information about the object",
    )

    @field_validator("extend")
    @classmethod
    def validate_extend(cls, v):
        if v is not None:
            extend_list = [choice.strip() for choice in v.split(",")]
            for choice in extend_list:
                if choice not in EXTEND_CHOICES:
                    raise ValueError(
                        f"Invalid extend choice: {choice}. "
                        f"Must be one of {EXTEND_CHOICES}"
                    )
        return v

    @field_validator("profile")
    @classmethod
    def validate_profile(cls, v):
        if v is not None:
            profile_list = [choice.strip() for choice in v.split(",")]
            for choice in profile_list:
                if choice not in PROFILE_CHOICES:
                    raise ValueError(
                        f"Invalid profile choice: {choice}. "
                        f"Must be one of {PROFILE_CHOICES}"
                    )
        return v


class BaseGetSingleParams(BaseModel):
    """Common parameters for GET operations that return a single object."""

    backlinks: Optional[bool] = Field(
        None, description="Include handles to objects referring to the object"
    )
    extend: Optional[str] = Field(
        None, description="Enables the return of extended record information"
    )
    profile: Optional[str] = Field(
        None,
        description="Enables the return of summarized information about the object",
    )

    @field_validator("extend")
    @classmethod
    def validate_extend(cls, v):
        if v is not None:
            extend_list = [choice.strip() for choice in v.split(",")]
            for choice in extend_list:
                if choice not in EXTEND_CHOICES:
                    raise ValueError(
                        f"Invalid extend choice: {choice}. "
                        f"Must be one of {EXTEND_CHOICES}"
                    )
        return v

    @field_validator("profile")
    @classmethod
    def validate_profile(cls, v):
        if v is not None:
            profile_list = [choice.strip() for choice in v.split(",")]
            for choice in profile_list:
                if choice not in PROFILE_CHOICES:
                    raise ValueError(
                        f"Invalid profile choice: {choice}. "
                        f"Must be one of {PROFILE_CHOICES}"
                    )
        return v


class BaseDataModel(BaseModel):
    """Base class for data models used in POST/PUT operations."""

    handle: Optional[str] = Field(None, description="Object's unique handle identifier")
    gramps_id: Optional[str] = Field(
        None, description="An alternate user managed identifier"
    )
    note_list: Optional[List[str]] = Field(
        None, description="List of handles for notes"
    )
    media_list: Optional[List[Dict[str, Any]]] = Field(
        None,
        description=(
            "List of media references as dictionaries. Each reference requires 'ref' key with media handle. "
            "Example: [{'ref': 'media_handle_123'}, {'ref': 'another_handle', 'private': True}]. "
            "Optional keys: 'attribute_list' (array of attributes), 'citation_list' (citation handles), "
            "'note_list' (note handles), 'private' (boolean), 'rect' (rectangle [x,y,w,h] for media area). "
            "Common mistake: passing a string instead of dict—must be list of {dict}."
        ),
    )
    attribute_list: Optional[List[Dict[str, Any]]] = Field(
        None,
        description=(
            "List of attributes as dictionaries. Each attribute must have 'type' and 'value' keys. "
            "Example: [{'type': 'Social Security Number', 'value': '123-45-6789'}, "
            "{'type': 'National Origin', 'value': 'Scottish', 'private': True}]. "
            "Optional keys: 'citation_list' (array of citation handles), "
            "'note_list' (array of note handles), 'private' (boolean)"
        ),
    )

    @field_validator("attribute_list", mode="before")
    @classmethod
    def validate_attribute_list(cls, v: Any) -> Optional[List[Dict[str, Any]]]:
        """Validate that attribute_list items are dictionaries with required keys."""
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError(
                f"attribute_list must be a list of dictionaries, got {type(v).__name__}"
            )
        for i, item in enumerate(v):
            if isinstance(item, str):
                raise ValueError(
                    f"attribute_list[{i}]: Attribute must be a dictionary with 'type' and 'value' keys, "
                    f"not a string. Got '{item}'. "
                    f"Correct format: {{'type': 'AttributeType', 'value': 'value_here'}} "
                    f"or similar."
                )
            if not isinstance(item, dict):
                raise ValueError(
                    f"attribute_list[{i}]: Each attribute must be a dictionary, got {type(item).__name__}"
                )
            if "type" not in item:
                raise ValueError(
                    f"attribute_list[{i}]: Missing required 'type' key. "
                    f"Correct format: {{'type': 'AttributeType', 'value': 'value_here'}}"
                )
            if "value" not in item:
                raise ValueError(
                    f"attribute_list[{i}]: Missing required 'value' key. "
                    f"Correct format: {{'type': 'AttributeType', 'value': 'value_here'}}"
                )
        return v

    @field_validator("media_list", mode="before")
    @classmethod
    def validate_media_list(cls, v: Any) -> Optional[List[Dict[str, Any]]]:
        """Validate that media_list items are dictionaries with required 'ref' key."""
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError(
                f"media_list must be a list of dictionaries, got {type(v).__name__}"
            )
        for i, item in enumerate(v):
            if isinstance(item, str):
                raise ValueError(
                    f"media_list[{i}]: Media reference must be a dictionary with 'ref' key, "
                    f"not a string. Got '{item}'. "
                    f"Correct format: {{'ref': 'media_handle'}} or {{'ref': 'media_handle', 'private': True}}"
                )
            if not isinstance(item, dict):
                raise ValueError(
                    f"media_list[{i}]: Each media reference must be a dictionary, got {type(item).__name__}"
                )
            if "ref" not in item:
                raise ValueError(
                    f"media_list[{i}]: Missing required 'ref' key (media handle). "
                    f"Correct format: {{'ref': 'media_handle'}}"
                )
        return v

    @field_validator("tag_list", mode="before")
    @classmethod
    def coerce_tag_list(cls, v: Any) -> Optional[List[str]]:
        """
        Coerce tag_list to handle stringified list inputs.

        Accepted inputs:
        - None              → None
        - list of strings   → used as-is
        - stringified list  → parsed and converted to list
        - single string     → wrapped in a list
        """
        if v is None:
            return None

        if isinstance(v, str):
            # Try JSON decode first (e.g. agent may send "['handle1', 'handle2']" or '["handle1", "handle2"]')
            try:
                v = json.loads(v)
            except (json.JSONDecodeError, ValueError):
                # If not valid JSON, treat as a single tag handle
                return [v.strip()] if v.strip() else None

        if isinstance(v, list):
            # Ensure all items are strings
            result = []
            for item in v:
                if isinstance(item, str):
                    result.append(item)
                else:
                    raise ValueError(
                        f"tag_list items must be strings (tag handles), got {type(item).__name__}"
                    )
            return result if result else None

        raise ValueError(f"tag_list must be a list or string, got {type(v).__name__}")

    @field_validator("note_list", mode="before")
    @classmethod
    def coerce_note_list(cls, v: Any) -> Optional[List[str]]:
        """
        Coerce note_list to handle stringified list inputs.

        Accepted inputs:
        - None              → None
        - list of strings   → used as-is
        - stringified list  → parsed and converted to list
        - single string     → wrapped in a list
        """
        if v is None:
            return None

        if isinstance(v, str):
            # Try JSON decode first (e.g. agent may send "['handle1', 'handle2']" or '["handle1", "handle2"]')
            try:
                v = json.loads(v)
            except (json.JSONDecodeError, ValueError):
                # If not valid JSON, treat as a single note handle
                return [v.strip()] if v.strip() else None

        if isinstance(v, list):
            # Ensure all items are strings
            result = []
            for item in v:
                if isinstance(item, str):
                    result.append(item)
                else:
                    raise ValueError(
                        f"note_list items must be strings (note handles), got {type(item).__name__}"
                    )
            return result if result else None

        raise ValueError(f"note_list must be a list or string, got {type(v).__name__}")

    tag_list: Optional[List[str]] = Field(None, description="List of handles to tags")
    private: Optional[bool] = Field(None, description="Whether the object is private")
    change: Optional[int] = Field(
        None, description="Time in epoch format the record was last modified"
    )

    model_config = {"populate_by_name": True}
