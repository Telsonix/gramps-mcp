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
Media model definitions for the Gramps API.

This module contains the Media primary object and related models including
MediaReference, MediaExtended, and MediaProfile.
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

from .base_entity import ExtendedEntity
from .core_types import Date
from .references import BacklinksExtended


class MediaReference(BaseModel):
    """
    A reference from a genealogical object to a media item, with cropping and metadata.

    Used in media_list to attach a media object (photo, document, etc.) to a person,
    family, place, or other object. Supports cropping rectangles for selecting
    a region of an image (e.g., to highlight a face in a group photo).

    Attributes:
        ref: Handle of the referenced Media object. Required.
        rect: Optional cropping rectangle as [x1, y1, x2, y2] percentages (0.0-100.0).
            Example: [10.0, 5.0, 60.0, 80.0] crops to 10%-60% horizontally and 5%-80% vertically.
        attribute_list: Attributes specific to this media reference.
            Examples: caption, transcription, description of what the media shows.
        citation_list: Handles for citations supporting this media reference.
        note_list: Handles for research notes about this media reference.
        private: True if this media reference is confidential.
    """

    ref: str = Field(..., description="Handle of the referenced Media object. Required.")
    rect: Optional[List[float]] = Field(None, description="Cropping rectangle [x1, y1, x2, y2] as percentages (0-100). Example: [10.0, 5.0, 60.0, 80.0] selects a region of an image.")
    attribute_list: Optional[List[Any]] = Field(None, description="Attributes for this media reference. Examples: caption, transcription, description of what the media shows.")
    citation_list: Optional[List[str]] = Field(None, description="Handles for citations supporting this media reference.")
    note_list: Optional[List[str]] = Field(None, description="Handles for research notes about this media reference.")
    private: Optional[bool] = Field(None, description="True if this media reference is confidential.")


