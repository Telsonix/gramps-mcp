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
Simplified parameter models for reduced token usage.
"""

from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class EntityType(str, Enum):
    """All searchable entity types in Gramps."""

    PERSON = "person"
    FAMILY = "family"
    EVENT = "event"
    PLACE = "place"
    SOURCE = "source"
    CITATION = "citation"
    MEDIA = "media"
    REPOSITORY = "repository"
    NOTE = "note"

    @classmethod
    def _missing_(cls, value: object):
        """Allow case-insensitive lookup."""
        if isinstance(value, str):
            for member in cls:
                if member.value == value.lower():
                    return member
        return None


class GetEntityType(str, Enum):
    """Entity types that support detailed get operations."""

    PERSON = "person"
    FAMILY = "family"
    EVENT = "event"
    PLACE = "place"
    SOURCE = "source"
    CITATION = "citation"
    MEDIA = "media"
    NOTE = "note"
    REPOSITORY = "repository"

    @classmethod
    def _missing_(cls, value: object):
        """Allow case-insensitive lookup."""
        if isinstance(value, str):
            for member in cls:
                if member.value == value.lower():
                    return member
        return None


class SimpleFindParams(BaseModel):
    """Simplified parameters for type-based search."""

    type: EntityType = Field(description="Entity type to search")
    gql: str = Field(description="Gramps Query Language filter")
    max_results: int = Field(default=20, description="Maximum results to return")


class SimpleSearchParams(BaseModel):
    """Simplified parameters for full-text search."""

    @field_validator("page", mode="before")
    @classmethod
    def coerce_page(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce page to int."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return int(v)
        return v

    @field_validator("pagesize", mode="before")
    @classmethod
    def coerce_pagesize(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce pagesize to int."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return int(v)
        return v

    @field_validator("max_results", mode="before")
    @classmethod
    def coerce_max_results(cls, v: Union[int, str, None]) -> Optional[int]:
        """Coerce max_results to int."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return int(v)
        return v

    @field_validator("strip", mode="before")
    @classmethod
    def coerce_strip(cls, v: Union[bool, str, None]) -> Optional[bool]:
        """Coerce strip to bool."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v) if v is not None else None

    @field_validator("semantic", mode="before")
    @classmethod
    def coerce_semantic(cls, v: Union[bool, str, None]) -> Optional[bool]:
        """Coerce semantic to bool."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v) if v is not None else None

    query: str = Field(description="Plain text search query")
    page: Optional[int] = Field(default=None, description="Page number (1-indexed)")
    pagesize: Optional[int] = Field(default=None, description="Results per page")
    max_results: Optional[int] = Field(default=None, description="Maximum results (legacy, use pagesize)")
    type: Optional[str] = Field(default=None, description="Object type filter (person,family,event,place,source,citation,media,repository,note)")
    sort: Optional[str] = Field(default=None, description="Sort field(s)")
    strip: Optional[bool] = Field(default=None, description="Strip empty values")
    locale: Optional[str] = Field(default=None, description="Locale code")
    profile: Optional[str] = Field(default=None, description="Result profile (default or full)")
    name_format: Optional[str] = Field(default=None, description="Name format string")
    semantic: Optional[bool] = Field(default=None, description="Use semantic search")


class SimpleGetParams(BaseModel):
    """Simplified parameters for getting entity details."""

    type: GetEntityType = Field(description="Entity type (person or family)")
    handle: Optional[str] = Field(default=None, description="Entity handle")
    gramps_id: Optional[str] = Field(
        default=None, description="Gramps ID (e.g., I0001 or F0001)"
    )

    @model_validator(mode="after")
    def require_exactly_one_identifier(self) -> "SimpleGetParams":
        """Enforce that exactly one of handle or gramps_id is provided."""
        if bool(self.handle) and bool(self.gramps_id):
            raise ValueError("Provide either handle or gramps_id, not both.")
        if not self.handle and not self.gramps_id:
            raise ValueError("Either handle or gramps_id is required.")
        return self


class EmptyParams(BaseModel):
    """Empty parameters for tools that don't require any input."""

    pass
