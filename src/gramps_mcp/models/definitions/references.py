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
Reference models for objects in the Gramps API.

This module contains reference models that point to other objects in the database,
including Backlinks and BacklinksExtended which aggregate references from other objects.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Backlinks(BaseModel):
    """
    A mapping of object types to handle lists of objects referring to the current object.

    This model tracks reverse references (backlinks) — which objects reference the current
    object by handle. Used in ExtendedEntity for lightweight backlink lookup.

    Attributes:
        person: Handles of Person records that reference this object.
        family: Handles of Family records that reference this object.
        event: Handles of Event records that reference this object.
        place: Handles of Place records that reference this object.
        source: Handles of Source records that reference this object.
        citation: Handles of Citation records that reference this object.
        media: Handles of Media records that reference this object.
    """

    person: Optional[List[str]] = Field(None, description="Handles of Person records that reference this object.")
    family: Optional[List[str]] = Field(None, description="Handles of Family records that reference this object.")
    event: Optional[List[str]] = Field(None, description="Handles of Event records that reference this object.")
    place: Optional[List[str]] = Field(None, description="Handles of Place records that reference this object.")
    source: Optional[List[str]] = Field(None, description="Handles of Source records that reference this object.")
    citation: Optional[List[str]] = Field(None, description="Handles of Citation records that reference this object.")
    media: Optional[List[str]] = Field(None, description="Handles of Media records that reference this object.")


class BacklinksExtended(BaseModel):
    """
    Extended backlinks containing full object records instead of just handles.

    Provides detailed information about all objects that reference the current object,
    with complete data rather than just handles. Populated by the extended query parameter.

    Note: Actual types (Person, Family, Event, etc.) are declared as Any due to circular imports.

    Attributes:
        person: Full Person records for people that reference this object.
        family: Full Family records for families that reference this object.
        event: Full Event records for events that reference this object.
        place: Full Place records for places that reference this object.
        source: Full Source records for sources that reference this object.
        citation: Full Citation records for citations that reference this object.
        media: Full Media records for media items that reference this object.
    """

    person: Optional[List[Any]] = Field(None, description="Full Person records for people that reference this object.")
    family: Optional[List[Any]] = Field(None, description="Full Family records for families that reference this object.")
    event: Optional[List[Any]] = Field(None, description="Full Event records for events that reference this object.")
    place: Optional[List[Any]] = Field(None, description="Full Place records for places that reference this object.")
    source: Optional[List[Any]] = Field(None, description="Full Source records for sources that reference this object.")
    citation: Optional[List[Any]] = Field(None, description="Full Citation records for citations that reference this object.")
    media: Optional[List[Any]] = Field(None, description="Full Media records for media items that reference this object.")
