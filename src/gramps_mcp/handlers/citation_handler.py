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
Citation data handler for Gramps MCP operations.

Provides clean, direct formatting of citation data including source details,
URLs, and repository information.
"""

import logging

from ..models.api_calls import ApiCalls
from .date_handler import format_date

logger = logging.getLogger(__name__)


async def format_citation(client, tree_id: str, handle: str) -> str:
    """
    Format citation data with source details, URLs, and repository info.

    Args:
        client: Gramps API client instance
        tree_id: Family tree identifier
        handle: Citation handle

    Returns:
        Formatted citation string with source and URL details
    """
    if not handle:
        return "• **Unknown Citation**\n  No handle provided\n\n"

    try:
        citation_data = await client.make_api_call(
            api_call=ApiCalls.GET_CITATION,
            tree_id=tree_id,
            handle=handle,
            params={"extend": "all", "backlinks": True},
        )
        if not citation_data:
            return f"• **Citation {handle}**\n  Citation not found\n\n"

        gramps_id = citation_data.get("gramps_id", "")
        page = citation_data.get("page", "").strip()
        source_handle = citation_data.get("source_handle", "")
        confidence = citation_data.get("confidence", -1)
        date = citation_data.get("date", {})
        media_list = citation_data.get("media_list", [])
        note_list = citation_data.get("note_list", [])
        # Extract extended early for tags and backlinks
        extended = citation_data.get("extended", {})

        # Get source title and gramps_id
        source_title = ""
        source_gramps_id = ""
        if source_handle:
            try:
                source_data = await client.make_api_call(
                    api_call=ApiCalls.GET_SOURCE, tree_id=tree_id, handle=source_handle
                )
                if source_data:
                    source_title = source_data.get("title", "").strip()
                    source_gramps_id = source_data.get("gramps_id", "")
            except Exception:
                pass

        # First line: source title, page - gramps_id - [handle]
        first_line_parts = []
        if source_title:
            first_line_parts.append(source_title)
        if page:
            first_line_parts.append(page)

        if first_line_parts:
            first_line = f"{', '.join(first_line_parts)} - {gramps_id} - [{handle}]"
        else:
            first_line = f" - {gramps_id} - [{handle}]"
        result = first_line

        # Source navigation reference
        if source_handle:
            src_ref = f"Source: {source_gramps_id} [{source_handle}]" if source_gramps_id else f"Source: [{source_handle}]"
            result += f"\n{src_ref}"

        # Confidence level
        if confidence >= 0:
            confidence_labels = {
                0: "Very Low", 1: "Low", 2: "Normal", 3: "High", 4: "Very High"
            }
            result += f"\nConfidence: {confidence_labels.get(confidence, str(confidence))}"

        # Date line
        if date:
            formatted_date = format_date(date)
            if formatted_date != "date unknown":
                result += f"\n{formatted_date}"

        # Attached media: gramps_id(s)
        if media_list:
            media_ids = []
            for media_ref in media_list:
                if isinstance(media_ref, dict):
                    media_handle = media_ref.get("ref", "")
                    if media_handle:
                        try:
                            media_data = await client.make_api_call(
                                api_call=ApiCalls.GET_MEDIA_ITEM,
                                tree_id=tree_id,
                                handle=media_handle,
                            )
                            if media_data:
                                media_gramps_id = media_data.get("gramps_id", "")
                                if media_gramps_id:
                                    media_ids.append(
                                        f"{media_gramps_id} [{media_handle}]"
                                    )
                        except Exception:
                            continue

            if media_ids:
                result += f"\nAttached media: {', '.join(media_ids)}"

        # Attached notes: gramps_id(s)
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

        # Tags
        tag_list = citation_data.get("tag_list", [])
        if tag_list:
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

        # Attributes
        attribute_list = citation_data.get("attribute_list", [])
        if attribute_list:
            attr_strs = [
                f"{a.get('type', '')}: {a.get('value', '')}"
                for a in attribute_list
                if a.get("type") or a.get("value")
            ]
            if attr_strs:
                result += f"\nAttributes: {'; '.join(attr_strs)}"

        # Attached to: gramps ids of backlinks (using extended data)
        extended_backlinks = extended.get("backlinks", {})

        if isinstance(extended_backlinks, dict) and extended_backlinks:
            backlink_ids = []
            # Filter for entity types that reference citations (person, family, event)
            relevant_types = ["person", "family", "event"]

            for entity_type, entities in extended_backlinks.items():
                if entity_type in relevant_types and isinstance(entities, list):
                    for entity in entities:
                        if isinstance(entity, dict):
                            entity_gramps_id = entity.get("gramps_id", "")
                            entity_handle_val = entity.get("handle", "")
                            if entity_gramps_id:
                                entry = f"{entity_gramps_id}"
                                if entity_handle_val:
                                    entry += f" [{entity_handle_val}]"
                                backlink_ids.append(entry)

            if backlink_ids:
                result += f"\nAttached to: {', '.join(backlink_ids)}"

        return result + "\n\n"

    except Exception as e:
        logger.debug(f"Failed to format citation {handle}: {e}")
        return f"• **Citation {handle}**\n  Error formatting citation: {str(e)}\n\n"
