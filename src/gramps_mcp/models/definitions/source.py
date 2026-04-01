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
Citation, Source, and Repository model definitions for the Gramps API.

This module contains primary objects for citations, sources, and repositories,
along with their extended and profile variants.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field

from .base_entity import ExtendedEntity
from .core_types import Date
from .references import BacklinksExtended


class Citation(ExtendedEntity["CitationExtended"]):
    """
    Represents a citation of a source in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Attributes:
        source_handle: Handle to the source being cited.
        page: The page in the source material being cited.
        confidence: Confidence indicator for the information.
        date: The date of the citation.
        attribute_list: List of attributes about the citation.
        profile: Summary profile information.
    """

    source_handle: str = Field(..., description="Handle to the source being cited.")
    page: Optional[str] = Field(None, description="The page in the source material.")
    confidence: Optional[int] = Field(None, description="Confidence indicator.")
    date: Optional[Date] = Field(None, description="The date of the citation.")
    attribute_list: Optional[List[Any]] = Field(None, description="List of attributes about the citation.")
    profile: Optional["CitationProfile"] = Field(None, description="Summary profile information.")


class CitationExtended(BaseModel):
    """
    Extended citation data with full details of all referenced objects.

    Attributes:
        source: The source record for the citation.
        media: Media records for any referenced media objects.
        notes: Note records for any referenced notes.
        tags: Tag records for any referenced tags.
        backlinks: Objects referring to this citation (extended).
    """

    source: Optional[Any] = Field(None, description="Source record for the citation.")
    media: Optional[List[Any]] = Field(None, description="Media records for referenced media.")
    notes: Optional[List[Any]] = Field(None, description="Note records for referenced notes.")
    tags: Optional[List[Any]] = Field(None, description="Tag records for referenced tags.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Objects referring to this citation (extended).")


class CitationProfile(BaseModel):
    """
    Profile summary of a citation with source information.

    Attributes:
        gramps_id: Alternate user-managed identifier.
        date: Date of the citation.
        page: Page cited from.
        source: Source profile for this citation.
        references: References from other objects.
    """

    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier.")
    date: Optional[str] = Field(None, description="Date of the citation.")
    page: Optional[str] = Field(None, description="Page cited from.")
    source: Optional[Any] = Field(None, description="Source profile.")
    references: Optional[Any] = Field(None, description="References from other objects.")


class Source(ExtendedEntity["SourceExtended"]):
    """
    Represents a source in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Attributes:
        title: Title for the source.
        author: The author of the source.
        abbrev: An abbreviated name for the source.
        pubinfo: Publication information.
        reporef_list: References to repositories where source can be found.
        attribute_list: List of attributes about the source.
    """

    title: Optional[str] = Field(None, description="Title for the source.")
    author: Optional[str] = Field(None, description="The author of the source.")
    abbrev: Optional[str] = Field(None, description="Abbreviated name for the source.")
    pubinfo: Optional[str] = Field(None, description="Publication information.")
    reporef_list: Optional[List[Any]] = Field(None, description="References to repositories.")
    attribute_list: Optional[List[Any]] = Field(None, description="List of attributes about the source.")


class SourceExtended(BaseModel):
    """
    Extended source data with full details of all referenced objects.

    Attributes:
        repositories: Repository records for any referenced repositories.
        media: Media records for any referenced media objects.
        notes: Note records for any referenced notes.
        tags: Tag records for any referenced tags.
        backlinks: Objects referring to this source (extended).
    """

    repositories: Optional[List[Any]] = Field(None, description="Repository records.")
    media: Optional[List[Any]] = Field(None, description="Media records for referenced media.")
    notes: Optional[List[Any]] = Field(None, description="Note records for referenced notes.")
    tags: Optional[List[Any]] = Field(None, description="Tag records for referenced tags.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Objects referring to this source (extended).")


class SourceProfile(BaseModel):
    """
    Profile summary of a source with publication details.

    Attributes:
        title: Title for the source.
        author: The author of the source.
        pubinfo: Publication information.
        references: References from other objects.
    """

    title: Optional[str] = Field(None, description="Title for the source.")
    author: Optional[str] = Field(None, description="The author of the source.")
    pubinfo: Optional[str] = Field(None, description="Publication information.")
    references: Optional[Any] = Field(None, description="References from other objects.")


class RepositoryReference(BaseModel):
    """
    A reference to a repository and how a source can be found there.

    Attributes:
        ref: Handle of the repository referenced.
        call_number: Call number for the source at the repository.
        media_type: The media format at the repository.
        note_list: Handles for research notes about the source at repository.
        private: Whether this record is private.
    """

    ref: str = Field(..., description="Handle of the repository referenced.")
    call_number: Optional[str] = Field(None, description="Call number for source at repository.")
    media_type: Optional[str] = Field(None, description="Media format at repository.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes.")
    private: Optional[bool] = Field(None, description="Private object indicator.")


class Repository(ExtendedEntity["RepositoryExtended"]):
    """
    Represents a repository in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Attributes:
        name: Name of the repository.
        type: The type of repository (e.g., 'Library', 'Archive').
        address_list: List of addresses for the repository.
        urls: URLs associated with the repository.
    """

    name: Optional[str] = Field(None, description="Name of the repository.")
    type: Optional[str] = Field(None, description="The type of repository.")
    address_list: Optional[List[Any]] = Field(None, description="List of addresses for the repository.")
    urls: Optional[List[Any]] = Field(None, description="URLs associated with the repository.")


class RepositoryExtended(BaseModel):
    """
    Extended repository data with full details of all referenced objects.

    Attributes:
        notes: Note records for any referenced notes.
        tags: Tag records for any referenced tags.
        backlinks: Objects referring to this repository (extended).
    """

    notes: Optional[List[Any]] = Field(None, description="Note records for referenced notes.")
    tags: Optional[List[Any]] = Field(None, description="Tag records for referenced tags.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Objects referring to this repository (extended).")
