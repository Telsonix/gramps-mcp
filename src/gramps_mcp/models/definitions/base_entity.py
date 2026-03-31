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
Base entity models for Gramps API objects.

This module provides reusable base classes for all primary entities in the Gramps database.
Entities can inherit from these classes to share common fields and behaviors:

- BaseEntity: Core identity and metadata fields (handle, gramps_id, _class, private, change).
- Referenceable: Extends BaseEntity; adds reference lists (citations, notes, tags, media).
- ExtendedEntity: Extends Referenceable; adds backlinks and extended dereferencing (generic type).
"""

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from .references import Backlinks

# Generic type variable for Extended fields (EventExtended, FamilyExtended, etc.)
ExtendedT = TypeVar("ExtendedT")


class BaseEntity(BaseModel):
    """
    Base class for all primary Gramps entities (Event, Family, Person, Place, etc.).

    Provides core identity and metadata fields shared across all entities.

    Attributes:
        handle: Unique identifier for the object in the Gramps database (required).
        gramps_id: User-managed alternate identifier (e.g., P0001, F0002).
        change: Unix timestamp of the last modification to this object.
        private: Whether this object is marked as private.
        class_field: Object class name (aliased from _class in JSON).

    Config:
        populate_by_name: Allow both field names and aliases in input (e.g., _class or class_field).
    """

    handle: str = Field(..., description="Unique identifier in Gramps database.")
    gramps_id: Optional[str] = Field(None, description="User-managed alternate identifier.")
    change: Optional[float] = Field(None, description="Unix timestamp of last modification.")
    private: Optional[bool] = Field(None, description="Whether this object is marked private.")
    class_field: Optional[str] = Field(None, alias="_class", description="Object class name.")

    model_config = ConfigDict(populate_by_name=True)


class Referenceable(BaseEntity):
    """
    Extends BaseEntity with reference lists for citations, notes, tags, and media.

    Used for entities that can be cited, tagged, or have attached notes and media.

    Attributes:
        citation_list: Handles to citations supporting this object.
        note_list: Handles to research notes about this object.
        tag_list: Handles to tags applied to this object.
        media_list: References or handles to media items attached to this object.
    """

    citation_list: Optional[List[str]] = Field(None, description="Handles to citations.")
    note_list: Optional[List[str]] = Field(None, description="Handles to research notes.")
    tag_list: Optional[List[str]] = Field(None, description="Handles to tags.")
    media_list: Optional[List] = Field(None, description="References or handles to media items.")


class ExtendedEntity(Referenceable, Generic[ExtendedT]):
    """
    Extends Referenceable with backlinks and extended dereferencing (generic type).

    Used for entities that support full object dereferencing via an Extended model.
    Subclasses specify the Extended type parameter (e.g., Event[EventExtended]).

    Type Parameters:
        ExtendedT: The extended (dereferenced) version of this entity.

    Attributes:
        backlinks: Objects referring to this entity.
        extended: Full dereferenced version of this entity (type varies by subclass).
    """

    backlinks: Optional[Backlinks] = Field(None, description="Objects referring to this entity.")
    extended: Optional[ExtendedT] = Field(None, description="Full dereferenced version of this entity.")
