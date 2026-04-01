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

from pydantic import BaseModel, Field, field_validator

from .base_entity import ExtendedEntity
from .core_types import Date, Location, URL
from .references import BacklinksExtended


class PlaceName(BaseModel):
    """
    Represents an alternate or historical name for a place.

    Places may have had different names in different languages or at different periods
    in history. PlaceName records capture these variants with optional date range and
    language information.

    Attributes:
        value: The place name string. Examples: 'New York', 'Nouvelle-Orléans',
            'Königsberg' (historical name of Kaliningrad), 'Constantinople'.
        date: Date or date range when this name was in use.
            Example: 'before 1946' for a pre-WWII place name.
        lang: ISO language code for this name. Examples: 'en' (English), 'de' (German),
            'fr' (French), 'pl' (Polish). Null if language unspecified.
    """

    value: Optional[str] = Field(None, description="Place name string. Examples: 'New York', 'Königsberg', 'Constantinople', 'Nouvelle-Orléans'.")
    date: Optional[Date] = Field(None, description="Date or range when this name was in use. Examples: 'before 1946', '1776-1783'.")
    lang: Optional[str] = Field(None, description="ISO language code. Examples: 'en' (English), 'de' (German), 'fr' (French), 'pl' (Polish).")


class PlaceReference(BaseModel):
    """
    A reference to a parent place, establishing a place hierarchy.

    Used in placeref_list to connect a place to a broader parent place
    (e.g., a city references its country). May include a date range indicating
    when the hierarchical relationship was valid.

    Attributes:
        ref: Handle of the referenced parent Place object. Required.
        date: Date or range when this hierarchical relationship was valid.
            Example: a town that was part of one county until 1900 and another after.
    """

    ref: str = Field(..., description="Handle of the referenced parent Place object. Required.")
    date: Optional[Date] = Field(None, description="Date or range when this parent-child relationship was valid.")


