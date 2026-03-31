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

import json
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

from .base_params import BaseDataModel, BaseGetMultipleParams, BaseGetSingleParams


class PlaceSearchParams(BaseGetMultipleParams):
    """Parameters for searching places."""

    pass


class PlaceDetailsParams(BaseGetSingleParams):
    """Parameters for getting specific place details."""

    pass


class PlaceSaveParams(BaseDataModel):
    """Parameters for creating or updating a place."""

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
    title: Optional[str] = Field(None, description="The full name of the place (e.g. 'Twin Falls, ID')")
    urls: Optional[List[dict]] = Field(
        None,
        description=(
            "Associated URLs as strings or dictionaries. Strings are converted to {'path': url_value}. "
            "Dict keys: 'path' (required when using dict), 'type', 'desc', 'private'. "
            "Examples: ['https://example.com'] or [{'path': 'https://example.com', 'type': 'Web Home'}]. "
            "Use get_types tool to see all valid URL types (listed under 'URL Types')."
        ),
    )

    @field_validator("urls", mode="before")
    @classmethod
    def normalise_urls(cls, v: Any) -> Optional[List[dict]]:
        """Coerce strings to dicts and normalise 'url' key to 'path'.
        
        Accepts either:
        - String URLs: converted to {'path': url_value}
        - Dict URLs: normalised if 'url' key exists (converted to 'path')
        """
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("urls must be a list")
        result = []
        for i, item in enumerate(v):
            if isinstance(item, str):
                # Coerce string to dict with 'path' key
                result.append({"path": item})
            elif isinstance(item, dict):
                # Normalise 'url' key to 'path' if needed
                if "url" in item and "path" not in item:
                    item = dict(item)
                    item["path"] = item.pop("url")
                result.append(item)
            else:
                raise ValueError(
                    f"urls[{i}]: Each URL must be a string or dictionary, got {type(item).__name__}"
                )
        return result

    @field_validator("name", mode="before")
    @classmethod
    def coerce_name(cls, v: Any) -> Optional[Dict[str, Any]]:
        """Accept a plain place name string and wrap it in the Gramps name object."""
        if isinstance(v, str):
            return {"value": v}
        return v
