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

from pydantic import BaseModel, Field, field_validator

from .base_entity import ExtendedEntity
from .references import BacklinksExtended


class ChildReference(BaseModel):
    """
    A reference to a child's membership in a family, with parentage relationship types.

    Records the relationship between a child and each parent in the family.
    Both biological and non-biological relationships (adopted, step, foster, etc.) are supported.

    Attributes:
        ref: Handle of the child Person object. Required.
        frel: Father-child relationship type. Examples: 'Birth' (biological), 'Adopted',
            'Stepchild', 'Foster', 'Sponsored', 'Unknown'. Defaults to 'Birth' if null.
        mrel: Mother-child relationship type. Same values as frel.
            Examples: 'Birth', 'Adopted', 'Stepchild', 'Foster', 'Unknown'.
        citation_list: Handles for citations supporting this child relationship.
        note_list: Handles for research notes about this child's family membership.
        private: True if this child reference is confidential.
    """

    ref: str = Field(..., description="Handle of the child Person object. Required.")
    frel: Optional[str] = Field(None, description="Father-child relationship: 'Birth' (biological), 'Adopted', 'Stepchild', 'Foster', 'Sponsored', 'Unknown'.")
    mrel: Optional[str] = Field(None, description="Mother-child relationship: 'Birth' (biological), 'Adopted', 'Stepchild', 'Foster', 'Sponsored', 'Unknown'.")
    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting this child relationship.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about this child's family membership.")
    private: Optional[bool] = Field(None, description="True if this child reference is confidential.")


class Family(ExtendedEntity["FamilyExtended"]):
    """
    Represents a family relationship unit in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    A Family groups two parents (father and mother, in any combination) and their children.
    It records the relationship type between the parents, associated events (marriage, divorce),
    and provides the central link for building family trees.

    Attributes:
        type: Relationship type between the parents (optional, max 100 chars).
            Examples: 'Married', 'Unmarried', 'Civil Union', 'Unknown', 'Partners'.
        father_handle: Handle of the Person who is the father/first parent (optional, max 50 chars).
            Null if the father is unknown or not recorded.
        mother_handle: Handle of the Person who is the mother/second parent (optional, max 50 chars).
            Null if the mother is unknown or not recorded.
        child_ref_list: ChildReference objects for each child in the family. Each reference
            includes the child's person handle and the parentage relationship type (birth/adopted/etc.).
        event_ref_list: EventReference objects for family events (marriage, divorce, separation, etc.).
            Each reference includes the event handle and role.
        lds_ord_list: LDS ordinance records (sealing to spouse) associated with this family.
        attribute_list: Additional key-value properties for this family.
        profile: Read-only profile summary (FamilyProfile) with parents, children, and key events.
    """

    type: Optional[str] = Field(
        None,
        description="Relationship type between parents. Examples: 'Married', 'Unmarried', 'Civil Union', 'Partners', 'Unknown'. Max 100 chars.",
    )
    father_handle: Optional[str] = Field(
        None,
        description="Handle of the father/first parent Person. Null if unknown or unrecorded. Max 50 chars.",
    )
    mother_handle: Optional[str] = Field(
        None,
        description="Handle of the mother/second parent Person. Null if unknown or unrecorded. Max 50 chars.",
    )
    child_ref_list: Optional[List[ChildReference]] = Field(None, description="ChildReference objects for each child. Each includes child handle and parentage type (birth/adopted/stepchild/etc.).")
    event_ref_list: Optional[List[Any]] = Field(None, description="EventReference objects for family events (marriage, divorce, separation, etc.).")
    lds_ord_list: Optional[List[Any]] = Field(None, description="LDS ordinance records (sealing to spouse) for this family.")
    attribute_list: Optional[List[Any]] = Field(None, description="Additional key-value properties for this family.")
    profile: Optional["FamilyProfile"] = Field(None, description="Read-only profile summary with parents, children, and key events. Auto-populated by the API.")

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v: Any) -> Optional[str]:
        """Validate type: optional, max 100 chars, trimmed.

        Args:
            v: Relationship type value (string or None).

        Returns:
            Trimmed type string or None.

        Raises:
            ValueError: If type exceeds 100 characters.

        Example:
            "  Married  " → "Married"
            "Civil Union" → "Civil Union"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 100:
            raise ValueError(f"type exceeds 100 chars (got {len(v)})")
        return v

    @field_validator("father_handle", "mother_handle", mode="before")
    @classmethod
    def validate_parent_handle(cls, v: Any) -> Optional[str]:
        """Validate parent handle: optional, max 50 chars, trimmed, non-empty.

        Args:
            v: Parent handle value (string or None).

        Returns:
            Trimmed handle or None.

        Raises:
            ValueError: If handle exceeds 50 chars or is empty string.

        Example:
            "  c0d0a0d0a0d0a0d0  " → "c0d0a0d0a0d0a0d0"
            "" → None
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if v == "":
            return None
        if len(v) > 50:
            raise ValueError(f"handle exceeds 50 chars (got {len(v)})")
        return v


