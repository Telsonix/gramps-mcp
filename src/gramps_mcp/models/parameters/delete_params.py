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
Delete parameters for Gramps MCP tools.

Supported API Calls:
- DELETE_PERSON: Delete a person
- DELETE_FAMILY: Delete a family
"""

from typing import Optional

from pydantic import BaseModel, Field, model_validator


class DeleteParams(BaseModel):
    """
    Parameters for deleting an entity.

    Provide exactly one of handle or gramps_id to identify the record.
    Handle is the internal opaque key (e.g. '8OUJQCUVZ0XML7BQLF').
    gramps_id is the user-facing identifier (e.g. 'I0001', 'F0001').
    """

    handle: Optional[str] = Field(None, description="Internal handle of the entity")
    gramps_id: Optional[str] = Field(
        None, description="User-facing Gramps ID (e.g. 'I0001', 'F0001', 'E0012')"
    )

    @model_validator(mode="after")
    def require_exactly_one(self) -> "DeleteParams":
        """Enforce that exactly one of handle or gramps_id is provided."""
        has_handle = bool(self.handle)
        has_gramps_id = bool(self.gramps_id)
        if has_handle and has_gramps_id:
            raise ValueError(
                "Provide either handle or gramps_id, not both. "
                "gramps_id is the user-facing ID (e.g. 'I0001'); "
                "handle is the internal key."
            )
        if not has_handle and not has_gramps_id:
            raise ValueError("Either handle or gramps_id is required.")
        return self