class Place(ExtendedEntity["PlaceExtended"]):
    """
    Represents a geographic place in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Places represent locations at any level of geographic hierarchy: countries, states,
    counties, cities, parishes, streets, or specific locations. Places can reference
    parent places to build a hierarchy (e.g., Boston → Massachusetts → USA).

    Attributes:
        title: Full descriptive title of the place (optional, max 255 chars).
            Usually combines name and hierarchy. Example: 'Boston, Massachusetts, USA'.
        name: Primary PlaceName object for this place.
        place_type: Geographic classification (optional, max 100 chars).
            Examples: 'City', 'Country', 'County', 'Parish', 'State', 'Province',
            'Village', 'Town', 'Hamlet', 'Farm', 'Church', 'Cemetery'.
        code: Administrative code for the place (optional, max 50 chars).
            Examples: 'US-MA', 'GB-ENG', 'DE-BY'. Used for ISO 3166 or FIPS codes.
        lat: Latitude coordinate as numeric string (optional).
            Examples: '42.3601', '51.5074'. Validated to be a numeric value.
        long: Longitude coordinate as numeric string (optional).
            Examples: '-71.0589', '-0.1278'. Validated to be a numeric value.
        alt_names: List of alternate/historical PlaceName objects.
            Examples: previous names, names in other languages.
        alt_loc: Alternate location data (Location objects with city/state/country fields).
        placeref_list: Parent PlaceReference objects establishing place hierarchy.
            A city would reference the state; a state would reference the country.
        urls: URLs associated with this place. Examples: Wikipedia article, official website.
        profile: Read-only profile summary (PlaceProfile) with coordinates and hierarchy.
    """

    title: Optional[str] = Field(
        None,
        description="Full descriptive title. Usually includes parent hierarchy. Example: 'Boston, Massachusetts, USA'. Max 255 chars.",
    )
    name: Optional[PlaceName] = Field(None, description="Primary PlaceName object with value, date, and language.")
    place_type: Optional[str] = Field(
        None,
        description="Geographic classification. Examples: 'City', 'County', 'Parish', 'State', 'Country', 'Village', 'Cemetery', 'Church'. Max 100 chars.",
    )
    code: Optional[str] = Field(
        None,
        description="Administrative code (ISO 3166 or FIPS). Examples: 'US-MA', 'GB-ENG', 'DE-BY'. Max 50 chars.",
    )
    lat: Optional[str] = Field(
        None,
        description="Latitude coordinate as numeric string. Examples: '42.3601', '51.5074', '-33.8688'. Validated as numeric.",
    )
    long: Optional[str] = Field(
        None,
        description="Longitude coordinate as numeric string. Examples: '-71.0589', '-0.1278', '151.2093'. Validated as numeric.",
    )
    alt_names: Optional[List[PlaceName]] = Field(None, description="Alternate or historical PlaceName objects. Examples: previous names, names in different languages.")
    alt_loc: Optional[List[Location]] = Field(None, description="Alternate location representations (Location objects with city/state/country fields).")
    placeref_list: Optional[List[PlaceReference]] = Field(None, description="Parent PlaceReference objects establishing hierarchy. Example: Boston → Massachusetts → USA.")
    urls: Optional[List[URL]] = Field(None, description="URLs for this place. Examples: Wikipedia article, official municipality website.")
    profile: Optional["PlaceProfile"] = Field(None, description="Read-only profile summary with coordinates and place hierarchy. Auto-populated by the API.")

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, v: Any) -> Optional[str]:
        """Validate title: optional, max 255 chars, trimmed.

        Args:
            v: Title value (string or None).

        Returns:
            Trimmed title or None.

        Raises:
            ValueError: If title exceeds 255 characters.

        Example:
            "  New York, NY, USA  " → "New York, NY, USA"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 255:
            raise ValueError(f"title exceeds 255 chars (got {len(v)})")
        return v

    @field_validator("place_type", mode="before")
    @classmethod
    def validate_place_type(cls, v: Any) -> Optional[str]:
        """Validate place_type: optional, max 100 chars, trimmed.

        Args:
            v: Place type value (string or None).

        Returns:
            Trimmed place type or None.

        Raises:
            ValueError: If place_type exceeds 100 characters.

        Example:
            "  City  " → "City"
            "County Seat" → "County Seat"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 100:
            raise ValueError(f"place_type exceeds 100 chars (got {len(v)})")
        return v

    @field_validator("code", mode="before")
    @classmethod
    def validate_code(cls, v: Any) -> Optional[str]:
        """Validate code: optional, max 50 chars, trimmed.

        Args:
            v: Code value (string or None).

        Returns:
            Trimmed code or None.

        Raises:
            ValueError: If code exceeds 50 characters.

        Example:
            "  US-NY  " → "US-NY"
            "GB-ENG" → "GB-ENG"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 50:
            raise ValueError(f"code exceeds 50 chars (got {len(v)})")
        return v

    @field_validator("lat", "long", mode="before")
    @classmethod
    def validate_coordinate(cls, v: Any) -> Optional[str]:
        """Validate coordinate: optional, must be valid numeric format.

        Args:
            v: Coordinate value (string, float, int, or None).

        Returns:
            String representation of coordinate or None.

        Raises:
            ValueError: If coordinate is not a valid number.

        Example:
            "40.7128" → "40.7128"
            40.7128 → "40.7128"
            -74.0060 → "-74.0060"
            "not_a_number" → ValueError
            None → None
        """
        if v is None or v == "":
            return None
        try:
            # Validate it's a valid number
            float(v)
            return str(v).strip() if isinstance(v, str) else str(v)
        except (ValueError, TypeError):
            raise ValueError(f"coordinate must be numeric, got '{v}'")


class PlaceExtended(BaseModel):
    """
    Extended place data with fully dereferenced objects instead of just handles.

    Populated only when the extended query parameter is requested. Contains complete
    records for all objects referenced by the place.

    Attributes:
        citations: Full Citation records for each citation referenced by this place.
        media: Full Media records for each media item attached to this place.
        notes: Full Note records for each note attached to this place.
        tags: Full Tag records for each tag applied to this place.
        backlinks: Full records of all objects (events, people) that reference this place.
    """

    citations: Optional[List[Any]] = Field(None, description="Full Citation records for each citation referenced by this place.")
    media: Optional[List[Any]] = Field(None, description="Full Media records for each media item attached to this place.")
    notes: Optional[List[Any]] = Field(None, description="Full Note records for each note attached to this place.")
    tags: Optional[List[Any]] = Field(None, description="Full Tag records for each tag applied to this place.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Full records of all objects (events, people, families) that reference this place.")


class PlaceProfile(BaseModel):
    """
    Read-only profile summary of a place with geographic coordinates and hierarchy.

    Returned by the API for display purposes. Contains pre-computed display fields
    including resolved coordinates and the place hierarchy chain.

    Attributes:
        name: Place title/display name. Example: 'Boston, Massachusetts, USA'.
        gramps_id: Alternate user-managed identifier. Examples: 'P0001', 'LOC042'.
        lat: Geographic latitude as float. Examples: 42.3601, 51.5074.
        long: Geographic longitude as float. Examples: -71.0589, -0.1278.
        alternate_names: List of alternate name strings for this place.
        alternate_place_names: Alternate PlaceName objects with date and language metadata.
        parent_places: List of parent place name strings in the hierarchy chain.
            Example: ['Massachusetts', 'North America', 'USA'].
        direct_parent_places: Direct parent place objects with associated date ranges.
        references: Summary count or list of objects (events, people) referencing this place.
    """

    name: Optional[str] = Field(None, description="Place title/display name. Example: 'Boston, Massachusetts, USA'.")
    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier. Examples: 'P0001', 'LOC042'.")
    lat: Optional[float] = Field(None, description="Geographic latitude as float. Examples: 42.3601, 51.5074, -33.8688.")
    long: Optional[float] = Field(None, description="Geographic longitude as float. Examples: -71.0589, -0.1278, 151.2093.")
    alternate_names: Optional[List[str]] = Field(None, description="Alternate name strings for this place.")
    alternate_place_names: Optional[List[Any]] = Field(None, description="Alternate PlaceName objects with date range and language metadata.")
    parent_places: Optional[List[Any]] = Field(None, description="Parent place name strings in the hierarchy chain. Example: ['Massachusetts', 'USA'].")
    direct_parent_places: Optional[List[Any]] = Field(None, description="Direct parent place objects with associated date ranges.")
    references: Optional[Any] = Field(None, description="Summary count or list of objects (events, people, families) referencing this place.")
