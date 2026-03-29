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
Detail retrieval MCP tools for genealogy operations.

This module contains 2 detail retrieval tools for getting comprehensive
person and family information using direct API calls.
"""

import logging
from typing import Dict, List

from mcp.types import TextContent

from ..client import GrampsAPIError, GrampsWebAPIClient
from ..config import get_settings
from ..handlers.citation_handler import format_citation
from ..handlers.event_handler import format_event
from ..handlers.family_detail_handler import format_family_detail
from ..handlers.media_handler import format_media
from ..handlers.note_handler import format_note
from ..handlers.person_detail_handler import format_person_detail
from ..handlers.place_handler import format_place
from ..handlers.repository_handler import format_repository
from ..handlers.source_handler import format_source
from ..models.api_calls import ApiCalls
from .search_basic import with_client

logger = logging.getLogger(__name__)


def _get_arg(arguments, key, default=None):
    """Get argument value from either dict or BaseModel."""
    from pydantic import BaseModel

    if isinstance(arguments, BaseModel):
        return getattr(arguments, key, default)
    return arguments.get(key, default)


def _format_error_response(error: Exception, operation: str) -> List[TextContent]:
    """Format error into user-friendly MCP response."""
    if isinstance(error, GrampsAPIError):
        error_msg = str(error)
    else:
        error_msg = f"Unexpected error during {operation}: {str(error)}"

    logger.error(f"Tool error in {operation}: {error_msg}")
    return [TextContent(type="text", text=f"Error: {error_msg}")]


async def get_entity_tool(arguments) -> List[TextContent]:
    """Universal get tool for any entity type details."""
    entity_type = _get_arg(arguments, "type")
    # Convert enum to string value if needed
    if hasattr(entity_type, "value"):
        entity_type = entity_type.value
    
    handle = _get_arg(arguments, "handle")
    gramps_id = _get_arg(arguments, "gramps_id")

    # Map entity type to the corresponding list API call
    api_call_map = {
        "person": ApiCalls.GET_PEOPLE,
        "family": ApiCalls.GET_FAMILIES,
        "event": ApiCalls.GET_EVENTS,
        "place": ApiCalls.GET_PLACES,
        "source": ApiCalls.GET_SOURCES,
        "citation": ApiCalls.GET_CITATIONS,
        "media": ApiCalls.GET_MEDIA,
        "note": ApiCalls.GET_NOTES,
        "repository": ApiCalls.GET_REPOSITORIES,
    }

    if entity_type not in api_call_map:
        return [TextContent(type="text", text=f"Unsupported entity type: {entity_type}")]

    # If gramps_id provided but no handle, resolve via the API's native gramps_id
    # query parameter (avoids GQL parsing issues)
    if gramps_id and not handle:
        settings = get_settings()
        tree_id = settings.gramps_tree_id
        client = GrampsWebAPIClient()
        try:
            results = await client.make_api_call(
                api_call=api_call_map[entity_type],
                params={"gramps_id": gramps_id},
                tree_id=tree_id,
            )
            if isinstance(results, list) and len(results) > 0:
                handle = results[0].get("handle")
            elif isinstance(results, dict):
                handle = results.get("handle")
        finally:
            await client.close()

    if not handle:
        return [TextContent(type="text", text=f"Could not find {entity_type} with the provided identifier.")]

    return await get_entity_tool(entity_type, handle)


@with_client
async def get_entity_tool(client, entity_type: str, handle: str) -> List[TextContent]:
    """Get details for any entity type: person, family, event, place, source, citation, media, note, or repository."""
    try:
        settings = get_settings()
        tree_id = settings.gramps_tree_id

        format_fn_map = {
            "person": lambda: format_person_detail(client, tree_id, handle),
            "family": lambda: format_family_detail(client, tree_id, handle),
            "event": lambda: format_event(client, tree_id, handle),
            "place": lambda: format_place(client, tree_id, handle),
            "source": lambda: format_source(client, tree_id, handle),
            "citation": lambda: format_citation(client, tree_id, handle),
            "media": lambda: format_media(client, tree_id, handle),
            "note": lambda: format_note(client, tree_id, handle),
            "repository": lambda: format_repository(client, tree_id, handle),
        }

        format_fn = format_fn_map.get(entity_type)
        if format_fn is None:
            return [TextContent(type="text", text=f"No formatter available for entity type: {entity_type}")]

        formatted = await format_fn()
        return [TextContent(type="text", text=formatted)]

    except Exception as e:
        return _format_error_response(e, f"{entity_type} details retrieval")
