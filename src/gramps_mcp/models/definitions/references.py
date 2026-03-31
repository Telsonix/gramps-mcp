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
    A mapping of object types to handles of objects referring to the current object.

    This model tracks backreferences - which objects reference the current object.

    Attributes:
        person: Handles of people referring to the object.
        family: Handles of families referring to the object.
        event: Handles of events referring to the object.
        place: Handles of places referring to the object.
        source: Handles of sources referring to the object.
        citation: Handles of citations referring to the object.
        media: Handles of media items referring to the object.
    """

    person: Optional[List[str]] = Field(None, description="Handles of people referring to the object.")
    family: Optional[List[str]] = Field(None, description="Handles of families referring to the object.")
    event: Optional[List[str]] = Field(None, description="Handles of events referring to the object.")
    place: Optional[List[str]] = Field(None, description="Handles of places referring to the object.")
    source: Optional[List[str]] = Field(None, description="Handles of sources referring to the object.")
    citation: Optional[List[str]] = Field(None, description="Handles of citations referring to the object.")
    media: Optional[List[str]] = Field(None, description="Handles of media items referring to the object.")


class BacklinksExtended(BaseModel):
    """
    Extended backlinks containing full objects instead of just handles.

    This model provides detailed information about all objects referring to the current object,
    including their complete data rather than just handles.

    Note: The actual model types (Person, Family, Event, Place, Source, Citation, Media)
    are forward-declared at the module level to avoid circular imports.

    Attributes:
        person: Full person objects referring to the object.
        family: Full family objects referring to the object.
        event: Full event objects referring to the object.
        place: Full place objects referring to the object.
        source: Full source objects referring to the object.
        citation: Full citation objects referring to the object.
        media: Full media objects referring to the object.
    """

    person: Optional[List[Any]] = Field(None, description="Person objects referring to the object.")
    family: Optional[List[Any]] = Field(None, description="Family objects referring to the object.")
    event: Optional[List[Any]] = Field(None, description="Event objects referring to the object.")
    place: Optional[List[Any]] = Field(None, description="Place objects referring to the object.")
    source: Optional[List[Any]] = Field(None, description="Source objects referring to the object.")
    citation: Optional[List[Any]] = Field(None, description="Citation objects referring to the object.")
    media: Optional[List[Any]] = Field(None, description="Media objects referring to the object.")
