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
Pydantic models for event-related operations.

API calls supported in this category:
- GET_EVENTS: Get information about multiple events
- POST_EVENTS: Add a new event to the database
- GET_EVENT: Get information about a specific event
- PUT_EVENT: Update the event
- DELETE_EVENT: Delete the event
- GET_EVENT_SPAN: Get elapsed time span between two events
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

from .base_params import BaseGetMultipleParams


def _coerce_date(value: Union[str, Dict[str, Any], None]) -> Optional[Dict[str, Any]]:
    """
    Convert a plain date string to a Gramps Date object dict.

    Accepts:
        "1850"           -> year only
        "1850-06"        -> year + month
        "1850-06-15"     -> full date

    Args:
        value: Plain date string or already-constructed date dict.

    Returns:
        Gramps Date object dict, or None if value is None.
    """
    if value is None or isinstance(value, dict):
        return value
    parts = str(value).strip().split("-")
    year = int(parts[0]) if len(parts) >= 1 and parts[0] else 0
    month = int(parts[1]) if len(parts) >= 2 else 0
    day = int(parts[2]) if len(parts) >= 3 else 0
    return {"dateval": [day, month, year, False], "quality": 0, "modifier": 0}


class EventSearchParams(BaseGetMultipleParams):
    """Parameters for searching multiple events."""

    dates: Optional[str] = Field(
        None, description="Date filter (y/m/d, -y/m/d, y/m/d-y/m/d, y/m/d-)"
    )


class EventSaveParams(BaseModel):
    """Parameters for creating or updating an event."""

    handle: Optional[str] = Field(
        None, description="Event's handle (for updates; omit for new event)"
    )
    type: str = Field(
        description=(
            "Event type string, e.g. 'Birth', 'Death', 'Marriage', 'Burial', "
            "'Divorce', 'Emigration', 'Immigration', 'Graduation', 'Occupation'. "
            "Use get_types tool for the full list."
        )
    )
    date: Optional[Union[str, Dict[str, Any]]] = Field(
        None,
        description=(
            "Event date. Can be a plain string ('1850', '1850-06', '1850-06-15') "
            "or a full Gramps Date object: "
            "{\"dateval\": [day, month, year, false], \"quality\": 0, \"modifier\": 0} "
            "where quality 0=regular/1=estimated/2=calculated and "
            "modifier 0=regular/1=before/2=after/3=about."
        ),
    )
    description: Optional[str] = Field(None, description="Event description")
    place: Optional[str] = Field(None, description="Place handle where event occurred")
    citation_list: Optional[List[str]] = Field(
        None, description="List of citation handles (optional)"
    )
    note_list: Optional[List[str]] = Field(None, description="List of note handles")

    @field_validator("date", mode="before")
    @classmethod
    def coerce_date(cls, v: Any) -> Optional[Dict[str, Any]]:
        """Accept plain date strings and convert to Gramps Date object."""
        return _coerce_date(v)


class EventSpanParams(BaseModel):
    """Parameters for getting elapsed time span between two events."""

    handle1: str = Field(description="The unique identifier for the first event")
    handle2: str = Field(description="The unique identifier for the second event")
    as_age: Optional[bool] = Field(None, description="Return result as an age")
    precision: Optional[int] = Field(
        None, ge=1, le=3, description="Number of significant levels (1-3)"
    )
