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

from pydantic import BaseModel, Field, field_validator

from .base_entity import ExtendedEntity
from .core_types import Address, Name, URL
from .references import BacklinksExtended


class PersonReference(BaseModel):
    """
    A reference from one person to another with relationship information.

    Used in person_ref_list to record associations such as godparent, foster parent,
    or other non-family relationships between two people.

    Attributes:
        citation_list: Handles for citations supporting this association.
        note_list: Handles for research notes about this association.
        private: True if this reference is confidential.
        ref: Handle of the person being referenced. Required.
        rel: Description of the relationship. Examples: 'Godfather', 'Godmother',
            'Foster parent', 'Employer', 'Neighbor'. Free-form text.
    """

    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting this person association.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about this person association.")
    private: Optional[bool] = Field(None, description="True if this reference is confidential.")
    ref: str = Field(..., description="Handle of the referenced person. Required.")
    rel: Optional[str] = Field(None, description="Relationship description. Examples: 'Godfather', 'Godmother', 'Foster parent', 'Employer', 'Neighbor'.")


class Person(ExtendedEntity["PersonExtended"]):
    """
    Represents a person in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Person is the central object in genealogy research. It holds the individual's names,
    gender, event participations (birth, death, marriage, etc.), family links,
    addresses, and relationships to other people.

    Attributes:
        address_list: Addresses associated with this person at various points in time.
            Each Address includes city, country, state, street, postal, and date fields.
        alternate_names: Additional Name records beyond the primary_name. Examples: maiden name,
            nickname, religious name, or name after immigration. Each Name has a type field.
        attribute_list: Additional key-value properties. Examples: Occupation, Education,
            Social Security Number, National Origin. Each Attribute has type and value.
        birth_ref_index: Index into event_ref_list pointing to the birth event reference.
            -1 if no birth event is assigned. Usually 0 or null when present.
        death_ref_index: Index into event_ref_list pointing to the death event reference.
            -1 if no death event is assigned.
        event_ref_list: References to events this person participated in (EventReference objects).
            Each reference includes the event handle, role (Primary/Witness/etc.), and attributes.
        family_list: Handles of Family records where this person is a parent (spouse/partner).
            These are the families this person formed, not the family they grew up in.
        gender: Gender/sex code. 0=Unknown, 1=Male, 2=Female. Required for most analyses.
        lds_ord_list: LDS (Latter-day Saint) ordinance records associated with this person.
        parent_family_list: Handles of Family records where this person appears as a child.
            A person may have multiple parent families (e.g., biological and adoptive).
        person_ref_list: References to other people with non-family relationships.
            Examples: godparent, foster parent, employer, neighbor.
        primary_name: The main/canonical Name record for this person. Used for display and sorting.
        urls: URLs associated with this person. Examples: FindAGrave memorial, Wikipedia article.
        profile: Read-only profile summary (PersonProfile) with key events and relationships.
    """

    address_list: Optional[List[Address]] = Field(None, description="List of Address records for this person, each with city/state/country/date. Tracks residence over time.")
    alternate_names: Optional[List[Name]] = Field(None, description="Additional Name records beyond primary_name. Examples: maiden name, nickname, religious name, post-immigration name.")
    attribute_list: Optional[List[Any]] = Field(None, description="Additional key-value properties. Examples: Occupation='Farmer', Education='High school', Social Security Number='123-45-6789'.")
    birth_ref_index: Optional[int] = Field(None, description="Index into event_ref_list for the birth event reference. -1 if no birth event assigned. Coerced from string if needed.")
    death_ref_index: Optional[int] = Field(None, description="Index into event_ref_list for the death event reference. -1 if no death event assigned. Coerced from string if needed.")
    event_ref_list: Optional[List[Any]] = Field(None, description="EventReference objects for all events this person participated in (births, deaths, marriages, etc.).")
    family_list: Optional[List[str]] = Field(None, description="Handles of Family records where this person is a parent/spouse. These are families this person formed (not grew up in).")
    gender: Optional[int] = Field(None, description="Gender/sex code: 0=Unknown, 1=Male, 2=Female. Coerced from string ('0', '1', '2') if needed.")
    lds_ord_list: Optional[List[Any]] = Field(None, description="LDS ordinance records (baptism, endowment, sealing) for this person.")
    parent_family_list: Optional[List[str]] = Field(None, description="Handles of Family records where this person is a child. May include biological and adoptive families.")
    person_ref_list: Optional[List[PersonReference]] = Field(None, description="References to other people with non-family relationships. Examples: godparent, foster parent, employer.")
    primary_name: Optional[Name] = Field(None, description="Primary/canonical Name record for display and sorting. Use alternate_names for additional names.")
    urls: Optional[List[URL]] = Field(None, description="URLs associated with this person. Examples: FindAGrave memorial, Wikipedia article, Ancestry.com profile.")
    profile: Optional["PersonProfile"] = Field(None, description="Read-only profile summary with key events (birth, death) and family relationships. Auto-populated by the API.")

    @field_validator("gender", mode="before")
    @classmethod
    def validate_gender(cls, v: Any) -> Optional[int]:
        """Validate gender: optional, must be 0 (unknown), 1 (male), or 2 (female).

        Args:
            v: Gender value (0, 1, 2, string representation, or None).

        Returns:
            Integer gender code (0, 1, or 2) or None.

        Raises:
            ValueError: If gender is not 0, 1, or 2.

        Example:
            1 → 1
            "2" → 2
            "male" → ValueError (invalid string, must use numbers)
            None → None
        """
        if v is None or v == "":
            return None
        # Coerce string to int
        try:
            gender_int = int(v) if isinstance(v, str) else v
        except (ValueError, TypeError):
            raise ValueError(f"gender must be int 0-2, got '{v}'")
        if gender_int not in (0, 1, 2):
            raise ValueError(f"gender must be 0 (unknown), 1 (male), or 2 (female), got {gender_int}")
        return gender_int

    @field_validator("birth_ref_index", "death_ref_index", mode="before")
    @classmethod
    def validate_ref_index(cls, v: Any) -> Optional[int]:
        """Validate event reference index: optional, must be >= 0 if provided.

        Args:
            v: Index value (integer, string representation, or None).

        Returns:
            Non-negative integer or None.

        Raises:
            ValueError: If index is negative or not a valid integer.

        Example:
            0 → 0
            "5" → 5
            -1 → ValueError
            None → None
        """
        if v is None or v == "":
            return None
        # Coerce string to int
        try:
            index_int = int(v) if isinstance(v, str) else v
        except (ValueError, TypeError):
            raise ValueError(f"event index must be non-negative integer, got '{v}'")
        if index_int < 0:
            raise ValueError(f"event index must be >= 0, got {index_int}")
        return index_int


