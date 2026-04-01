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
Event model definitions for the Gramps API.

This module contains the Event primary object and related models including
EventReference, EventExtended, EventProfile, LDSOrdination, and TimelineEventProfile.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

from .base_entity import ExtendedEntity
from .core_types import Date
from .references import BacklinksExtended


class EventReference(BaseModel):
    """
    A reference from a person or family to an event, with role information.

    EventReferences appear in event_ref_list on Person and Family objects and describe
    the role that the person/family played in the referenced event.

    Attributes:
        ref: Handle of the referenced Event object. Required.
        role: Role of the person/family in the event. Examples: 'Primary' (the main subject),
            'Witness', 'Family', 'Clergy', 'Informant', 'Custom'. Null defaults to 'Primary'.
        attribute_list: Attributes specific to this person's participation in the event.
            Examples: recording occupation or age at time of event.
        note_list: Handles for research notes about this event reference.
        private: True if this event reference record is confidential.
    """

    ref: str = Field(..., description="Handle of the referenced Event object. Required.")
    role: Optional[str] = Field(None, description="Role in the event. Examples: 'Primary' (main subject), 'Witness', 'Clergy', 'Informant', 'Family', 'Custom'.")
    attribute_list: Optional[List[Any]] = Field(None, description="Attributes for this person's participation. Examples: occupation or age at time of event.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about this event participation.")
    private: Optional[bool] = Field(None, description="True if this event reference record is confidential.")


class LDSOrdination(BaseModel):
    """
    Represents an LDS (Latter-day Saint) church ordinance associated with a person or family.

    LDS ordinances are unique to research on members of The Church of Jesus Christ of
    Latter-day Saints and include events like Baptism for the Dead, Endowment, and Sealing.

    Attributes:
        type: Ordinance type integer. 0=Baptism, 1=Endowment, 2=Seal to Parents,
            3=Seal to Spouse, 4=Confirmation, 5=Initiatory. Null if unspecified.
        date: Date the ordinance was performed.
        place: Handle of the Place object where the ordinance was performed.
        famc: Handle of the family object associated with this ordinance (for sealing events).
        temple: Temple abbreviation code where ordinance was performed.
            Examples: 'SLAKE' (Salt Lake City), 'PROVO' (Provo Utah).
        status: Ordinance status integer. Examples: 0=None, 1=BIC (Born in Covenant),
            2=Canceled, 3=Child, 4=Completed, 5=Dns, 6=Dns/Can, 7=Infant, 8=Pre-1970,
            9=Qualified, 10=Stillborn, 11=Submitted, 12=Uncleared.
        citation_list: Handles for citations supporting this ordinance record.
        note_list: Handles for research notes about this ordinance.
        private: True if this ordinance record is confidential.
    """

    type: Optional[int] = Field(None, description="Ordinance type: 0=Baptism, 1=Endowment, 2=Seal to Parents, 3=Seal to Spouse, 4=Confirmation, 5=Initiatory.")
    date: Optional[Date] = Field(None, description="Date the ordinance was performed.")
    place: Optional[str] = Field(None, description="Handle of the Place where the ordinance was performed.")
    famc: Optional[str] = Field(None, description="Handle of the family associated with this ordinance (for sealing events).")
    temple: Optional[str] = Field(None, description="Temple abbreviation code. Examples: 'SLAKE' (Salt Lake City), 'PROVO' (Provo Utah), 'JORDAN' (Jordan River Utah).")
    status: Optional[int] = Field(None, description="Ordinance status: 0=None, 1=BIC, 2=Canceled, 3=Child, 4=Completed, 5=Dns, 6=Dns/Can, 7=Infant, 8=Pre-1970, 9=Qualified, 10=Stillborn, 11=Submitted, 12=Uncleared.")
    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting this ordinance.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about this ordinance.")
    private: Optional[bool] = Field(None, description="True if this ordinance record is confidential.")