class FamilyExtended(BaseModel):
    """
    Extended family data with fully dereferenced objects instead of just handles.

    Populated only when the extended query parameter is requested. Contains complete
    records for all objects referenced by the family.

    Attributes:
        father: Full Person record for the father/first parent. Null if none assigned.
        mother: Full Person record for the mother/second parent. Null if none assigned.
        children: Full Person records for each child referenced in child_ref_list.
        citations: Full Citation records for each citation referenced by this family.
        events: Full Event records for each event in event_ref_list.
        media: Full Media records for each media item attached to this family.
        notes: Full Note records for each note attached to this family.
        tags: Full Tag records for each tag applied to this family.
        backlinks: Full records of all objects that reference this family.
    """

    father: Optional[Any] = Field(None, description="Full Person record for the father/first parent. Null if not assigned.")
    mother: Optional[Any] = Field(None, description="Full Person record for the mother/second parent. Null if not assigned.")
    children: Optional[List[Any]] = Field(None, description="Full Person records for all children referenced in child_ref_list.")
    citations: Optional[List[Any]] = Field(None, description="Full Citation records for each citation referenced by this family.")
    events: Optional[List[Any]] = Field(None, description="Full Event records for each event in event_ref_list.")
    media: Optional[List[Any]] = Field(None, description="Full Media records for each media item attached to this family.")
    notes: Optional[List[Any]] = Field(None, description="Full Note records for each note attached to this family.")
    tags: Optional[List[Any]] = Field(None, description="Full Tag records for each tag applied to this family.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Full records of all objects (people, events) that reference this family.")


class FamilyProfile(BaseModel):
    """
    Read-only profile summary of a family with key members and events.

    Returned by the API for display purposes. Contains pre-computed display fields
    including person profiles for parents and children.

    Attributes:
        handle: Unique handle (ID) of the family.
        gramps_id: Alternate user-managed identifier. Examples: 'F0001', 'F01234'.
        father: Person profile for the father/first parent. Null if not recorded.
        mother: Person profile for the mother/second parent. Null if not recorded.
        children: Person profiles for all children in baby_ref_list.
        family_surname: Derived surname for the family unit. Example: 'Smith'.
        relationship: Relationship type label. Examples: 'Married', 'Unmarried', 'Civil Union'.
        marriage: Marriage event profile with date and place. Null if no marriage event.
        divorce: Divorce event profile with date and place. Null if no divorce event.
        events: Profiles for all events associated with this family.
        references: Summary count or list of objects referencing this family.
    """

    handle: Optional[str] = Field(None, description="Unique handle (ID) of the family.")
    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier. Examples: 'F0001', 'F01234'.")
    father: Optional[Any] = Field(None, description="Person profile for the father/first parent. Null if not recorded.")
    mother: Optional[Any] = Field(None, description="Person profile for the mother/second parent. Null if not recorded.")
    children: Optional[List[Any]] = Field(None, description="Person profiles for all children in this family.")
    family_surname: Optional[str] = Field(None, description="Derived surname for the family unit. Example: 'Smith'.")
    relationship: Optional[str] = Field(None, description="Relationship type label. Examples: 'Married', 'Unmarried', 'Civil Union', 'Partners'.")
    marriage: Optional[Any] = Field(None, description="Marriage event profile with date and place. Null if no marriage event.")
    divorce: Optional[Any] = Field(None, description="Divorce event profile with date and place. Null if no divorce event.")
    events: Optional[List[Any]] = Field(None, description="Profiles for all events associated with this family.")
    references: Optional[Any] = Field(None, description="Summary count or list of objects referencing this family.")
