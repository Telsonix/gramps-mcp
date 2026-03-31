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
Place model definitions for the Gramps API.

This module contains the Place primary object and related models including
PlaceReference, PlaceExtended, PlaceName, and PlaceProfile.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field

from .base_entity import ExtendedEntity
from .core_types import Date, Location, URL
from .references import BacklinksExtended


class PlaceName(BaseModel):
    """
    Represents an alternate name for a place.

    Attributes:
        value: The name in use.
        date: Date the place name was in use.
        lang: Language the name is in.
    """

    value: Optional[str] = Field(None, description="The name in use.")
    date: Optional[Date] = Field(None, description="Date the place name was in use.")
    lang: Optional[str] = Field(None, description="Language the name is in.")


class PlaceReference(BaseModel):
    """
    A reference to another place.

    Attributes:
        ref: Handle of the referenced place.
        date: Date of the reference.
    """

    ref: str = Field(..., description="Handle of the referenced place.")
    date: Optional[Date] = Field(None, description="Date of the reference.")


class Place(ExtendedEntity["PlaceExtended"]):
    """
    Represents a place in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Attributes:
        title: The full name of the place.
        name: The place name.
        place_type: The type of place (e.g., 'City', 'Country').
        code: Code identifier for the place.
        lat: Latitude coordinate.
        long: Longitude coordinate.
        alt_names: Alternate names for the place.
        alt_loc: Alternate locations for the place.
        placeref_list: References to other places.
        urls: URLs associated with the place.
        profile: Summary profile information.
    """

    title: Optional[str] = Field(None, description="The full name of the place.")
    name: Optional[PlaceName] = Field(None, description="The place name.")
    place_type: Optional[str] = Field(None, description="The type of place.")
    code: Optional[str] = Field(None, description="Code.")
    lat: Optional[str] = Field(None, description="Latitude.")
    long: Optional[str] = Field(None, description="Longitude.")
    alt_names: Optional[List[PlaceName]] = Field(None, description="Alternate names for the place.")
    alt_loc: Optional[List[Location]] = Field(None, description="Alternate locations for the place.")
    placeref_list: Optional[List[PlaceReference]] = Field(None, description="References to other places.")
    urls: Optional[List[URL]] = Field(None, description="URLs associated with the place.")
    profile: Optional[Any] = Field(None, description="Summary profile information.")


class PlaceExtended(BaseModel):
    """
    Extended place data with full details of all referenced objects.

    Attributes:
        citations: Citation records for any referenced citations.
        media: Media records for any referenced media objects.
        notes: Note records for any referenced notes.
        tags: Tag records for any referenced tags.
        backlinks: Objects referring to this place (extended).
    """

    citations: Optional[List[Any]] = Field(None, description="Citation records for referenced citations.")
    media: Optional[List[Any]] = Field(None, description="Media records for referenced media objects.")
    notes: Optional[List[Any]] = Field(None, description="Note records for referenced notes.")
    tags: Optional[List[Any]] = Field(None, description="Tag records for referenced tags.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Objects referring to this place (extended).")


class PlaceProfile(BaseModel):
    """
    Profile summary of a place with geographic and hierarchy information.

    Attributes:
        name: The place title.
        gramps_id: Alternate user-managed identifier.
        lat: Geographic latitude as a float.
        long: Geographic longitude as a float.
        alternate_names: Alternative names of the place.
        alternate_place_names: Alternative names with dates.
        parent_places: List of parent places.
        direct_parent_places: Direct parent places with dates.
        references: References from other objects.
    """

    name: Optional[str] = Field(None, description="The place title.")
    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier.")
    lat: Optional[float] = Field(None, description="Geographic latitude as a float.")
    long: Optional[float] = Field(None, description="Geographic longitude as a float.")
    alternate_names: Optional[List[str]] = Field(None, description="Alternative names of the place.")
    alternate_place_names: Optional[List[Any]] = Field(None, description="Alternative names with dates.")
    parent_places: Optional[List[Any]] = Field(None, description="List of parent places.")
    direct_parent_places: Optional[List[Any]] = Field(None, description="Direct parent places with dates.")
    references: Optional[Any] = Field(None, description="References from other objects.")