class Event(ExtendedEntity["EventExtended"]):
    """
    Represents an event in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Events are life occurrences or significant moments in genealogical records. Examples include births,
    deaths, marriages, divorces, emigrations, property transactions, and other milestones. Each event
    has a type, optional date, optional location, and optional description.

    Attributes:
        type: Event classification/category (string). Examples: 'Birth', 'Death', 'Marriage', 'Divorce',
            'Engagement', 'Emigration', 'Immigration', 'Baptism', 'Burial', 'Cremation', 'Probate'.
            Use get_types tool to see all valid event types. Non-empty if provided, max 100 characters.
        date: Date object with event timing information. Can include year, month, day, quality indicators
            (exact, estimated, calculated), and modifiers (before, after, about). Null if date unknown.
        place: Handle (ID) referencing the Place object where event occurred. String format, typically 20-50 chars.
            Null if place unknown or not specified.
        description: Free-form descriptive text providing additional context or notes about the event.
            Examples: 'Birth in a blizzard', 'Died of pneumonia', 'Married by Rev. Smith'. Max 500 chars.
        attribute_list: List of Attribute objects providing additional typed properties (not core fields).
            Examples: occupation recorded at birth, witness names, multiple places. Empty list if no attributes.
        profile: Summary profile object (EventProfile) with key event details for display. Read-only;
            contains simplified/aggregate information like citations count, participants, etc.
    """

    type: Optional[str] = Field(
        None,
        max_length=100,
        description="Event type/category. Examples: 'Birth', 'Death', 'Marriage'. Use get_types to see valid types. Max 100 chars.",
    )
    date: Optional[Date] = Field(
        None,
        description="Date object with event timing. Includes year, month, day, quality, modifiers. Null if unknown.",
    )
    place: Optional[str] = Field(
        None,
        max_length=50,
        description="Handle (ID) of place where event occurred. Null if unknown. Max 50 chars.",
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Free-form contextual description. Examples: 'Born in blizzard', 'Died of pneumonia'. Max 500 chars.",
    )
    attribute_list: Optional[List[Any]] = Field(
        None,
        description="List of Attribute objects with additional event properties. Examples: occupation, witness names.",
    )
    profile: Optional["EventProfile"] = Field(
        None,
        description="Summary profile (EventProfile) with key details. Read-only; auto-populated.",
    )

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v: Any) -> Optional[str]:
        """Validate and coerce type: optional, non-empty if provided, max 100 chars, trimmed."""
        if v is None or v == "":
            return None
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            return None
        if len(v) > 100:
            raise ValueError(f"type exceeds maximum length of 100 characters (got {len(v)})")
        return v

    @field_validator("place", mode="before")
    @classmethod
    def validate_place(cls, v: Any) -> Optional[str]:
        """Validate and coerce place: optional handle, non-empty if provided, max 50 chars, trimmed."""
        if v is None or v == "":
            return None
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            return None
        if len(v) > 50:
            raise ValueError(f"place handle exceeds maximum length of 50 characters (got {len(v)})")
        return v

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v: Any) -> Optional[str]:
        """Validate and coerce description: optional, non-empty if provided, max 500 chars, trimmed."""
        if v is None or v == "":
            return None
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            return None
        if len(v) > 500:
            raise ValueError(f"description exceeds maximum length of 500 characters (got {len(v)})")
        return v


class EventExtended(BaseModel):
    """
    Extended event data with fully dereferenced objects instead of just handles.

    Populated only when the extended query parameter is requested. Contains complete
    records for all objects referenced by the event.

    Attributes:
        place: Full Place record if a place handle was set on the event. Null otherwise.
        citations: Full Citation records for each handle in citation_list.
        media: Full Media records for each handle in media_list.
        notes: Full Note records for each handle in note_list.
        tags: Full Tag records for each handle in tag_list.
        backlinks: Full records of all objects that reference this event.
    """

    place: Optional[Any] = Field(None, description="Full Place record for the event location. Null if no place was set.")
    citations: Optional[List[Any]] = Field(None, description="Full Citation records for each citation referenced by this event.")
    media: Optional[List[Any]] = Field(None, description="Full Media records for each media item attached to this event.")
    notes: Optional[List[Any]] = Field(None, description="Full Note records for each note attached to this event.")
    tags: Optional[List[Any]] = Field(None, description="Full Tag records for each tag applied to this event.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Full records of all objects (people, families) that reference this event.")