class PersonExtended(BaseModel):
    """
    Extended person data with fully dereferenced objects instead of just handles.

    Populated only when the extended query parameter is requested. Contains complete
    records for all objects referenced by the person.

    Attributes:
        citations: Full Citation records for all citations in citation_list.
        events: Full Event records for all events in event_ref_list.
        families: Full Family records for all families in family_list (families person is parent of).
        media: Full Media records for all items in media_list.
        notes: Full Note records for all notes in note_list.
        parent_families: Full Family records for all families in parent_family_list.
        people: Full Person records for all persons referenced (e.g., in person_ref_list).
        primary_parent_family: Full Family record for the primary parent family.
        tags: Full Tag records for all tags in tag_list.
        backlinks: Full records of all objects that reference this person.
    """

    citations: Optional[List[Any]] = Field(None, description="Full Citation records for each citation referenced by this person.")
    events: Optional[List[Any]] = Field(None, description="Full Event records for each event referenced in event_ref_list.")
    families: Optional[List[Any]] = Field(None, description="Full Family records for families where this person is a parent/spouse.")
    media: Optional[List[Any]] = Field(None, description="Full Media records for each media item attached to this person.")
    notes: Optional[List[Any]] = Field(None, description="Full Note records for each note attached to this person.")
    parent_families: Optional[List[Any]] = Field(None, description="Full Family records for all parent families (biological, adoptive, etc.).")
    people: Optional[List[Any]] = Field(None, description="Full Person records for people referenced from person_ref_list.")
    primary_parent_family: Optional[Any] = Field(None, description="Full Family record for the primary parent family (where this person grew up).")
    tags: Optional[List[Any]] = Field(None, description="Full Tag records for each tag applied to this person.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Full records of all objects (families, events, citations) that reference this person.")


