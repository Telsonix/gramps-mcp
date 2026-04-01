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

from pydantic import BaseModel, Field

from .base_entity import ExtendedEntity
from .core_types import Date
from .references import BacklinksExtended


class EventReference(BaseModel):
    """
    A reference to an event with role information.

    Attributes:
        ref: The handle of the event referenced.
        role: Role of the person in the event.
        attribute_list: Attributes related to the person's role.
        note_list: Handles for research notes about the event.
        private: Whether this record is private.
    """

    ref: str = Field(..., description="The handle of the event referenced.")
    role: Optional[str] = Field(None, description="Role of the person in the event.")
    attribute_list: Optional[List[Any]] = Field(None, description="Attributes related to the person's role.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about the event.")
    private: Optional[bool] = Field(None, description="Private object indicator.")


class LDSOrdination(BaseModel):
    """
    Represents an LDS (Latter-day Saint) ordinance event.

    Attributes:
        type: Type of the ordinance.
        date: Date of the ordinance.
        place: Handle to location of the ordinance.
        famc: Family handle.
        temple: Temple where the ordinance was held.
        status: Status of the ordinance.
        citation_list: Handles for citations supporting the ordinance.
        note_list: Handles for research notes about the ordinance.
        private: Whether this record is private.
    """

    type: Optional[int] = Field(None, description="Type of the ordinance.")
    date: Optional[Date] = Field(None, description="Date of the ordinance.")
    place: Optional[str] = Field(None, description="Handle to location of the ordinance.")
    famc: Optional[str] = Field(None, description="Family.")
    temple: Optional[str] = Field(None, description="Temple the ordinance was held at.")
    status: Optional[int] = Field(None, description="Status of the ordinance.")
    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting the ordinance.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about the ordinance.")
    private: Optional[bool] = Field(None, description="Private object indicator.")


class Event(ExtendedEntity["EventExtended"]):
    """
    Represents an event in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Attributes:
        type: The type of event (e.g., 'Birth', 'Marriage').
        date: The date of the event.
        place: Handle to the place record where event occurred.
        description: A description for the event.
        attribute_list: List of attributes about the event.
        profile: Summary profile information.
    """

    type: Optional[str] = Field(None, description="The type of event.")
    date: Optional[Date] = Field(None, description="The date of the event.")
    place: Optional[str] = Field(None, description="Handle to the place where event occurred.")
    description: Optional[str] = Field(None, description="A description for the event.")
    attribute_list: Optional[List[Any]] = Field(None, description="List of attributes about the event.")
    profile: Optional["EventProfile"] = Field(None, description="Summary profile information.")


class EventExtended(BaseModel):
    """
    Extended event data with full details of all referenced objects.

    Attributes:
        place: The place record if a place was referenced.
        citations: Citation records for any referenced citations.
        media: Media records for any referenced media objects.
        notes: Note records for any referenced notes.
        tags: Tag records for any referenced tags.
        backlinks: Objects referring to this event (extended).
    """

    place: Optional[Any] = Field(None, description="Place record if a place was referenced.")
    citations: Optional[List[Any]] = Field(None, description="Citation records for referenced citations.")
    media: Optional[List[Any]] = Field(None, description="Media records for referenced media objects.")
    notes: Optional[List[Any]] = Field(None, description="Note records for referenced notes.")
    tags: Optional[List[Any]] = Field(None, description="Tag records for referenced tags.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Objects referring to this event (extended).")


class EventProfile(BaseModel):
    """
    Profile summary of an event with citations and participants.

    Attributes:
        type: Type of the event.
        date: Date of the event.
        place: Place of the event.
        place_name: Name of the event's place.
        citations: Total citations supporting the event.
        confidence: Highest confidence rating among supporting citations.
        participants: People or families participating in event.
        references: References from other objects.
    """

    type: Optional[str] = Field(None, description="Type of the event.")
    date: Optional[str] = Field(None, description="Date of the event.")
    place: Optional[str] = Field(None, description="Place of the event.")
    place_name: Optional[str] = Field(None, description="Name of the event's place.")
    citations: Optional[int] = Field(None, description="Total citations supporting the event.")
    confidence: Optional[int] = Field(None, description="Highest confidence rating among supporting citations.")
    participants: Optional[Any] = Field(None, description="People or families participating in the event.")
    references: Optional[Any] = Field(None, description="References from other objects.")


class TimelineEventProfile(BaseModel):
    """
    Event profile with timeline context including age and description.

    Attributes:
        type: Type of the event.
        date: Date of the event.
        place: Place profile of the event.
        place_name: Name of the event's place.
        description: The event description.
        age: Age of the person at the time of the event.
        label: Generated label accounting for relationships.
        gramps_id: Alternate user-managed identifier.
        handle: Unique identifier for the event.
        citations: Total citations supporting the event.
        confidence: Highest confidence rating among supporting citations.
        media: List of media handles for the event.
        person: Person profile participating in the event.
    """

    type: Optional[str] = Field(None, description="Type of the event.")
    date: Optional[str] = Field(None, description="Date of the event.")
    place: Optional[Any] = Field(None, description="Place profile of the event.")
    place_name: Optional[str] = Field(None, description="Name of the event's place.")
    description: Optional[str] = Field(None, description="The event description.")
    age: Optional[str] = Field(None, description="Age of person at the time of event.")
    label: Optional[str] = Field(None, description="Generated label for the event type.")
    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier.")
    handle: Optional[str] = Field(None, description="Unique identifier for the event.")
    citations: Optional[int] = Field(None, description="Total citations supporting the event.")
    confidence: Optional[int] = Field(None, description="Highest confidence rating.")
    media: Optional[List[str]] = Field(None, description="Media handles for the event.")
    person: Optional[Any] = Field(None, description="Person profile participating in event.")
