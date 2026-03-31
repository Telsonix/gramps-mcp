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
Person model definitions for the Gramps API.

This module contains the Person primary object and related models including
PersonReference, PersonExtended, PersonProfile, and TimelinePersonProfile.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field

from .base_entity import ExtendedEntity
from .core_types import Address, Name, URL
from .references import BacklinksExtended


class PersonReference(BaseModel):
    """
    A reference to another person with relationship information.

    Attributes:
        citation_list: Handles for citations supporting the association.
        note_list: Handles for research notes about the association.
        private: Whether this record is private.
        ref: The handle of the person referenced.
        rel: The relationship between the two people.
    """

    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting the association.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about the association.")
    private: Optional[bool] = Field(None, description="Private object indicator.")
    ref: str = Field(..., description="The handle of the person referenced.")
    rel: Optional[str] = Field(None, description="The relationship between the two people.")


class Person(ExtendedEntity["PersonExtended"]):
    """
    Represents a person in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Attributes:
        address_list: List of addresses for the person.
        alternate_names: List of all known names used by the person.
        attribute_list: List of attributes about the person.
        birth_ref_index: Index of birth event in event_ref_list.
        death_ref_index: Index of death event in event_ref_list.
        event_ref_list: References to events the person participated in.
        family_list: Handles of families where person is a parent.
        gender: Gender/sex (0=unknown, 1=male, 2=female).
        lds_ord_list: List of LDS ordinance events.
        parent_family_list: Handles of parent family records.
        person_ref_list: References to relationships with other people.
        primary_name: The primary name of the person.
        urls: List of URLs associated with the person.
        profile: Summary profile information.
    """

    address_list: Optional[List[Address]] = Field(None, description="List of addresses for the person.")
    alternate_names: Optional[List[Name]] = Field(None, description="List of all known names used by the person.")
    attribute_list: Optional[List[Any]] = Field(None, description="List of attributes about the person.")
    birth_ref_index: Optional[int] = Field(None, description="Index indicating if birth event is assigned.")
    death_ref_index: Optional[int] = Field(None, description="Index indicating if death event is assigned.")
    event_ref_list: Optional[List[Any]] = Field(None, description="References to events the person participated in.")
    family_list: Optional[List[str]] = Field(None, description="Handles of families where person is parent.")
    gender: Optional[int] = Field(None, description="Gender/sex of the person.")
    lds_ord_list: Optional[List[Any]] = Field(None, description="List of LDS ordinance events.")
    parent_family_list: Optional[List[str]] = Field(None, description="Handles of parent family records.")
    person_ref_list: Optional[List[PersonReference]] = Field(None, description="References to relationships with other people.")
    primary_name: Optional[Name] = Field(None, description="Primary name of the person.")
    urls: Optional[List[URL]] = Field(None, description="URLs associated with the person.")
    profile: Optional[Any] = Field(None, description="Summary profile information.")


class PersonExtended(BaseModel):
    """
    Extended person data with full details of all referenced objects.

    Attributes:
        citations: Citation records for any referenced citations.
        events: Event records for any referenced events.
        families: Family records for any referenced families.
        media: Media records for any referenced media objects.
        notes: Note records for any referenced notes.
        parent_families: Family records for parent families.
        people: Person records for any referenced persons.
        primary_parent_family: Family record for primary parent family.
        tags: Tag records for any referenced tags.
        backlinks: Objects referring to this person (extended).
    """

    citations: Optional[List[Any]] = Field(None, description="Citation records for referenced citations.")
    events: Optional[List[Any]] = Field(None, description="Event records for referenced events.")
    families: Optional[List[Any]] = Field(None, description="Family records for referenced families.")
    media: Optional[List[Any]] = Field(None, description="Media records for referenced media objects.")
    notes: Optional[List[Any]] = Field(None, description="Note records for referenced notes.")
    parent_families: Optional[List[Any]] = Field(None, description="Family records for parent families.")
    people: Optional[List[Any]] = Field(None, description="Person records for referenced persons.")
    primary_parent_family: Optional[Any] = Field(None, description="Family record for primary parent family.")
    tags: Optional[List[Any]] = Field(None, description="Tag records for referenced tags.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Objects referring to this person (extended).")


class PersonProfile(BaseModel):
    """
    Profile summary of a person with key events and relationships.

    Attributes:
        handle: Unique identifier for the person.
        gramps_id: Alternate user-managed identifier.
        name_display: Preferred name in display format.
        name_given: Preferred given name.
        name_surname: Preferred surname.
        name_suffix: Name suffix.
        sex: Gender identifier (M/F/U).
        birth: Birth event profile.
        death: Death event profile.
        events: Event profiles for all person events.
        families: Family profiles for families person is parent of.
        primary_parent_family: Family profile for primary parents.
        other_parent_families: Family profiles for other parent families.
        references: References from other objects.
    """

    handle: Optional[str] = Field(None, description="Unique identifier for the person.")
    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier.")
    name_display: Optional[str] = Field(None, description="Preferred name in display format.")
    name_given: Optional[str] = Field(None, description="Preferred given name.")
    name_surname: Optional[str] = Field(None, description="Preferred surname.")
    name_suffix: Optional[str] = Field(None, description="Name suffix.")
    sex: Optional[str] = Field(None, description="Gender identifier.")
    birth: Optional[Any] = Field(None, description="Birth event profile.")
    death: Optional[Any] = Field(None, description="Death event profile.")
    events: Optional[List[Any]] = Field(None, description="Event profiles for all person events.")
    families: Optional[List[Any]] = Field(None, description="Family profiles for families person is parent of.")
    primary_parent_family: Optional[Any] = Field(None, description="Family profile for primary parents.")
    other_parent_families: Optional[List[Any]] = Field(None, description="Family profiles for other parent families.")
    references: Optional[Any] = Field(None, description="References from other objects.")


class TimelinePersonProfile(BaseModel):
    """
    Person profile with timeline context including age at events.

    Attributes:
        handle: Unique identifier for the person.
        gramps_id: Alternate user-managed identifier.
        name_display: Preferred name in display format.
        name_given: Preferred given name.
        name_surname: Preferred surname.
        name_suffix: Name suffix.
        sex: Gender identifier.
        age: Age of the person at the time of an event.
        relationship: Relationship to the timeline-anchored person.
        birth: Birth event profile.
        death: Death event profile.
    """

    handle: Optional[str] = Field(None, description="Unique identifier for the person.")
    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier.")
    name_display: Optional[str] = Field(None, description="Preferred name in display format.")
    name_given: Optional[str] = Field(None, description="Preferred given name.")
    name_surname: Optional[str] = Field(None, description="Preferred surname.")
    name_suffix: Optional[str] = Field(None, description="Name suffix.")
    sex: Optional[str] = Field(None, description="Gender identifier.")
    age: Optional[str] = Field(None, description="Age at the time of an event.")
    relationship: Optional[str] = Field(None, description="Relationship to the timeline-anchored person.")
    birth: Optional[Any] = Field(None, description="Birth event profile.")
    death: Optional[Any] = Field(None, description="Death event profile.")
