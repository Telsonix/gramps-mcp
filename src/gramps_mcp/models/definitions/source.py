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

from pydantic import BaseModel, Field, field_validator

from .base_entity import ExtendedEntity
from .core_types import Date
from .references import BacklinksExtended


class Citation(ExtendedEntity["CitationExtended"]):
    """
    Represents a citation linking research information to a specific source.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Citations connect claims in the research database (a person's birth date, a family event,
    etc.) to the source documents that provide evidence. Each citation links to one Source
    and can specify a page reference, confidence level, and date of access.

    Attributes:
        source_handle: Handle of the Source being cited (required, max 50 chars).
            Every citation must reference exactly one source.
        page: Page or location reference within the source (optional, max 500 chars).
            Examples: 'p. 42', 'vol. 3, pp. 156-159', 'microfilm roll 1234, frame 589',
            'entry 47', 'certificate number 1234567'.
        confidence: Researcher confidence level (optional, 0-10 scale).
            0=Very Low, 1=Low, 2=Normal, 3=High, 4=Very High. Scaled 0-4 in Gramps.
        date: Date the source was accessed or the date recorded in the source.
        attribute_list: Additional key-value properties for this citation.
        profile: Read-only profile summary (CitationProfile). Auto-populated by the API.
    """

    source_handle: str = Field(
        ...,
        description="Handle of the Source being cited. Required; every citation must reference one source. Max 50 chars.",
    )
    page: Optional[str] = Field(
        None,
        description="Page or location reference within source. Examples: 'p. 42', 'vol. 3, pp. 156-159', 'microfilm roll 1234', 'certificate 1234567'. Max 500 chars.",
    )
    confidence: Optional[int] = Field(
        None,
        description="Researcher confidence level 0-4 (stored 0-10 internally): 0=Very Low, 1=Low, 2=Normal, 3=High, 4=Very High. Coerced from string if needed.",
    )
    date: Optional[Date] = Field(None, description="Date the source was accessed or the date recorded in the source.")
    attribute_list: Optional[List[Any]] = Field(None, description="Additional key-value properties for this citation.")
    profile: Optional["CitationProfile"] = Field(None, description="Read-only profile summary with source details. Auto-populated by the API.")

    @field_validator("source_handle", mode="before")
    @classmethod
    def validate_source_handle(cls, v: Any) -> str:
        """Validate source_handle: required, max 50 chars, trimmed, non-empty.

        Args:
            v: Source handle value (string).

        Returns:
            Trimmed handle string.

        Raises:
            ValueError: If handle is empty or exceeds 50 characters.

        Example:
            "  c0d0a0d0a0d0a0d0  " → "c0d0a0d0a0d0a0d0"
            "" → ValueError (required field)
        """
        if v is None or v == "":
            raise ValueError("source_handle is required")
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if v == "":
            raise ValueError("source_handle cannot be empty")
        if len(v) > 50:
            raise ValueError(f"source_handle exceeds 50 chars (got {len(v)})")
        return v

    @field_validator("page", mode="before")
    @classmethod
    def validate_page(cls, v: Any) -> Optional[str]:
        """Validate page: optional, max 500 chars, trimmed.

        Args:
            v: Page reference value (string or None).

        Returns:
            Trimmed page reference or None.

        Raises:
            ValueError: If page exceeds 500 characters.

        Example:
            "  p. 42  " → "p. 42"
            "vol. 3, pp. 156-159" → "vol. 3, pp. 156-159"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 500:
            raise ValueError(f"page exceeds 500 chars (got {len(v)})")
        return v

    @field_validator("confidence", mode="before")
    @classmethod
    def validate_confidence(cls, v: Any) -> Optional[int]:
        """Validate confidence: optional, must be in range 0-10.

        Args:
            v: Confidence value (int, string representation, or None).

        Returns:
            Integer confidence score 0-10, or None.

        Raises:
            ValueError: If confidence is outside 0-10 range.

        Example:
            0 → 0
            5 → 5
            "10" → 10
            11 → ValueError
            -1 → ValueError
            None → None
        """
        if v is None or v == "":
            return None
        try:
            conf_int = int(v) if isinstance(v, str) else v
        except (ValueError, TypeError):
            raise ValueError(f"confidence must be int 0-10, got '{v}'")
        if conf_int < 0 or conf_int > 10:
            raise ValueError(f"confidence must be 0-10, got {conf_int}")
        return conf_int


class CitationExtended(BaseModel):
    """
    Extended citation data with fully dereferenced objects instead of just handles.

    Populated only when the extended query parameter is requested. Contains complete
    records for all objects referenced by the citation.

    Attributes:
        source: Full Source record for the cited source. The source this citation references.
        media: Full Media records for each media item attached to this citation.
        notes: Full Note records for each note attached to this citation.
        tags: Full Tag records for each tag applied to this citation.
        backlinks: Full records of all objects (people, events, families) that use this citation.
    """

    source: Optional[Any] = Field(None, description="Full Source record for the source that this citation references.")
    media: Optional[List[Any]] = Field(None, description="Full Media records for each media item attached to this citation.")
    notes: Optional[List[Any]] = Field(None, description="Full Note records for each note attached to this citation.")
    tags: Optional[List[Any]] = Field(None, description="Full Tag records for each tag applied to this citation.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Full records of all objects (people, events, families, places) that use this citation.")


class CitationProfile(BaseModel):
    """
    Read-only profile summary of a citation with source details.

    Returned by the API for display purposes. Contains pre-computed display fields
    including a nested source profile.

    Attributes:
        gramps_id: Alternate user-managed identifier. Examples: 'C0001', 'C01234'.
        date: Formatted date string for the citation. Examples: '25 Dec 1900', 'circa 1895'.
        page: Page or location reference. Examples: 'p. 42', 'vol. 3, pp. 156-159'.
        source: Nested source profile summarizing the source for this citation.
        references: Summary count or list of objects that use this citation as evidence.
    """

    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier. Examples: 'C0001', 'C01234'.")
    date: Optional[str] = Field(None, description="Formatted date string. Examples: '25 Dec 1900', 'circa 1895'.")
    page: Optional[str] = Field(None, description="Page or location reference. Examples: 'p. 42', 'vol. 3, pp. 156-159', 'microfilm roll 1234'.")
    source: Optional[Any] = Field(None, description="Nested source profile summarizing the source for this citation.")
    references: Optional[Any] = Field(None, description="Summary count or list of objects that use this citation as evidence.")


class Source(ExtendedEntity["SourceExtended"]):
    """
    Represents a source document or publication in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Sources are the original documents, publications, or records that provide genealogical
    evidence. Citations reference sources. A source can be associated with repositories
    where it is physically held.

    Attributes:
        title: Full title of the source (optional, max 255 chars).
            Examples: '1900 United States Federal Census', 'Massachusetts Vital Records 1840-1910',
            'Parish Register of St. Mary\'s Church 1750-1820'.
        author: Author or creator of the source (optional, max 255 chars).
            Examples: 'U.S. Bureau of the Census', 'John Smith', 'Ancestry.com Operations'.
        abbrev: Short abbreviated name for the source (optional, max 100 chars).
            Examples: '1900 US Census', 'MA Vital Records', 'St. Mary Register'.
        pubinfo: Publication information (optional, max 500 chars).
            Examples: 'Washington DC: National Archives, 1900', 'PublishedBoston: NEHGS, 1994'.
        reporef_list: RepositoryReference objects linking to repositories holding this source.
        attribute_list: Additional key-value properties for this source.
    """

    title: Optional[str] = Field(
        None,
        description="Full source title. Examples: '1900 United States Federal Census', 'MA Vital Records 1840-1910'. Max 255 chars.",
    )
    author: Optional[str] = Field(
        None,
        description="Author or creator of the source. Examples: 'U.S. Bureau of the Census', 'John Smith', 'Ancestry.com Operations'. Max 255 chars.",
    )
    abbrev: Optional[str] = Field(
        None,
        description="Abbreviated source name for compact display. Examples: '1900 US Census', 'MA Vital Records', 'St. Mary Register'. Max 100 chars.",
    )
    pubinfo: Optional[str] = Field(
        None,
        description="Publication information. Examples: 'Washington DC: National Archives, 1900', 'Boston: NEHGS, 1994'. Max 500 chars.",
    )
    reporef_list: Optional[List[Any]] = Field(None, description="RepositoryReference objects linking this source to physical repositories where it is held.")
    attribute_list: Optional[List[Any]] = Field(None, description="Additional key-value properties for this source.")

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, v: Any) -> Optional[str]:
        """Validate title: optional, max 255 chars, trimmed.

        Args:
            v: Title value (string or None).

        Returns:
            Trimmed title or None.

        Raises:
            ValueError: If title exceeds 255 characters.

        Example:
            "  The History of New York  " → "The History of New York"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 255:
            raise ValueError(f"title exceeds 255 chars (got {len(v)})")
        return v

    @field_validator("author", mode="before")
    @classmethod
    def validate_author(cls, v: Any) -> Optional[str]:
        """Validate author: optional, max 255 chars, trimmed.

        Args:
            v: Author value (string or None).

        Returns:
            Trimmed author name or None.

        Raises:
            ValueError: If author exceeds 255 characters.

        Example:
            "  John Smith  " → "John Smith"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 255:
            raise ValueError(f"author exceeds 255 chars (got {len(v)})")
        return v

    @field_validator("abbrev", mode="before")
    @classmethod
    def validate_abbrev(cls, v: Any) -> Optional[str]:
        """Validate abbrev: optional, max 100 chars, trimmed.

        Args:
            v: Abbreviation value (string or None).

        Returns:
            Trimmed abbreviation or None.

        Raises:
            ValueError: If abbreviation exceeds 100 characters.

        Example:
            "  NY History  " → "NY History"
            "TNA HO 107" → "TNA HO 107"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 100:
            raise ValueError(f"abbrev exceeds 100 chars (got {len(v)})")
        return v

    @field_validator("pubinfo", mode="before")
    @classmethod
    def validate_pubinfo(cls, v: Any) -> Optional[str]:
        """Validate pubinfo: optional, max 500 chars, trimmed.

        Args:
            v: Publication info value (string or None).

        Returns:
            Trimmed publication info or None.

        Raises:
            ValueError: If pubinfo exceeds 500 characters.

        Example:
            "  Published in 1995 by Oxford University Press  " → "Published in 1995 by Oxford University Press"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 500:
            raise ValueError(f"pubinfo exceeds 500 chars (got {len(v)})")
        return v


class SourceExtended(BaseModel):
    """
    Extended source data with fully dereferenced objects instead of just handles.

    Populated only when the extended query parameter is requested. Contains complete
    records for all objects referenced by the source.

    Attributes:
        repositories: Full Repository records for each repository referenced in reporef_list.
        media: Full Media records for each media item attached to this source.
        notes: Full Note records for each note attached to this source.
        tags: Full Tag records for each tag applied to this source.
        backlinks: Full records of all objects (citations) that reference this source.
    """

    repositories: Optional[List[Any]] = Field(None, description="Full Repository records for each repository where this source is held.")
    media: Optional[List[Any]] = Field(None, description="Full Media records for each media item attached to this source.")
    notes: Optional[List[Any]] = Field(None, description="Full Note records for each note attached to this source.")
    tags: Optional[List[Any]] = Field(None, description="Full Tag records for each tag applied to this source.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Full records of all objects (citations) that reference this source.")


class SourceProfile(BaseModel):
    """
    Read-only profile summary of a source with publication details.

    Returned by the API for display purposes, typically nested inside CitationProfile.

    Attributes:
        title: Full or abbreviated title of the source.
            Examples: '1900 United States Federal Census', 'MA Vital Records'.
        author: Author or creator. Examples: 'U.S. Bureau of the Census', 'John Smith'.
        pubinfo: Publication information.
            Examples: 'Washington DC: National Archives, 1900'.
        references: Summary count or list of citations referencing this source.
    """

    title: Optional[str] = Field(None, description="Source title. Examples: '1900 United States Federal Census', 'MA Vital Records 1840-1910'.")
    author: Optional[str] = Field(None, description="Author or creator. Examples: 'U.S. Bureau of the Census', 'John Smith', 'Ancestry.com Operations'.")
    pubinfo: Optional[str] = Field(None, description="Publication information. Examples: 'Washington DC: National Archives, 1900', 'Boston: NEHGS, 1994'.")
    references: Optional[Any] = Field(None, description="Summary count or list of citations that reference this source.")


class RepositoryReference(BaseModel):
    """
    A reference from a Source to a Repository with location-specific details.

    Records how a source can be found at a specific repository, including the
    call number, media format available at that repository, and any research notes.

    Attributes:
        ref: Handle of the referenced Repository object. Required.
        call_number: Call number, shelf location, or accession number for this source
            at the repository. Examples: 'T9_1234_01234_00001', 'Shelf A3-Box 7', 'MS 1234'.
        media_type: Physical or digital media format at this repository.
            Examples: 'Microfilm', 'Microfiche', 'Book', 'Digital', 'Manuscript',
            'Portrait', 'Audio', 'Video'.
        note_list: Handles for research notes about accessing this source at this repository.
        private: True if this repository reference is confidential.
    """

    ref: str = Field(..., description="Handle of the referenced Repository object. Required.")
    call_number: Optional[str] = Field(None, description="Call number or shelf location. Examples: 'T9_1234_01234_00001', 'Shelf A3-Box 7', 'MS 1234', 'Accession 5678'.")
    media_type: Optional[str] = Field(None, description="Media format at this repository. Examples: 'Microfilm', 'Microfiche', 'Book', 'Digital', 'Manuscript', 'Portrait'.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about accessing this source at this repository.")
    private: Optional[bool] = Field(None, description="True if this repository reference is confidential.")


class Repository(ExtendedEntity["RepositoryExtended"]):
    """
    Represents a repository (archive, library, collection) in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Repositories are physical or digital institutions that hold genealogical sources.
    Sources reference repositories via RepositoryReference objects to record where
    original documents can be found.

    Attributes:
        name: Name of the repository (optional, max 255 chars).
            Examples: 'Library of Congress', 'National Archives and Records Administration',
            'Family History Library', 'Massachusetts State Archives', 'Ancestor.com'.
        type: Repository classification (optional, max 100 chars).
            Examples: 'Library', 'Archive', 'Museum', 'Cemetery', 'Church',
            'Government Agency', 'Newspaper', 'Personal Collection', 'Web site'.
        address_list: Addresses for this repository (physical location).
        urls: URLs for this repository. Examples: official website, catalog search page.
    """

    name: Optional[str] = Field(
        None,
        description="Repository name. Examples: 'Library of Congress', 'National Archives', 'Family History Library'. Max 255 chars.",
    )
    type: Optional[str] = Field(
        None,
        description="Repository type. Examples: 'Library', 'Archive', 'Museum', 'Cemetery', 'Church', 'Government Agency', 'Web site'. Max 100 chars.",
    )
    address_list: Optional[List[Any]] = Field(None, description="Address records for this repository's physical location(s).")
    urls: Optional[List[Any]] = Field(None, description="URLs for this repository. Examples: official website, online catalog, finding aids.")

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: Any) -> Optional[str]:
        """Validate name: optional, max 255 chars, trimmed.

        Args:
            v: Repository name value (string or None).

        Returns:
            Trimmed name or None.

        Raises:
            ValueError: If name exceeds 255 characters.

        Example:
            "  Library of Congress  " → "Library of Congress"
            "National Archives and Records Administration" → "National Archives and Records Administration"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 255:
            raise ValueError(f"name exceeds 255 chars (got {len(v)})")
        return v

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v: Any) -> Optional[str]:
        """Validate type: optional, max 100 chars, trimmed.

        Args:
            v: Repository type value (string or None).

        Returns:
            Trimmed type or None.

        Raises:
            ValueError: If type exceeds 100 characters.

        Example:
            "  Library  " → "Library"
            "Archive" → "Archive"
            "Cemetery" → "Cemetery"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 100:
            raise ValueError(f"type exceeds 100 chars (got {len(v)})")
        return v


class RepositoryExtended(BaseModel):
    """
    Extended repository data with fully dereferenced objects instead of just handles.

    Populated only when the extended query parameter is requested. Contains complete
    records for all objects referenced by the repository.

    Attributes:
        notes: Full Note records for each note attached to this repository.
        tags: Full Tag records for each tag applied to this repository.
        backlinks: Full records of all objects (sources) that reference this repository.
    """

    notes: Optional[List[Any]] = Field(None, description="Full Note records for each note attached to this repository.")
    tags: Optional[List[Any]] = Field(None, description="Full Tag records for each tag applied to this repository.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Full records of all objects (sources via RepositoryReference) that reference this repository.")
