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
Utility functions for gramps_mcp.
"""

from typing import Optional

from markdownify import markdownify as md

from .models.api_calls import ApiCalls

# Mapping from entity type string to the list (GET all) API call.
# Used by resolve_handle_from_gramps_id to query by gramps_id filter.
_TYPE_TO_LIST_CALL = {
    "person": ApiCalls.GET_PEOPLE,
    "family": ApiCalls.GET_FAMILIES,
    "event": ApiCalls.GET_EVENTS,
    "place": ApiCalls.GET_PLACES,
    "citation": ApiCalls.GET_CITATIONS,
    "source": ApiCalls.GET_SOURCES,
    "repository": ApiCalls.GET_REPOSITORIES,
    "media": ApiCalls.GET_MEDIA,
    "note": ApiCalls.GET_NOTES,
    "tag": ApiCalls.GET_TAGS,
}

def html_to_markdown(html: str) -> str:
    """
    Convert HTML content to Markdown format.

    Args:
        html: HTML string to convert

    Returns:
        Markdown formatted string
    """
    if not html or not html.strip():
        return ""

    return md(html, heading_style="ATX")


async def get_gramps_id_from_handle(
    client, obj_class: str, obj_handle: str, tree_id: str
) -> str:
    """
    Convert an object handle to its gramps_id using the appropriate API call.

    Args:
        client: GrampsWebAPIClient instance
        obj_class: Object class/type (e.g., "person", "family", "source")
        obj_handle: Object handle to convert
        tree_id: Tree identifier

    Returns:
        Gramps ID if found, otherwise the original handle
    """
    try:
        obj_class_lower = obj_class.lower()

        if obj_class_lower == "person":
            obj_info = await client.make_api_call(
                api_call=ApiCalls.GET_PERSON,
                params=None,
                tree_id=tree_id,
                handle=obj_handle,
            )
        elif obj_class_lower == "family":
            obj_info = await client.make_api_call(
                api_call=ApiCalls.GET_FAMILY,
                params=None,
                tree_id=tree_id,
                handle=obj_handle,
            )
        elif obj_class_lower == "event":
            obj_info = await client.make_api_call(
                api_call=ApiCalls.GET_EVENT,
                params=None,
                tree_id=tree_id,
                handle=obj_handle,
            )
        elif obj_class_lower == "place":
            obj_info = await client.make_api_call(
                api_call=ApiCalls.GET_PLACE,
                params=None,
                tree_id=tree_id,
                handle=obj_handle,
            )
        elif obj_class_lower == "source":
            obj_info = await client.make_api_call(
                api_call=ApiCalls.GET_SOURCE,
                params=None,
                tree_id=tree_id,
                handle=obj_handle,
            )
        elif obj_class_lower == "citation":
            obj_info = await client.make_api_call(
                api_call=ApiCalls.GET_CITATION,
                params=None,
                tree_id=tree_id,
                handle=obj_handle,
            )
        elif obj_class_lower == "media":
            obj_info = await client.make_api_call(
                api_call=ApiCalls.GET_MEDIA_ITEM,
                params=None,
                tree_id=tree_id,
                handle=obj_handle,
            )
        elif obj_class_lower == "note":
            obj_info = await client.make_api_call(
                api_call=ApiCalls.GET_NOTE,
                params=None,
                tree_id=tree_id,
                handle=obj_handle,
            )
        elif obj_class_lower == "repository":
            obj_info = await client.make_api_call(
                api_call=ApiCalls.GET_REPOSITORY,
                params=None,
                tree_id=tree_id,
                handle=obj_handle,
            )
        else:
            return obj_handle

        if obj_info and "gramps_id" in obj_info:
            return obj_info["gramps_id"]
        else:
            return obj_handle

    except Exception:
        # If we can't resolve it, just return the handle
        return obj_handle


async def resolve_handle_from_gramps_id(
    client, entity_type: str, gramps_id: str, tree_id: str
) -> Optional[str]:
    """
    Resolve a user-facing gramps_id to the internal handle using the list endpoint.

    Queries the appropriate list endpoint with a gramps_id filter and returns
    the handle of the first matching record.

    Args:
        client: GrampsWebAPIClient instance.
        entity_type: Entity type string (e.g., 'person', 'family', 'event').
        gramps_id: User-facing Gramps ID (e.g., 'I0001', 'F0001', 'E0012').
        tree_id: Tree identifier.

    Returns:
        Internal handle string, or None if not found.
    """
    from .models.parameters.base_params import BaseGetMultipleParams

    api_call = _TYPE_TO_LIST_CALL.get(entity_type.lower())
    if not api_call:
        return None
    try:
        # Reason: list endpoints accept gramps_id as a filter query param,
        # returning only the matching record(s).
        filter_params = BaseGetMultipleParams(gramps_id=gramps_id)
        results = await client.make_api_call(
            api_call=api_call,
            params=filter_params,
            tree_id=tree_id,
        )
        if isinstance(results, list) and results:
            return results[0].get("handle")
        return None
    except Exception:
        return None
