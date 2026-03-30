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
Pydantic models for place-related operations.

API calls supported in this category:
- GET_PLACES: Get information about multiple places
- POST_PLACES: Add a new place to the database
- GET_PLACE: Get information about a specific place
- PUT_PLACE: Update the place
- DELETE_PLACE: Delete the place
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

from .base_params import BaseGetMultipleParams, BaseGetSingleParams


class PlaceSearchParams(BaseGetMultipleParams):
    """Parameters for searching places."""

    pass


class PlaceDetailsParams(BaseGetSingleParams):
    """Parameters for getting specific place details."""

    pass


class PlaceSaveParams(BaseModel):
    """Parameters for creating or updating a place."""

    handle: Optional[str] = Field(
        None, min_length=8, description="Place handle (for updates; omit for new place)"
    )
    gramps_id: Optional[str] = Field(
        None, description="Alternate user managed identifier"
    )
    name: Optional[Union[str, Dict[str, Any]]] = Field(
        None,
        description=(
            "Place name. Can be a plain string ('London') or a Gramps name object "
            "{\"value\": \"London\"}. Plain strings are automatically converted."
        ),
    )
    code: Optional[str] = Field(None, description="Place code")
    alt_loc: Optional[List[dict]] = Field(None, description="Alternative locations")
    place_type: str = Field(
        ...,
        description=(
            "Place type string, e.g. 'City', 'Country', 'County', 'State', "
            "'Province', 'Region', 'Parish', 'Town', 'Village', 'Address', "
            "'District', 'Borough', 'Municipality', 'Hamlet', 'Farm', "
            "'Unknown'. Use get_types tool for full list."
        ),
    )
    placeref_list: Optional[List[dict]] = Field(
        None, description="List of place references"
    )
    alt_names: Optional[List[str]] = Field(None, description="Alternative names")
    lat: Optional[str] = Field(None, description="Latitude coordinate")
    long: Optional[str] = Field(None, description="Longitude coordinate")
    urls: Optional[List[dict]] = Field(
        None,
        description="Associated URLs as dicts with 'path', 'type', 'desc'. Use 'path' for the URL value. Use get_types tool to see all valid URL types (listed under 'URL Types').",
    )

    @field_validator("urls", mode="before")
    @classmethod
    def normalise_urls(cls, v: Any) -> Optional[List[dict]]:
        """Normalise 'url' key to 'path' to match the Gramps API schema."""
        if v is None or not isinstance(v, list):
            return v
        result = []
        for item in v:
            if isinstance(item, dict) and "url" in item and "path" not in item:
                item = dict(item)
                item["path"] = item.pop("url")
            result.append(item)
        return result
    media_list: Optional[List[str]] = Field(None, description="List of media handles")
    citation_list: Optional[List[str]] = Field(
        None, description="List of citation handles"
    )
    note_list: Optional[List[str]] = Field(None, description="List of note handles")
    tag_list: Optional[List[str]] = Field(None, description="List of tag handles")
    private: Optional[bool] = Field(None, description="Mark as private")

    @field_validator("name", mode="before")
    @classmethod
    def coerce_name(cls, v: Any) -> Optional[Dict[str, Any]]:
        """Accept a plain place name string and wrap it in the Gramps name object."""
        if isinstance(v, str):
            return {"value": v}
        return v