class Media(ExtendedEntity["MediaExtended"]):
    """
    Represents a media object (image, document, audio, video) in the genealogical database.

    Inherits core identity, reference lists, and extended fields from ExtendedEntity.

    Media objects store references to external files plus descriptive metadata.
    They can be attached to people, families, events, places, and sources via MediaReference
    objects. Supports file integrity validation via checksum.

    Attributes:
        path: File system path or URL to the media file (optional, max 255 chars).
            Examples: '/home/user/photos/family.jpg', 'relative/path/census.pdf'.
        mime: IANA media type (optional, must be 'type/subtype' format).
            Examples: 'image/jpeg', 'image/png', 'application/pdf', 'audio/mpeg', 'video/mp4'.
        desc: Human-readable description of the media contents (optional, max 255 chars).
            Examples: 'Family portrait circa 1895', '1900 US Census page 5'.
        date: Date associated with the media content (when the photo was taken, document signed, etc.).
        checksum: Hexadecimal integrity checksum for file verification (optional).
            Examples: 'a1b2c3d4e5f6', 'sha256:deadbeef...'.
        attribute_list: Additional key-value properties for this media item.
        profile: Read-only profile summary (MediaProfile). Auto-populated by the API.
    """

    path: Optional[str] = Field(
        None,
        description="File system path or URL to the media file. Examples: '/home/user/photos/family.jpg', 'documents/census.pdf'. Max 255 chars.",
    )
    mime: Optional[str] = Field(
        None,
        description="IANA media type in 'type/subtype' format. Examples: 'image/jpeg', 'application/pdf', 'audio/mpeg', 'video/mp4'. Max 255 chars.",
    )
    desc: Optional[str] = Field(
        None,
        description="Human-readable description of media contents. Examples: 'Family portrait circa 1895', '1900 US Census page 5'. Max 255 chars.",
    )
    date: Optional[Date] = Field(
        None,
        description="Date associated with the media content (e.g., when photo was taken or document was written).",
    )
    checksum: Optional[str] = Field(
        None,
        description="Hexadecimal integrity checksum for file verification. Examples: 'a1b2c3d4e5f6', 'deadbeef1234'.",
    )
    attribute_list: Optional[List[Any]] = Field(None, description="Additional key-value properties for this media item.")
    profile: Optional["MediaProfile"] = Field(None, description="Read-only profile summary with date and reference counts. Auto-populated by the API.")

    @field_validator("path", mode="before")
    @classmethod
    def validate_path(cls, v: Any) -> Optional[str]:
        """Validate path: optional, max 255 chars, trimmed.

        Args:
            v: Path value (string or None).

        Returns:
            Trimmed path string or None.

        Raises:
            ValueError: If path exceeds 255 characters.

        Example:
            "  /home/user/photo.jpg  " → "/home/user/photo.jpg"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 255:
            raise ValueError(f"path exceeds 255 chars (got {len(v)})")
        return v

    @field_validator("mime", mode="before")
    @classmethod
    def validate_mime(cls, v: Any) -> Optional[str]:
        """Validate mime: optional, IANA media type format (type/subtype).

        Args:
            v: MIME type value (string or None).

        Returns:
            Trimmed MIME type or None.

        Raises:
            ValueError: If MIME type format is invalid.

        Example:
            "image/jpeg" → "image/jpeg"
            "  text/plain  " → "text/plain"
            "invalid" → ValueError
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if "/" not in v:
            raise ValueError(f"mime must be in format 'type/subtype', got '{v}'")
        return v

    @field_validator("desc", mode="before")
    @classmethod
    def validate_desc(cls, v: Any) -> Optional[str]:
        """Validate desc: optional, max 255 chars, trimmed.

        Args:
            v: Description value (string or None).

        Returns:
            Trimmed description or None.

        Raises:
            ValueError: If description exceeds 255 characters.

        Example:
            "  Family photo  " → "Family photo"
            None → None
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        if len(v) > 255:
            raise ValueError(f"desc exceeds 255 chars (got {len(v)})")
        return v

    @field_validator("checksum", mode="before")
    @classmethod
    def validate_checksum(cls, v: Any) -> Optional[str]:
        """Validate checksum: optional, hex string format.

        Args:
            v: Checksum value (hex string or None).

        Returns:
            Checksum string or None.

        Raises:
            ValueError: If checksum contains non-hex characters.

        Example:
            "a1b2c3d4e5f6" → "a1b2c3d4e5f6"
            "ABCDEF0123456789" → "ABCDEF0123456789"
            "not_hex" → ValueError
        """
        if v is None or v == "":
            return None
        v = str(v).strip() if not isinstance(v, str) else v.strip()
        # Validate hex format (allow any length hex string)
        try:
            int(v, 16)
        except ValueError:
            raise ValueError(f"checksum must be valid hex string, got '{v}'")
        return v


class MediaExtended(BaseModel):
    """
    Extended media data with fully dereferenced objects instead of just handles.

    Populated only when the extended query parameter is requested. Contains complete
    records for all objects referenced by the media item.

    Attributes:
        citations: Full Citation records for each citation referenced by this media item.
        notes: Full Note records for each note attached to this media item.
        tags: Full Tag records for each tag applied to this media item.
        backlinks: Full records of all objects (people, families, events) that reference this media.
    """

    citations: Optional[List[Any]] = Field(None, description="Full Citation records for each citation referenced by this media item.")
    notes: Optional[List[Any]] = Field(None, description="Full Note records for each note attached to this media item.")
    tags: Optional[List[Any]] = Field(None, description="Full Tag records for each tag applied to this media item.")
    backlinks: Optional[BacklinksExtended] = Field(None, description="Full records of all objects (people, families, events, places) that reference this media item.")


class MediaProfile(BaseModel):
    """
    Read-only profile summary of a media object.

    Returned by the API for display purposes. Contains pre-computed display fields
    and a cross-reference summary of which objects use this media item.

    Attributes:
        gramps_id: Alternate user-managed identifier. Examples: 'O0001', 'M0042'.
        date: Formatted date string for the media. Examples: '25 Dec 1900', 'circa 1895'.
        references: Summary or list of objects (people, families, events) that reference
            this media item via MediaReference.
    """

    gramps_id: Optional[str] = Field(None, description="Alternate user-managed identifier. Examples: 'O0001', 'M0042'.")
    date: Optional[str] = Field(None, description="Formatted date string. Examples: '25 Dec 1900', 'circa 1895'.")
    references: Optional[Any] = Field(None, description="Summary or list of objects (people, families, events, places) referencing this media item.")
