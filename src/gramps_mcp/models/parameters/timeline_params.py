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
Timeline parameter models for the Gramps Web API.
"""

from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator


def _coerce_bool(v: Union[bool, str, None]) -> Optional[bool]:
    """Helper to coerce value to bool."""
    if v is None or v == "":
        return None
    if isinstance(v, str):
        return v.lower() in ("true", "1", "yes", "on")
    return bool(v) if v is not None else None


def _coerce_int(v: Union[int, str, None]) -> Optional[int]:
    """Helper to coerce value to int."""
    if v is None or v == "":
        return None
    if isinstance(v, str):
        return int(v)
    return v


class PeopleTimelineParams(BaseModel):
    """
    Parameters for getting the timeline for a group of people.

    Note: This endpoint does NOT support gramps_id, sort, gql, backlinks, extend, profile.
    
    Args:
        anchor: Handle of a person to anchor the timeline.
        dates: Date range to bound the timeline (formats: -y/m/d, y/m/d-y/m/d, y/m/d-).
        first: Whether events prior to anchor person's first event should be included.
        last: Whether events after anchor person's last event should be included.
        handles: Comma delimited list of handles for specific people.
        filter: Use named filter for complex queries.
        rules: JSON filter expressions for custom filtering.
        events: Comma delimited list of specific events to include.
        event_classes: Comma delimited list of event classes to include.
        ratings: Whether to include citation count and confidence score.
        precision: Number of significant levels for date representation (1-3).
        discard_empty: Whether to discard undated events.
        locale: Locale for localized data.
        page: Page number for pagination.
        pagesize: Number of records per page.
        strip: Strip empty values from results.
        keys: Return only specific fields.
        skipkeys: Omit specific fields.
    """

    @field_validator("first", "last", "ratings", "discard_empty", "strip", mode="before")
    @classmethod
    def coerce_bool_fields(cls, v: Union[bool, str, None]) -> Optional[bool]:
        """Coerce boolean fields."""
        return _coerce_bool(v)

    @field_validator("precision", mode="before")
    @classmethod
    def coerce_precision(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce precision to int."""
        return _coerce_int(v)

    @field_validator("page", mode="before")
    @classmethod
    def coerce_page(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce page to int."""
        return _coerce_int(v)

    @field_validator("pagesize", mode="before")
    @classmethod
    def coerce_pagesize(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce pagesize to int."""
        return _coerce_int(v)

    anchor: Optional[str] = None
    dates: Optional[str] = None
    first: bool = True
    last: bool = True
    handles: Optional[str] = None
    filter: Optional[str] = None
    rules: Optional[str] = None
    events: Optional[str] = None
    event_classes: Optional[str] = None
    ratings: bool = False
    precision: int = Field(default=1, ge=1, le=3)
    discard_empty: bool = True
    locale: Optional[str] = None
    page: Optional[int] = Field(None, ge=0)
    pagesize: Optional[int] = Field(None, gt=0)
    strip: Optional[bool] = None
    keys: Optional[str] = None
    skipkeys: Optional[str] = None


class FamiliesTimelineParams(BaseModel):
    """
    Parameters for getting the timeline for all people in a group of families.

    Note: This endpoint does NOT support gramps_id, sort, gql, backlinks, extend, profile.
    
    Args:
        handles: Comma delimited list of handles for specific families.
        dates: Date range to bound the timeline (formats: -y/m/d, y/m/d-y/m/d, y/m/d-).
        filter: Use named filter for complex queries.
        rules: JSON filter expressions for custom filtering.
        events: Comma delimited list of specific events to include.
        event_classes: Comma delimited list of event classes to include.
        ratings: Whether to include citation count and confidence score.
        discard_empty: Whether to discard undated events.
        locale: Locale for localized data.
        page: Page number for pagination.
        pagesize: Number of records per page.
        strip: Strip empty values from results.
        keys: Return only specific fields.
        skipkeys: Omit specific fields.
    """

    @field_validator("ratings", "discard_empty", "strip", mode="before")
    @classmethod
    def coerce_bool_fields(cls, v: Union[bool, str, None]) -> Optional[bool]:
        """Coerce boolean fields."""
        return _coerce_bool(v)

    @field_validator("page", mode="before")
    @classmethod
    def coerce_page(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce page to int."""
        return _coerce_int(v)

    @field_validator("pagesize", mode="before")
    @classmethod
    def coerce_pagesize(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce pagesize to int."""
        return _coerce_int(v)

    handles: Optional[str] = None
    dates: Optional[str] = None
    filter: Optional[str] = None
    rules: Optional[str] = None
    events: Optional[str] = None
    event_classes: Optional[str] = None
    ratings: bool = False
    discard_empty: bool = True
    locale: Optional[str] = None
    page: Optional[int] = Field(None, ge=0)
    pagesize: Optional[int] = Field(None, gt=0)
    strip: Optional[bool] = None
    keys: Optional[str] = None
    skipkeys: Optional[str] = None
