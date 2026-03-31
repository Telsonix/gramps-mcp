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
Family model definitions for the Gramps API.

This module contains the Family primary object and related models including
ChildReference, FamilyExtended, and FamilyProfile.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .references import Backlinks, BacklinksExtended


class ChildReference(BaseModel):
    """
    A reference to a child in a family relationship.

    Attributes:
        ref: The handle of the child referenced.
        frel: Relationship between the child and father.
        mrel: Relationship between the child and mother.
        citation_list: Handles for citations supporting this child reference.
        note_list: Handles for research notes about this child membership.
        private: Whether this record is private.
    """

    ref: str = Field(..., description="The handle of the child referenced.")
    frel: Optional[str] = Field(None, description="Relationship between the child and father.")
    mrel: Optional[str] = Field(None, description="Relationship between the child and mother.")
    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting the child reference.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about child membership.")
    private: Optional[bool] = Field(None, description="Private object indicator.")


class Family(BaseModel):
    """
    Represents a family relationship in the genealogical database.

    Attributes:
        _class: Object class identifier (must be 'Family').
        handle: Unique identifier for the family.
        gramps_id: Alternate user-managed identifier.
        type: The type of relationship (e.g., 'Married', 'Unmarried').
        father_handle: Handle of the father.
        mother_handle: Handle of the mother.
        child_ref_list: References to children in the family.
        event_ref_list: References to events the family participated in.
        media_list: References to media associated with the family.
        lds_ord_list: List of LDS ordinance events.
        attribute_list: List of attributes about the family.
        citation_list: Handles for citations supporting the family.
        note_list: Handles for research notes about the family.
        tag_list: Handles to tags associated with the family.
        private: Whether this record is private.
        change: Unix timestamp of last modification.
        backlinks: Objects referring to this family.
        extended: Extended data with referenced objects.
        profile: Summary profile information.
    """

    model_config = ConfigDict(populate_by_name=True)

    class_field: Optional[str] = Field(None, alias="_class", description="Object class name; must be 'Family'.")
    handle: str = Field(..., description="The unique identifier for a family.")
    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier for the family.")
    type: Optional[str] = Field(None, description="The type of relationship between parents.")
    father_handle: Optional[str] = Field(None, description="Handle of the father.")
    mother_handle: Optional[str] = Field(None, description="Handle of the mother.")
    child_ref_list: Optional[List[ChildReference]] = Field(None, description="References to children in the family.")
    event_ref_list: Optional[List[Any]] = Field(None, description="References to events the family participated in.")
    media_list: Optional[List[Any]] = Field(None, description="References to media associated with family.")
    lds_ord_list: Optional[List[Any]] = Field(None, description="List of LDS ordinance events.")
    attribute_list: Optional[List[Any]] = Field(None, description="List of attributes about the family.")
    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting the family.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about the family.")
    tag_list: Optional[List[str]] = Field(None, description="Tags associated with the family.")
    private: Optional[bool] = Field(None, description="Private object indicator.")
    change: Optional[float] = Field(None, description="Unix timestamp of last modification.")
    backlinks: Optional[Backlinks] = Field(None, description="Objects referring to this family.")
    extended: Optional["FamilyExtended"] = Field(None, description="Extended data with referenced objects.")
    profile: Optional[Any] = Field(None, description="Summary profile information.")


class FamilyExtended(BaseModel):
    """
    Extended family data with full details of all referenced objects.

    Attributes:
        father: The person record for the father if known.
        mother: The person record for the mother if known.
        children: The person records for any referenced children.
        citations: Citation records for any referenced citations.
        events: Event records for any referenced events.
        media: Media records for any referenced media objects.
        notes: Note records for any referenced notes.
        tags: Tag records for any referenced tags.
        backlinks: Objects referring to this family (extended).
    """

    father: Optional[Any] = Field(None, description="Person record for the father.")
    mother: Optional[Any] = Field(None, description="Person record for the mother.")
    children: Optional[List[Any]] = Field(None, description="Person records for children.")
    citations: Optional[List[Any]] = Field(None, description="Citation records for referenced citations.")
    events: Optional[List[Any]] = Field(None, description="Event records for referenced events.")
    media: Optional[List[Any]] = Field(None, description="Media records for referenced media objects.")
    notes: Optional[List[Any]] = Field(None, description="Note records for referenced notes.")
    tags: Optional[List[Any]] = Field(None, description="Tag records for referenced tags.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Objects referring to this family (extended).")


class FamilyProfile(BaseModel):
    """
    Profile summary of a family with key members and events.

    Attributes:
        handle: Unique identifier for the family.
        gramps_id: Alternate user-managed identifier.
        father: Person profile for the father.
        mother: Person profile for the mother.
        children: Person profiles for children in the family.
        family_surname: The surname of the family.
        relationship: The relationship type between parents.
        marriage: Marriage event profile.
        divorce: Divorce event profile.
        events: Event profiles for all family events.
        references: References from other objects.
    """

    handle: Optional[str] = Field(None, description="Unique identifier for the family.")
    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier.")
    father: Optional[Any] = Field(None, description="Person profile for the father.")
    mother: Optional[Any] = Field(None, description="Person profile for the mother.")
    children: Optional[List[Any]] = Field(None, description="Person profiles for children.")
    family_surname: Optional[str] = Field(None, description="Surname of the family.")
    relationship: Optional[str] = Field(None, description="Relationship type between parents.")
    marriage: Optional[Any] = Field(None, description="Marriage event profile.")
    divorce: Optional[Any] = Field(None, description="Divorce event profile.")
    events: Optional[List[Any]] = Field(None, description="Event profiles for all family events.")
    references: Optional[Any] = Field(None, description="References from other objects.")
