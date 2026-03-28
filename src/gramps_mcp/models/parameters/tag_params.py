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
Pydantic models for tag-related operations.

API calls supported in this category:
- GET_TAGS: Get information about multiple tags
- POST_TAGS: Add a new tag to the database
- GET_TAG: Get information about a specific tag
- PUT_TAG: Update the tag
- DELETE_TAG: Delete the tag
"""

from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator


class TagSearchParams(BaseModel):
    """
    Parameters for searching tags.
    
    Note: This endpoint does NOT support gramps_id, gql, backlinks, extend, profile.
    Only the fields below are valid.
    """

    @field_validator("page", mode="before")
    @classmethod
    def coerce_page(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce page to int."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return int(v)
        return v

    @field_validator("pagesize", mode="before")
    @classmethod
    def coerce_pagesize(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce pagesize to int."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return int(v)
        return v

    @field_validator("strip", mode="before")
    @classmethod
    def coerce_strip(cls, v: Union[bool, str, None]) -> Optional[bool]:
        """Coerce strip to bool."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v) if v is not None else None

    page: Optional[int] = Field(None, ge=0, description="Page number for pagination")
    pagesize: Optional[int] = Field(None, gt=0, description="Number of records per page")
    sort: Optional[str] = Field(None, description="Field to sort by")
    strip: Optional[bool] = Field(None, description="Strip empty values from results")
    keys: Optional[str] = Field(None, description="Return only specific fields")
    skipkeys: Optional[str] = Field(None, description="Omit specific fields")
    locale: Optional[str] = Field(None, description="Locale for localized data")


class TagSaveParams(BaseModel):
    """Parameters for creating or updating a tag."""

    handle: Optional[str] = Field(
        None, description="Tag's handle (for updates; omit for new tag)"
    )
    name: str = Field(description="Tag name", min_length=1)
    color: Optional[str] = Field(None, description="Tag color")
    priority: Optional[int] = Field(None, description="Tag priority")
    change: Optional[str] = Field(None, description="Change timestamp")
