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
Repository data handler for Gramps MCP operations.

Provides clean, direct formatting of repository data from handles.
"""

import logging

from ..models.api_calls import ApiCalls
from .date_handler import format_date

logger = logging.getLogger(__name__)


async def format_repository(client, tree_id: str, handle: str) -> str:
    """
    Format repository data with name and type.

    Args:
        client: Gramps API client instance
        tree_id: Family tree identifier
        handle: Repository handle

    Returns:
        Formatted repository string with details
    """
    if not handle:
        return ""

    try:
        repo_data = await client.make_api_call(
            api_call=ApiCalls.GET_REPOSITORY,
            tree_id=tree_id,
            handle=handle,
            params={"extend": "all"},
        )
        if not repo_data:
            return ""

        gramps_id = repo_data.get("gramps_id", "")
        name = repo_data.get("name", "").strip()
        repo_type = repo_data.get("type", "")

        # First line: type: name - gramps_id - [handle]
        first_line = f"{repo_type}: {name} - {gramps_id} - [{handle}]"
        result = first_line

        # Tags
        tag_list = repo_data.get("tag_list", [])
        if tag_list:
            extended = repo_data.get("extended", {})
            ext_tags = extended.get("tags", [])
            tag_map = {
                t.get("handle", ""): t.get("name", "")
                for t in ext_tags
                if t.get("handle")
            }
            tag_strs = []
            for h in tag_list:
                tag_name = tag_map.get(h, "")
                tag_str = (tag_name if tag_name else h) + f" [{h}]"
                tag_strs.append(tag_str)
            if tag_strs:
                result += f"\nTags: {', '.join(tag_strs)}"

        # Add URLs if present
        urls = repo_data.get("urls", [])
        for url in urls:
            path = url.get("path", "")
            desc = url.get("desc", "")
            if path:
                url_line = path
                if desc:
                    url_line += f" - {desc}"
                result += f"\n{url_line}"

        # Add notes if present - need to get actual note gramps_ids
        note_list = repo_data.get("note_list", [])
        if note_list:
            note_ids = []
            for note_handle in note_list:
                try:
                    note_data = await client.make_api_call(
                        api_call=ApiCalls.GET_NOTE, tree_id=tree_id, handle=note_handle
                    )
                    if note_data:
                        note_gramps_id = note_data.get("gramps_id", "")
                        if note_gramps_id:
                            note_ids.append(f"{note_gramps_id} [{note_handle}]")
                except Exception:
                    continue

            if note_ids:
                result += f"\nAttached notes: {', '.join(note_ids)}"

        # Addresses
        address_list = repo_data.get("address_list", [])
        if address_list:
            result += "\nAddresses:"
            for addr in address_list:
                addr_date = format_date(addr.get("date", {}))
                parts = [
                    addr.get("street", ""),
                    addr.get("locality", ""),
                    addr.get("city", ""),
                    addr.get("state", ""),
                    addr.get("postal", ""),
                    addr.get("country", ""),
                ]
                addr_parts = [p for p in parts if p]
                addr_str = ", ".join(addr_parts)
                if addr_date and addr_date != "date unknown":
                    addr_str += f" ({addr_date})"
                if addr_str:
                    result += f"\n  {addr_str}"
                phone = addr.get("phone", "")
                if phone:
                    result += f"\n  Phone: {phone}"

        return result + "\n\n"

    except Exception as e:
        logger.debug(f"Failed to format repository {handle}: {e}")
        return ""