class EventProfile(BaseModel):
    """
    Read-only profile summary of an event, returned by the API for display purposes.

    Contains pre-computed display fields and aggregated metadata. Not used for
    creating or updating events; populated by the API on read.

    Attributes:
        type: Resolved event type label. Examples: 'Birth', 'Marriage', 'Death'.
        date: Formatted date string for display. Examples: '25 Dec 1900', 'circa 1875'.
        place: Place handle or place profile object for the event location.
        place_name: Human-readable name of the event's location.
            Examples: 'Boston, Massachusetts, USA', 'London, England'.
        citations: Total count of citations supporting this event.
        confidence: Highest confidence level among supporting citations (0-10).
        participants: Person or family profiles that participated in this event.
        references: Count or list of objects referencing this event.
    """

    type: Optional[str] = Field(None, description="Resolved event type label. Examples: 'Birth', 'Marriage', 'Death', 'Burial'.")
    date: Optional[str] = Field(None, description="Formatted date string. Examples: '25 Dec 1900', 'circa 1875', 'before 1900'.")
    place: Optional[str] = Field(None, description="Place handle or place profile for the event location.")
    place_name: Optional[str] = Field(None, description="Human-readable location name. Examples: 'Boston, Massachusetts, USA', 'London, England'.")
    citations: Optional[int] = Field(None, description="Total citations supporting this event.")
    confidence: Optional[int] = Field(None, description="Highest confidence level (0-10) among supporting citations.")
    participants: Optional[Any] = Field(None, description="Person or family profiles that participated in this event.")
    references: Optional[Any] = Field(None, description="Count or list of objects referencing this event.")


class TimelineEventProfile(BaseModel):
    """
    Event profile with timeline context, including age of the anchor person and a display label.

    Used in person timeline views where events are displayed for a specific person's life,
    including events of relatives and ancestors contextualised with age and relationship.

    Attributes:
        type: Resolved event type label. Examples: 'Birth', 'Marriage', 'Death'.
        date: Formatted date string for display. Examples: '25 Dec 1900', 'circa 1875'.
        place: Place profile or handle for the event location.
        place_name: Human-readable location name. Examples: 'Boston, Massachusetts, USA'.
        description: Event description text. Examples: 'Died of pneumonia'.
        age: Age of the anchor person at the time of this event. Examples: '32 years', '5 months'.
        label: Generated display label incorporating relationship and event type.
            Examples: 'Birth of Father', 'Marriage of John Smith'.
        gramps_id: Alternate identifier of the event. Examples: 'E0001', 'E01658'.
        handle: Unique handle (ID) of the event.
        citations: Total citations supporting this event.
        confidence: Highest confidence level (0-10) among supporting citations.
        media: Handles of media items attached to this event.
        person: Profile of the person who is the primary subject of this event.
    """

    type: Optional[str] = Field(None, description="Resolved event type label. Examples: 'Birth', 'Marriage', 'Death', 'Burial'.")
    date: Optional[str] = Field(None, description="Formatted date string. Examples: '25 Dec 1900', 'circa 1875'.")
    place: Optional[Any] = Field(None, description="Place profile or handle for the event location.")
    place_name: Optional[str] = Field(None, description="Human-readable location name. Examples: 'Boston, Massachusetts, USA', 'London, England'.")
    description: Optional[str] = Field(None, description="Event description text. Examples: 'Died of pneumonia', 'Married at St. Mary\'s Church'.")
    age: Optional[str] = Field(None, description="Age of the anchor person at time of this event. Examples: '32 years', '5 months', '1 year, 3 months'.")
    label: Optional[str] = Field(None, description="Generated display label. Examples: 'Birth of Father', 'Marriage of John Smith', 'Death of Maternal Grandmother'.")
    gramps_id: Optional[str] = Field(None, description="Alternate identifier of the event. Examples: 'E0001', 'E01658'.")
    handle: Optional[str] = Field(None, description="Unique handle (ID) of the event.")
    citations: Optional[int] = Field(None, description="Total citations supporting this event.")
    confidence: Optional[int] = Field(None, description="Highest confidence level (0-10) among supporting citations.")
    media: Optional[List[str]] = Field(None, description="Handles of media items attached to this event.")
    person: Optional[Any] = Field(None, description="Profile of the primary subject person of this event.")
