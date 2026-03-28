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
Pydantic models for people-related operations.

API calls supported in this category:
- GET_PEOPLE: Get information about multiple people
- POST_PEOPLE: Add a new person to the database
- GET_PERSON: Get information about a specific person
- PUT_PERSON: Update the person
- DELETE_PERSON: Delete the person
- GET_PERSON_TIMELINE: Get the timeline for a specific person
- GET_PERSON_DNA_MATCHES: Get DNA matches for a specific person
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

from .base_params import BaseDataModel

_GENDER_MAP = {
    "female": 0,
    "f": 0,
    "male": 1,
    "m": 1,
    "unknown": 2,
    "u": 2,
    "other": 2,
}


def _build_name_object(value: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convert a plain name string into a Gramps Name object dict.

    Splits on whitespace: last token becomes the surname, everything before
    it becomes first_name.  If only one token is given it is used as surname.

    Args:
        value: Either a full name string (e.g. "John Smith") or an already
               constructed name dict.

    Returns:
        Dict[str, Any]: A Gramps-compatible Name object.
    """
    if isinstance(value, dict):
        return value
    parts = value.strip().split()
    if len(parts) > 1:
        first_name = " ".join(parts[:-1])
        surname = parts[-1]
    else:
        first_name = ""
        surname = parts[0] if parts else ""
    return {
        "first_name": first_name,
        "surname_list": [{"surname": surname, "primary": True}],
        "type": "Birth Name",
    }


class EventReference(BaseModel):
    """Model for event references in a person's event_ref_list."""

    ref: str = Field(..., description="The handle of the event referenced")
    role: str = Field(..., description="Role of the person in the event")


class PersonData(BaseDataModel):
    """Model for creating or updating a person in Gramps API."""

    primary_name: Union[str, Dict[str, Any]] = Field(
        ...,
        description=(
            "Person's primary name. Can be a plain string like 'John Smith' "
            "(last word becomes the surname) or a full Gramps Name object dict "
            "with first_name and surname_list."
        ),
    )
    gender: Union[int, str] = Field(
        ...,
        description=(
            "Gender: integer (0=Female, 1=Male, 2=Unknown) or string "
            "('Female', 'Male', 'Unknown')"
        ),
    )

    @field_validator("primary_name", mode="before")
    @classmethod
    def coerce_primary_name(cls, v: Any) -> Dict[str, Any]:
        """Accept a plain name string and build a proper Name object."""
        return _build_name_object(v)

    @field_validator("gender", mode="before")
    @classmethod
    def coerce_gender(cls, v: Any) -> int:
        """Accept string gender labels and convert to Gramps integer codes."""
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            mapped = _GENDER_MAP.get(v.lower())
            if mapped is not None:
                return mapped
            raise ValueError(
                f"Invalid gender '{v}'. Use 'Male', 'Female', or 'Unknown' (or 0/1/2)."
            )
        raise ValueError(f"gender must be an int or string, got {type(v)}")
    alternate_names: Optional[List[Dict[str, Any]]] = Field(
        None,
        description=(
            "List of alternate names (married names, maiden names, etc). "
            "Each name should have the same structure as primary_name with "
            "first_name, surname_list, and type (e.g., 'Married Name', 'Birth Name')"
        ),
    )
    event_ref_list: Optional[List[EventReference]] = Field(
        None, description="List of references to events the person participated in"
    )
    family_list: Optional[List[str]] = Field(
        None, description="List of handles for families the person was a parent of"
    )
    parent_family_list: Optional[List[str]] = Field(
        None, description="List of handles for families of the person's parents"
    )
    urls: Optional[List[Dict[str, Any]]] = Field(
        None, description="List of URLs associated with the person"
    )


class PersonTimelineParams(BaseModel):
    """Parameters for getting a person's timeline from Gramps API.
    
    Note: This endpoint does NOT support gramps_id, sort, gql, backlinks, extend, profile.
    """

    @field_validator("first", "last", "ratings", "discard_empty", "omit_anchor", "strip", mode="before")
    @classmethod
    def coerce_bool_fields(cls, v: Union[bool, str, None]) -> Optional[bool]:
        """Coerce boolean fields."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v) if v is not None else None

    @field_validator("ancestors", "offspring", "precision", "page", "pagesize", mode="before")
    @classmethod
    def coerce_int_fields(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce integer fields."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return int(v)
        return v

    dates: Optional[str] = Field(
        None,
        description=(
            "Date range to bound the timeline (e.g., -y/m/d, y/m/d-y/m/d, y/m/d-)"
        ),
    )
    first: Optional[bool] = Field(
        None, description="Discard events dated prior to the first event for the person"
    )
    last: Optional[bool] = Field(
        None, description="Discard events dated after the last event for the person"
    )
    ancestors: Optional[int] = Field(
        None, ge=0, description="Number of generations of ancestors to consider"
    )
    offspring: Optional[int] = Field(
        None, ge=0, description="Number of generations of offspring to consider"
    )
    events: Optional[str] = Field(
        None, description="Comma delimited list of specific events to include"
    )
    event_classes: Optional[str] = Field(
        None, description="Comma delimited list of event classes to include"
    )
    relatives: Optional[str] = Field(
        None, description="Comma delimited list of relationship types to consider"
    )
    relative_events: Optional[str] = Field(
        None, description="Comma delimited list of events for relatives"
    )
    relative_event_classes: Optional[str] = Field(
        None, description="Comma delimited list of event classes for relatives"
    )
    ratings: Optional[bool] = Field(
        None, description="Include citation count and highest confidence score"
    )
    precision: Optional[int] = Field(
        None,
        ge=1,
        le=3,
        description="Number of significant levels for date representation",
    )
    discard_empty: Optional[bool] = Field(None, description="Discard undated events")
    omit_anchor: Optional[bool] = Field(
        None, description="Omit person info for events pertaining to that person"
    )
    locale: Optional[str] = Field(None, description="Locale for localized data")
    strip: Optional[bool] = Field(None, description="Strip empty values from results")
    keys: Optional[str] = Field(None, description="Return only specific fields")
    skipkeys: Optional[str] = Field(None, description="Omit specific fields")
    page: Optional[int] = Field(None, ge=0, description="Page number for pagination")
    pagesize: Optional[int] = Field(None, gt=0, description="Number of records per page")


class PersonDnaMatchesParams(BaseModel):
    """Parameters for getting DNA matches for a person from Gramps API."""

    raw: Optional[bool] = Field(None, description="Include raw data for the matches")