class PersonProfile(BaseModel):
    """
    Read-only profile summary of a person with key events and relationships.

    Returned by the API for display purposes. Contains pre-computed display fields
    and nested profiles for birth, death, and family relationships.

    Attributes:
        handle: Unique handle (ID) of the person.
        gramps_id: Alternate user-managed identifier. Examples: 'P0001', 'I0042'.
        name_display: Full name in display format. Example: 'John Robert Smith'.
        name_given: Given/first name portion. Example: 'John Robert'.
        name_surname: Primary surname. Example: 'Smith'.
        name_suffix: Name suffix. Examples: 'Jr.', 'Sr.', 'III', 'M.D.'.
        sex: Gender identifier string. Examples: 'M' (male), 'F' (female), 'U' (unknown).
        birth: Birth event profile with date, place, and citation summary. Null if no birth event.
        death: Death event profile with date, place, and citation summary. Null if no death event.
        events: Profiles for all events this person participated in.
        families: Family profiles for families where this person is a parent.
        primary_parent_family: Family profile for the primary parent family.
        other_parent_families: Family profiles for additional parent families (e.g., adoptive).
        references: Summary of how many other objects reference this person.
    """

    handle: Optional[str] = Field(None, description="Unique handle (ID) of the person.")
    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier. Examples: 'P0001', 'I0042'.")
    name_display: Optional[str] = Field(None, description="Full name in display format. Example: 'John Robert Smith'.")
    name_given: Optional[str] = Field(None, description="Given/first name portion. Example: 'John Robert'.")
    name_surname: Optional[str] = Field(None, description="Primary surname. Example: 'Smith'.")
    name_suffix: Optional[str] = Field(None, description="Name suffix. Examples: 'Jr.', 'Sr.', 'III', 'M.D.'.")
    sex: Optional[str] = Field(None, description="Gender identifier: 'M' (male), 'F' (female), 'U' (unknown).")
    birth: Optional[Any] = Field(None, description="Birth event profile with date, place, and citation summary. Null if no birth event assigned.")
    death: Optional[Any] = Field(None, description="Death event profile with date, place, and citation summary. Null if no death event assigned.")
    events: Optional[List[Any]] = Field(None, description="Profiles for all events this person participated in.")
    families: Optional[List[Any]] = Field(None, description="Family profiles for families where this person is a parent/spouse.")
    primary_parent_family: Optional[Any] = Field(None, description="Family profile for the primary parent family (where this person grew up).")
    other_parent_families: Optional[List[Any]] = Field(None, description="Family profiles for additional parent families (e.g., adoptive, step).")
    references: Optional[Any] = Field(None, description="Summary count or list of other objects that reference this person.")


class TimelinePersonProfile(BaseModel):
    """
    Person profile with timeline context, showing a person relative to a timeline anchor person.

    Used in person timeline views where relatives and associates of the anchor person
    are displayed alongside events, with their age and relationship to the anchor noted.

    Attributes:
        handle: Unique handle (ID) of the person.
        gramps_id: Alternate user-managed identifier. Examples: 'P0001', 'I0042'.
        name_display: Full name in display format. Example: 'Mary Ann Smith'.
        name_given: Given/first name portion. Example: 'Mary Ann'.
        name_surname: Primary surname. Example: 'Smith'.
        name_suffix: Name suffix. Examples: 'Jr.', 'Sr.', 'III'.
        sex: Gender identifier: 'M', 'F', or 'U'.
        age: Age of this person at the time of the anchor event.
            Examples: '32 years', '5 months', '1 year, 3 months'.
        relationship: This person's relationship to the timeline anchor person.
            Examples: 'Father', 'Mother', 'Sibling', 'Spouse', 'Child', 'Paternal Grandfather'.
        birth: Birth event profile for this person.
        death: Death event profile for this person.
    """

    handle: Optional[str] = Field(None, description="Unique handle (ID) of the person.")
    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier. Examples: 'P0001', 'I0042'.")
    name_display: Optional[str] = Field(None, description="Full name in display format. Example: 'Mary Ann Smith'.")
    name_given: Optional[str] = Field(None, description="Given/first name portion. Example: 'Mary Ann'.")
    name_surname: Optional[str] = Field(None, description="Primary surname. Example: 'Smith'.")
    name_suffix: Optional[str] = Field(None, description="Name suffix. Examples: 'Jr.', 'Sr.', 'III'.")
    sex: Optional[str] = Field(None, description="Gender identifier: 'M' (male), 'F' (female), 'U' (unknown).")
    age: Optional[str] = Field(None, description="Age at the time of the anchor event. Examples: '32 years', '5 months', '1 year, 3 months'.")
    relationship: Optional[str] = Field(None, description="Relationship to the timeline anchor person. Examples: 'Father', 'Mother', 'Sibling', 'Spouse', 'Child', 'Paternal Grandfather'.")
    birth: Optional[Any] = Field(None, description="Birth event profile for this person.")
    death: Optional[Any] = Field(None, description="Death event profile for this person.")
