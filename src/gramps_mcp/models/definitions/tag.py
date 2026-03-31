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

from pydantic import BaseModel, Field

from .base_entity import BaseEntity, ExtendedEntity
from .core_types import StyledText
from .references import BacklinksExtended


class Tag(BaseEntity):
    """
    Represents a tag for categorizing genealogical objects.

    Inherits core identity and metadata from BaseEntity.

    Attributes:
        name: The tag name.
        color: Color of the tag (hex code).
        priority: Priority/order of the tag.
    """

    name: str = Field(..., description="Tag name.")
    color: Optional[str] = Field(None, description="Color of the tag (e.g., #efb60c280c28)")
    priority: Optional[int] = Field(None, description="Priority of the tag.")


class NoteExtended(BaseModel):
    """
    Extended note data with full details of all referenced objects.

    Attributes:
        tags: Tag records for any referenced tags.
        backlinks: Objects referring to this note (extended).
    """

    tags: Optional[List[Any]] = Field(None, description="Tag records for referenced tags.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Objects referring to this note (extended).")


class Note(ExtendedEntity["NoteExtended"]):
    """
    Represents a research note in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Attributes:
        text: The note text with optional styling.
        type: The type of note (e.g., "Source text", "Transcript").
        format: Identifier for the note format (0=plain text, 1=RTF).
    """

    text: Optional[StyledText] = Field(None, description="The note text.")
    type: Optional[str] = Field(None, description="The type of note.")
    format: Optional[int] = Field(None, description="Identifier for the note format.")
