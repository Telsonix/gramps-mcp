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
Tag and Note model definitions for the Gramps API.

This module contains Tag objects for categorizing genealogical data,
and Note objects for storing research notes.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .core_types import StyledText
from .references import Backlinks, BacklinksExtended


class Tag(BaseModel):
    """
    Represents a tag for categorizing genealogical objects.

    Attributes:
        _class: Object class identifier (must be 'Tag').
        handle: Unique identifier for the tag.
        name: The tag name.
        color: Color of the tag (hex code).
        priority: Priority/order of the tag.
        change: Unix timestamp of last modification.
    """

    model_config = ConfigDict(populate_by_name=True)

    class_field: Optional[str] = Field(None, alias="_class", description="Object class name; must be 'Tag'.")
    handle: str = Field(..., description="The unique identifier for the tag.")
    name: str = Field(..., description="Tag name.")
    color: Optional[str] = Field(None, description="Color of the tag (e.g., #efb60c280c28)")
    priority: Optional[int] = Field(None, description="Priority of the tag.")
    change: Optional[float] = Field(None, description="Unix timestamp of last modification.")


class NoteExtended(BaseModel):
    """
    Extended note data with full details of all referenced objects.

    Attributes:
        tags: Tag records for any referenced tags.
        backlinks: Objects referring to this note (extended).
    """

    tags: Optional[List[Any]] = Field(None, description="Tag records for referenced tags.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Objects referring to this note (extended).")


class Note(BaseModel):
    """
    Represents a research note in the genealogical database.

    Attributes:
        _class: Object class identifier (must be 'Note').
        handle: Unique identifier for the note.
        gramps_id: Alternate user-managed identifier.
        text: The note text with optional styling.
        type: The type of note (e.g., "Source text", "Transcript").
        format: Identifier for the note format (0=plain text, 1=RTF).
        private: Whether this record is private.
        tag_list: Handles to tags associated with the note.
        change: Unix timestamp of last modification.
        backlinks: Objects referring to this note.
        extended: Extended data with referenced objects.
    """

    model_config = ConfigDict(populate_by_name=True)

    class_field: Optional[str] = Field(None, alias="_class", description="Object class name; must be 'Note'.")
    handle: str = Field(..., description="The unique identifier for the note.")
    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier.")
    text: Optional[StyledText] = Field(None, description="The note text.")
    type: Optional[str] = Field(None, description="The type of note.")
    format: Optional[int] = Field(None, description="Identifier for the note format.")
    private: Optional[bool] = Field(None, description="Private object indicator.")
    tag_list: Optional[List[str]] = Field(None, description="Tags associated with the note.")
    change: Optional[float] = Field(None, description="Unix timestamp of last modification.")
    backlinks: Optional[Backlinks] = Field(None, description="Objects referring to this note.")
    extended: Optional[NoteExtended] = Field(None, description="Extended data with referenced objects.")
