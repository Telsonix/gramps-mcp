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
API Response Definition Models

This package contains Pydantic models for all response schemas defined in the
Gramps Web API specification (apispec.yaml). These models represent the data
structures returned by the API endpoints.

Each module is organized by domain:
- core_types: Basic data types (Date, Name, Attribute, Address, etc.)
- person: Person objects and related models
- authentication: JWT tokens and authentication models
- references: Backlinks and reference models
- tag: Tag categorization models
- And more for other primary objects...

Example usage:
    from gramps_mcp.models.definitions import Person, PersonProfile, Date
    from gramps_mcp.models.definitions.person import PersonReference
"""

# Core types
from .core_types import (
    Address,
    Attribute,
    Date,
    Location,
    Name,
    Span,
    StyledText,
    StyledTextTag,
    Surname,
    URL,
)

# Base entity models
from .base_entity import BaseEntity, ExtendedEntity, Referenceable

# References
from .references import Backlinks, BacklinksExtended

# Person and related
from .person import Person, PersonExtended, PersonProfile, PersonReference, TimelinePersonProfile

# Family and related
from .family import ChildReference, Family, FamilyExtended, FamilyProfile

# Event and related
from .event import Event, EventExtended, EventProfile, EventReference, LDSOrdination, TimelineEventProfile

# Place and related
from .place import Place, PlaceExtended, PlaceName, PlaceProfile, PlaceReference

# Citation and related
from .source import Citation, CitationExtended, CitationProfile, RepositoryExtended, RepositoryReference, Repository, Source, SourceExtended, SourceProfile

# Media and related
from .media import Media, MediaExtended, MediaProfile, MediaReference

# Authentication
from .authentication import Credentials, JWTAccessToken, JWTAccessTokens, JWTRefreshToken, OIDCConfig, OIDCProvider, PasswordChange

# Tags
from .tag import Note, NoteExtended, Tag

__all__ = [
    # Core types
    "Address",
    "Attribute",
    "Date",
    "Location",
    "Name",
    "Span",
    "StyledText",
    "StyledTextTag",
    "Surname",
    "URL",
    # Base entity models
    "BaseEntity",
    "ExtendedEntity",
    "Referenceable",
    # References
    "Backlinks",
    "BacklinksExtended",
    # Person
    "Person",
    "PersonExtended",
    "PersonProfile",
    "PersonReference",
    "TimelinePersonProfile",
    # Family
    "ChildReference",
    "Family",
    "FamilyExtended",
    "FamilyProfile",
    # Event
    "Event",
    "EventExtended",
    "EventProfile",
    "EventReference",
    "LDSOrdination",
    "TimelineEventProfile",
    # Place
    "Place",
    "PlaceExtended",
    "PlaceName",
    "PlaceProfile",
    "PlaceReference",
    # Citation and Source
    "Citation",
    "CitationExtended",
    "CitationProfile",
    "Source",
    "SourceExtended",
    "SourceProfile",
    # Repository
    "Repository",
    "RepositoryExtended",
    "RepositoryReference",
    # Media
    "Media",
    "MediaExtended",
    "MediaProfile",
    "MediaReference",
    # Authentication
    "Credentials",
    "JWTAccessToken",
    "JWTAccessTokens",
    "JWTRefreshToken",
    "OIDCConfig",
    "OIDCProvider",
    "PasswordChange",
    # Tags and Notes
    "Note",
    "NoteExtended",
    "Tag",
]
