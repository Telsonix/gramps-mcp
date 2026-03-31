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
Media model definitions for the Gramps API.

This module contains the Media primary object and related models including
MediaReference, MediaExtended, and MediaProfile.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .core_types import Date
from .references import Backlinks, BacklinksExtended


class MediaReference(BaseModel):
    """
    A reference to a media object with attributes and notes.

    Attributes:
        ref: The handle of the media referenced.
        rect: Rectangle coordinates for media cropping.
        attribute_list: Attributes related to the media reference.
        citation_list: Handles for citations supporting the reference.
        note_list: Handles for research notes about the reference.
        private: Whether this record is private.
    """

    ref: str = Field(..., description="The handle of the media referenced.")
    rect: Optional[List[float]] = Field(None, description="Rectangle coordinates.")
    attribute_list: Optional[List[Any]] = Field(None, description="Attributes related to the reference.")
    citation_list: Optional[List[str]] = Field(None, description="Handles for citations.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes.")
    private: Optional[bool] = Field(None, description="Private object indicator.")


class Media(BaseModel):
    """
    Represents a media object in the genealogical database.

    Attributes:
        _class: Object class identifier (must be 'Media').
        handle: Unique identifier for the media object.
        gramps_id: Alternate user-managed identifier.
        path: The path to load the media from storage.
        mime: The format of the media object.
        desc: A description of the media contents.
        date: The date associated with the media.
        checksum: A checksum for integrity validation.
        attribute_list: List of attributes about the media.
        citation_list: Handles for citations supporting the media.
        media_list: References to other media.
        note_list: Handles for research notes about the media.
        tag_list: Handles to tags associated with the media.
        private: Whether this record is private.
        change: Unix timestamp of last modification.
        backlinks: Objects referring to this media.
        extended: Extended data with referenced objects.
        profile: Summary profile information.
    """

    model_config = ConfigDict(populate_by_name=True)

    class_field: Optional[str] = Field(None, alias="_class", description="Object class name; must be 'Media'.")
    handle: str = Field(..., description="The unique identifier for the media object.")
    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier.")
    path: Optional[str] = Field(None, description="Path to locate and load the media.")
    mime: Optional[str] = Field(None, description="The format of the media object.")
    desc: Optional[str] = Field(None, description="Description of the media contents.")
    date: Optional[Date] = Field(None, description="Date associated with the media.")
    checksum: Optional[str] = Field(None, description="Checksum for integrity validation.")
    attribute_list: Optional[List[Any]] = Field(None, description="List of attributes about the media.")
    citation_list: Optional[List[str]] = Field(None, description="Handles for citations.")
    media_list: Optional[List[MediaReference]] = Field(None, description="References to other media.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes.")
    tag_list: Optional[List[str]] = Field(None, description="Tags associated with the media.")
    private: Optional[bool] = Field(None, description="Private object indicator.")
    change: Optional[float] = Field(None, description="Unix timestamp of last modification.")
    backlinks: Optional[Backlinks] = Field(None, description="Objects referring to this media.")
    extended: Optional["MediaExtended"] = Field(None, description="Extended data with referenced objects.")
    profile: Optional[Any] = Field(None, description="Summary profile information.")


class MediaExtended(BaseModel):
    """
    Extended media data with full details of all referenced objects.

    Attributes:
        citations: Citation records for any referenced citations.
        notes: Note records for any referenced notes.
        tags: Tag records for any referenced tags.
        backlinks: Objects referring to this media (extended).
    """

    citations: Optional[List[Any]] = Field(None, description="Citation records for referenced citations.")
    notes: Optional[List[Any]] = Field(None, description="Note records for referenced notes.")
    tags: Optional[List[Any]] = Field(None, description="Tag records for referenced tags.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Objects referring to this media (extended).")


class MediaProfile(BaseModel):
    """
    Profile summary of a media object with references.

    Attributes:
        gramps_id: Alternate user-managed identifier.
        date: Date of media.
        references: References from other objects (person, family, event, etc).
    """

    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier.")
    date: Optional[str] = Field(None, description="Date of media.")
    references: Optional[Any] = Field(None, description="References from other objects.")
