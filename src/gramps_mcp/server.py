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
MCP server main entry point with HTTP transport.

This module provides the FastAPI application and MCP server setup with
all 23 genealogy tools for Gramps Web API integration.
"""

import asyncio
import inspect
import logging
import os
import sys
from typing import Any, Dict, Optional, get_args, get_origin

from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server
from mcp.types import Tool
from pydantic import BaseModel, Field

# Import all parameter models
from .models.parameters.citation_params import CitationData
from .models.parameters.event_params import EventSaveParams
from .models.parameters.family_params import FamilySaveParams
from .models.parameters.media_params import MediaSaveParams, MediaFileUploadParams, MediaFileUpdateParams, MediaGetParams
from .models.parameters.note_params import NoteSaveParams
from .models.parameters.people_params import PersonData
from .models.parameters.place_params import PlaceSaveParams
from .models.parameters.repository_params import RepositoryData
from .models.parameters.simple_params import (
    EmptyParams,
    SimpleFindParams,
    SimpleGetParams,
    SimpleSearchParams,
)
from .models.parameters.source_params import SourceSaveParams
from .models.parameters.transactions_params import TransactionHistoryParams
from .models.parameters.delete_params import DeleteParams
from .models.parameters.relations_params import RelationParams
from .models.parameters.tag_params import TagSaveParams, TagSearchParams
from .models.parameters.living_params import LivingParams
from .models.parameters.facts_params import FactsParams
from .models.parameters.timeline_params import PeopleTimelineParams, FamiliesTimelineParams
from .models.parameters.event_params import EventSpanParams

# Import all tool functions
from .tools import (
    create_citation_tool,
    create_event_tool,
    create_family_tool,
    create_media_tool,
    create_note_tool,
    create_person_tool,
    create_place_tool,
    create_repository_tool,
    create_source_tool,
    create_tag_tool,
    delete_citation_tool,
    delete_event_tool,
    delete_family_tool,
    delete_media_tool,
    delete_note_tool,
    delete_person_tool,
    delete_place_tool,
    delete_repository_tool,
    delete_source_tool,
    delete_tag_tool,
    find_anything_tool,
    find_tags_tool,
    get_ancestors_tool,
    get_descendants_tool,
    get_facts_tool,
    get_families_timeline_tool,
    get_living_tool,
    get_media_file_tool,
    get_people_timeline_tool,
    get_recent_changes_tool,
    get_relations_all_tool,
    get_relations_tool,
    get_tree_info_tool,
    get_event_span_tool,
    get_types_tool,
    update_media_file_tool,
    upload_media_file_tool,
)
from .tools.search_basic import find_type_tool
from .tools.search_details import get_type_tool


# Simple analysis models for tools that use direct dict access
class TreeInfoParams(BaseModel):
    include_statistics: bool = Field(True, description="Include statistics")


class DescendantsParams(BaseModel):
    gramps_id: str = Field(..., description="Person ID")
    max_generations: Optional[int] = Field(
        5,
        description=(
            "Max generations to retrieve (default: 5, use higher values "
            "carefully as they can overflow context)"
        ),
    )


class AncestorsParams(BaseModel):
    gramps_id: str = Field(..., description="Person ID")
    max_generations: Optional[int] = Field(
        5,
        description=(
            "Max generations to retrieve (default: 5, use higher values "
            "carefully as they can overflow context)"
        ),
    )


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Tool registry - single source of truth for all tools
TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ========================================================================
    # Search & Retrieval Tools (3 tools)
    # ========================================================================
    "find_type": {
        "description": (
            "Search for any genealogy record type using Gramps Query Language (GQL). "
            "REQUIRED: type (person/family/event/place/source/citation/media/repository/note), "
            "gql (GQL filter expression). OPTIONAL: max_results (default 20). "
            "CRITICAL GQL RULES: "
            "1. Array properties REQUIRE [0] or .any/.all - NEVER access arrays directly as strings. "
            "2. Persons do NOT have 'birth' property. Birth/death are in event_ref_list. "
            "CORRECT GQL EXAMPLES: "
            "- Surname: primary_name.surname_list[0].surname = \"Smith\" "
            "- First name: primary_name.first_name ~ \"John\" "
            "- Any surname: primary_name.surname_list.any.surname ~ \"Smith\" "
            "- Gender (0=female, 1=male): gender = 1 "
            "- Has media: media_list "
            "- Private record: private "
            "- Has children (family): child_ref_list.length > 0 "
            "- Person has any event with description 'farmer': event_ref_list.any.ref.get_event.description ~ farmer "
            "- Event year > 1800: class = event and date.dateval[2] > 1800 "
            "- Note contains text: class = note and text.string ~ \"Smith\" "
            "WRONG (will fail or return empty): surname = x, birth.date, event_ref_list.date "
            "Returns list of matching records with handles and gramps_ids. "
            "Read the full GQL documentation at gql://documentation resource or "
            "https://github.com/DavidMStraub/gramps-ql for complete syntax reference."
        ),
        "schema": SimpleFindParams,
        "handler": find_type_tool,
    },
    "find_anything": {
        "description": (
            "Perform a full-text search across ALL genealogy records (people, families, "
            "events, places, sources, citations, notes, media, repositories). "
            "Matches text strings in record fields using full-text search or semantic search. "
            "REQUIRED: query (plain text string to search for). "
            "OPTIONAL PARAMETERS: "
            "- type (str): Filter by object type (person/family/event/place/source/citation/media/note/repository). "
            "- page (int >= 0): Page number for pagination (starts at 0). "
            "- pagesize (int > 0): Number of results per page (default 20). "
            "- sort (str): Sort field (e.g., 'name' or '-date' for descending). "
            "- strip (bool): Remove empty values from results for cleaner output. "
            "- locale (str): Localization code for multi-language support. "
            "- profile (str): Result profile ('default' or 'full' for more data). "
            "- semantic (bool): Use semantic (AI-powered) search instead of exact text match (default false). "
            "Returns: Handles, gramps_ids, and brief info of all matching records. "
            "Use for quick keyword searches without learning GQL syntax."
        ),
        "schema": SimpleSearchParams,
        "handler": find_anything_tool,
    },
    "get_type": {
        "description": (
            "Get comprehensive details for a person or family record by identifier. "
            "REQUIRED: type ('person' or 'family'), and either handle (internal key) "
            "or gramps_id (user-facing ID like 'I0001' or 'F0001', not both). "
            "Returns all details: names, relationships, events, dates, notes, media, "
            "citations. Use this after find_type/find_anything to get full record data."
        ),
        "schema": SimpleGetParams,
        "handler": get_type_tool,
    },
    # ========================================================================
    # Data Management Tools — Create/Update (10 tools)
    # ========================================================================
    "create_person": {
        "description": (
            "Create a new person record or update an existing one. "
            "REQUIRED: primary_name (plain string like 'John Smith' or full Name object), "
            "gender ('Male'/'Female'/'Unknown' or 0/1/2). "
            "OPTIONAL: handle (for updates; omit for new), alternate_names, event_ref_list, "
            "family_list, parent_family_list, urls. "
            "Plain strings for names are auto-converted: last word becomes surname. "
            "Returns new/updated person's handle and gramps_id. "
            "Use create_family AFTER creating person to attach to families."
        ),
        "schema": PersonData,
        "handler": create_person_tool,
    },
    "create_family": {
        "description": (
            "Create a new family unit or update an existing one. "
            "OPTIONAL: handle (for updates; omit for new), father_handle, mother_handle "
            "(internal handles from get_type results), child_handles (list of person handles). "
            "Use child_handles=['h1','h2'] for convenient child assignment "
            "(auto-converted to API format). "
            "Returns family's handle and gramps_id. "
            "Always create/reference persons BEFORE adding them to families."
        ),
        "schema": FamilySaveParams,
        "handler": create_family_tool,
    },
    "create_event": {
        "description": (
            "Create a new life event (Birth, Death, Marriage, Burial, etc.) or update one. "
            "REQUIRED: type (event type string). "
            "OPTIONAL: handle (for updates), date (plain '1850', '1850-06', '1850-06-15' "
            "or Gramps Date object), description, place (place handle from get_type), "
            "citation_list (handles of sources), note_list (note handles). "
            "Use get_types tool to see all valid event types. "
            "Returns event's handle and gramps_id. "
            "Link events to people via person.event_ref_list."
        ),
        "schema": EventSaveParams,
        "handler": create_event_tool,
    },
    "create_place": {
        "description": (
            "Create a new geographic location or update an existing one. "
            "REQUIRED: place_type (e.g. 'City', 'Country', 'County', 'State', 'Town'). "
            "OPTIONAL: handle (for updates), name (plain 'London' or {\"value\": \"London\"}), "
            "code, lat (latitude), long (longitude), alt_names, urls, citation_list, "
            "note_list. "
            "Use get_types tool to see all valid place types. "
            "Returns place's handle and gramps_id. "
            "Must exist before linking to events."
        ),
        "schema": PlaceSaveParams,
        "handler": create_place_tool,
    },
    "create_source": {
        "description": (
            "Create a new source document (book, website, archive record, etc.) or update one. "
            "REQUIRED: title (name of the source). "
            "OPTIONAL: handle (for updates), author, pubinfo (publication info), "
            "reporef_list (repository references). "
            "Returns source's handle and gramps_id. "
            "Must exist before creating citations that reference it. "
            "Base unit for genealogy research — each source can link to multiple citations."
        ),
        "schema": SourceSaveParams,
        "handler": create_source_tool,
    },
    "create_citation": {
        "description": (
            "Create a new citation (specific reference within a source) or update one. "
            "REQUIRED: source_handle (internal handle of the source document). "
            "OPTIONAL: handle (for updates), page (page number or location), "
            "date (plain string or Gramps Date object). "
            "Citations connect sources to claims (people, events, facts). "
            "Returns citation's handle and gramps_id. "
            "Always create source BEFORE creating citations."
        ),
        "schema": CitationData,
        "handler": create_citation_tool,
    },
    "create_note": {
        "description": (
            "Create a new textual note or update an existing one. "
            "REQUIRED: text (note content as plain string), type (note type string, "
            "e.g. 'General', 'Research', 'Source', 'To Do'). "
            "OPTIONAL: handle (for updates). "
            "Text is auto-wrapped in Gramps' StyledText format. "
            "Returns note's handle and gramps_id. "
            "Use for research notes, citations, or any supplementary text attached to records."
        ),
        "schema": NoteSaveParams,
        "handler": create_note_tool,
    },
    "create_media": {
        "description": (
            "Create a new media record (photo, document, etc. metadata) or update one. "
            "REQUIRED: desc (description of the media). "
            "OPTIONAL: handle (for updates), path (file path or URL), mime (MIME type), "
            "date (when media was created), citation_list, note_list. "
            "This creates the METADATA only — use upload_media_file to also store the actual file. "
            "Returns media's handle and gramps_id. "
            "Useful for organizing photos, documents, artifacts in the tree."
        ),
        "schema": MediaSaveParams,
        "handler": create_media_tool,
    },
    "create_repository": {
        "description": (
            "Create a new repository (archive, library, church, website, etc.) or update one. "
            "REQUIRED: name (repository name), type (repository type string, "
            "e.g. 'Archive', 'Library', 'Church', 'National Archive', 'Web'). "
            "OPTIONAL: handle (for updates), urls. "
            "Returns repository's handle and gramps_id. "
            "Repositories hold sources and help organize your research locations."
        ),
        "schema": RepositoryData,
        "handler": create_repository_tool,
    },
    # ========================================================================
    # Delete Tools (10 tools)
    # ========================================================================
    "delete_person": {
        "description": (
            "Delete a person record and all linked data. "
            "REQUIRED: Either handle (internal key) or gramps_id (e.g. 'I0001'), not both. "
            "WARNING: Deletion is permanent and cascades to related records. "
            "Use find_type or find_anything first to locate the record, then get_type "
            "to verify it's correct before deleting."
        ),
        "schema": DeleteParams,
        "handler": delete_person_tool,
    },
    "delete_family": {
        "description": (
            "Delete a family unit and its relationships. "
            "REQUIRED: Either handle or gramps_id (e.g. 'F0001'), not both. "
            "WARNING: Permanent deletion. Family relationships are removed but individuals "
            "are preserved. Verify with get_type before deleting."
        ),
        "schema": DeleteParams,
        "handler": delete_family_tool,
    },
    "delete_event": {
        "description": (
            "Delete an event record. "
            "REQUIRED: Either handle or gramps_id (e.g. 'E0012'), not both. "
            "WARNING: Permanent deletion and removes the event from all associated people. "
            "Use get_type first to confirm which event you're deleting."
        ),
        "schema": DeleteParams,
        "handler": delete_event_tool,
    },
    "delete_note": {
        "description": (
            "Delete a note record. "
            "REQUIRED: Either handle or gramps_id, not both. "
            "WARNING: Permanent deletion removes the note from all associated records."
        ),
        "schema": DeleteParams,
        "handler": delete_note_tool,
    },
    "delete_citation": {
        "description": (
            "Delete a citation record. "
            "REQUIRED: Either handle or gramps_id, not both. "
            "WARNING: Permanent deletion. Citations link sources to specific claims."
        ),
        "schema": DeleteParams,
        "handler": delete_citation_tool,
    },
    "delete_source": {
        "description": (
            "Delete a source document record. "
            "REQUIRED: Either handle or gramps_id, not both. "
            "WARNING: Permanent deletion cascades to all citations referencing this source."
        ),
        "schema": DeleteParams,
        "handler": delete_source_tool,
    },
    "delete_place": {
        "description": (
            "Delete a place record. "
            "REQUIRED: Either handle or gramps_id, not both. "
            "WARNING: Permanent deletion removes place from all associated events."
        ),
        "schema": DeleteParams,
        "handler": delete_place_tool,
    },
    "delete_repository": {
        "description": (
            "Delete a repository record. "
            "REQUIRED: Either handle or gramps_id, not both. "
            "WARNING: Permanent deletion."
        ),
        "schema": DeleteParams,
        "handler": delete_repository_tool,
    },
    "delete_media": {
        "description": (
            "Delete a media record. "
            "REQUIRED: Either handle or gramps_id, not both. "
            "WARNING: Permanent deletion removes media from all associated records."
        ),
        "schema": DeleteParams,
        "handler": delete_media_tool,
    },
    # ========================================================================
    # Analysis & Lookup Tools (12 tools)
    # ========================================================================
    "tree_stats": {
        "description": (
            "Get statistics about the entire family tree: total counts of people, families, "
            "events, places, sources, citations, media, notes, repositories. "
            "OPTIONAL: include_statistics (default true). "
            "Returns summarized tree information useful for understanding tree size and scope. "
            "No parameters needed for basic usage."
        ),
        "schema": TreeInfoParams,
        "handler": get_tree_info_tool,
    },
    "get_descendants": {
        "description": (
            "Find all descendants of a person down to N generations. "
            "REQUIRED: gramps_id or handle of starting person. "
            "OPTIONAL: max_generations (default 5, be careful with higher values — "
            "very large trees can overflow response). "
            "WARNING: This is a VERY token-heavy operation. Use sparingly. "
            "Returns hierarchical tree of all descendants. "
            "Use for family reunion planning, inheritance tracking, or tree analysis."
        ),
        "schema": DescendantsParams,
        "handler": get_descendants_tool,
    },
    "get_ancestors": {
        "description": (
            "Find all ancestors of a person going back N generations. "
            "REQUIRED: gramps_id or handle of starting person. "
            "OPTIONAL: max_generations (default 5). "
            "WARNING: VERY token-heavy operation. Keep generations low. "
            "Returns hierarchical tree of all ancestors. "
            "Use for lineage research, identifying distant cousins, or heritage analysis."
        ),
        "schema": AncestorsParams,
        "handler": get_ancestors_tool,
    },
    "recent_changes": {
        "description": (
            "Get a log of recent changes/modifications to the family tree. "
            "Shows what records were created, updated, or modified and when. "
            "OPTIONAL PARAMETERS: "
            "- page (int >= 0): Page number for pagination. "
            "- pagesize (int > 0): Number of records per page. "
            "- sort (str): Sort field (e.g., '-id' for descending by ID, default is '-id'). "
            "- old (bool): Include raw object data BEFORE the change. "
            "- new (bool): Include raw object data AFTER the change. "
            "- before (float): Unix timestamp — return only changes BEFORE this time. "
            "- after (float): Unix timestamp — return only changes AFTER this time. "
            "Returns: Transaction history with object type, action (create/update), timestamps. "
            "Useful for tracking tree modifications, auditing changes, or resuming work."
        ),
        "schema": TransactionHistoryParams,
        "handler": get_recent_changes_tool,
    },
    "get_relations": {
        "description": (
            "Calculate the relationship between two specific people. "
            "REQUIRED: Two person identifiers (gramps_id or handle). "
            "Example output: 'Second cousin once removed', 'Uncle', 'Brother-in-law'. "
            "Returns single relationship description. "
            "Use this to understand family connections and verify relationships in the tree."
        ),
        "schema": RelationParams,
        "handler": get_relations_tool,
    },
    "get_relations_all": {
        "description": (
            "Find ALL possible relationship paths between two people. "
            "REQUIRED: Two person identifiers (gramps_id or handle). "
            "Returns multiple relationship descriptions if people are related through "
            "different paths. "
            "Use for understanding complex family connections (e.g., both cousins AND "
            "in-laws through different ancestors)."
        ),
        "schema": RelationParams,
        "handler": get_relations_all_tool,
    },
    "get_living": {
        "description": (
            "Check if a person is considered living for privacy purposes. "
            "REQUIRED: gramps_id or handle of person. "
            "OPTIONAL: living proxy settings, age parameters. "
            "Returns whether person should be treated as living. "
            "Useful for privacy management — living people often have restricted info."
        ),
        "schema": LivingParams,
        "handler": get_living_tool,
    },
    "get_facts": {
        "description": (
            "Get computed facts and statistics about the family tree, optionally filtered "
            "by person (descendants, ancestors, common ancestors) or location. "
            "OPTIONAL: gramps_id/handle (for person-specific facts), living proxy policy, "
            "person filter (Descendants/Ancestors/CommonAncestor), private flag. "
            "Returns interesting derived facts: oldest people, most events, median age, etc. "
            "Use to analyze tree patterns and answer 'who' questions."
        ),
        "schema": FactsParams,
        "handler": get_facts_tool,
    },
    # ========================================================================
    # Tag Tools (3 tools)
    # ========================================================================
    "find_tags": {
        "description": (
            "List all tags in the database with optional pagination and filtering. "
            "Tags are labels for organizing records. "
            "OPTIONAL PARAMETERS: "
            "- page (int >= 0): Page number for pagination (starts at 0). "
            "- pagesize (int > 0): Number of tags per page (default 20). "
            "- sort (str): Field to sort by (e.g., 'name', '-date'). "
            "- strip (bool): Remove empty/null values from results. "
            "- locale (str): Localization code (e.g., 'en_US', 'de_DE'). "
            "- keys (str): Return only specific fields (comma-separated). "
            "- skipkeys (str): Omit specific fields (comma-separated). "
            "Returns: List of tags with names, colors, priorities, handles, and gramps_ids. "
            "Use before create_tag to check existing tags and avoid duplicates."
        ),
        "schema": TagSearchParams,
        "handler": find_tags_tool,
    },
    "create_tag": {
        "description": (
            "Create a new tag or update an existing one. "
            "REQUIRED: name (tag label, e.g. 'Needs Research', 'DNA Match', 'Historical'). "
            "OPTIONAL: handle (for updates), color (hex color #RRGGBB), priority (integer). "
            "Returns tag's handle and gramps_id. "
            "Tags help organize and categorize records across the entire tree."
        ),
        "schema": TagSaveParams,
        "handler": create_tag_tool,
    },
    "delete_tag": {
        "description": (
            "Delete a tag record. "
            "REQUIRED: Either handle or gramps_id, not both. "
            "WARNING: Permanent deletion removes tag from all records it was assigned to."
        ),
        "schema": DeleteParams,
        "handler": delete_tag_tool,
    },
    # ========================================================================
    # Timeline Tools (2 tools)
    # ========================================================================
    "get_people_timeline": {
        "description": (
            "Get a chronological timeline of all events for a list of people. "
            "Returns events sorted by date for all specified people. "
            "OPTIONAL PARAMETERS: "
            "- handles (str): Comma-separated list of person handles (e.g., 'H001,H002,H003'). "
            "- anchor (str): Handle of a person to anchor/focus the timeline. "
            "- dates (str): Date range filter (formats: '-y/m/d', 'y/m/d-y/m/d', or 'y/m/d-'). "
            "- first (bool): Include events before anchor person's first event. "
            "- last (bool): Include events after anchor person's last event. "
            "- filter (str): Use a named filter query for advanced filtering. "
            "- rules (str): JSON filter expressions for custom complex filtering. "
            "- events (str): Comma-separated event types to include (e.g., 'Birth,Death,Marriage'). "
            "- event_classes (str): Event classes to include (Primary, Family). "
            "- ratings (bool): Include citation count and confidence scores. "
            "- precision (int 1-3): Date precision level in results. "
            "- discard_empty (bool): Skip events without dates. "
            "- locale (str): Localization code for output formatting. "
            "- page (int >= 0): Page number for pagination. "
            "- pagesize (int > 0): Events per page. "
            "- strip (bool): Remove empty values from results. "
            "- keys (str): Return only specific fields. "
            "- skipkeys (str): Omit specific fields. "
            "Use for understanding life sequences, migration patterns, and family stories."
        ),
        "schema": PeopleTimelineParams,
        "handler": get_people_timeline_tool,
    },
    "get_families_timeline": {
        "description": (
            "Get a chronological timeline of all events for a list of families. "
            "Returns events sorted by date for family units and their members. "
            "OPTIONAL PARAMETERS: "
            "- handles (str): Comma-separated list of family handles (e.g., 'F001,F002,F003'). "
            "- dates (str): Date range filter (formats: '-y/m/d', 'y/m/d-y/m/d', or 'y/m/d-'). "
            "- filter (str): Use a named filter query for advanced filtering. "
            "- rules (str): JSON filter expressions for custom complex filtering. "
            "- events (str): Comma-separated event types to include (e.g., 'Marriage,Divorce'). "
            "- event_classes (str): Event classes to include (Primary, Family). "
            "- ratings (bool): Include citation count and confidence scores. "
            "- discard_empty (bool): Skip events without dates. "
            "- locale (str): Localization code for output formatting. "
            "- page (int >= 0): Page number for pagination. "
            "- pagesize (int > 0): Events per page. "
            "- strip (bool): Remove empty values from results. "
            "- keys (str): Return only specific fields. "
            "- skipkeys (str): Omit specific fields. "
            "Returns: Events for all people in the families with dates, types, descriptions. "
            "Use for understanding family history progression and significant milestones."
        ),
        "schema": FamiliesTimelineParams,
        "handler": get_families_timeline_tool,
    },
    # ========================================================================
    # Media File Tools (3 tools)
    # ========================================================================
    "get_media_file": {
        "description": (
            "Get metadata about a media file, with optional file content download. "
            "REQUIRED: Either handle or gramps_id (e.g. 'O0100'), not both. "
            "OPTIONAL: include_content (default false) — if true, downloads the actual file "
            "and includes it as base64-encoded content. "
            "max_file_size (default 50MB) — skip download if file exceeds this limit. "
            "Set to -1 for no limit (caution: large files increase response size). "
            "Returns: file description, MIME type, path, handle, checksum, and authenticated URL. "
            "✅ Use include_content=true to get the file directly without needing auth tokens — "
            "perfect for AI agents! "
            "For images, also returns displayable data URI. "
            "Example: get_media_file(gramps_id='O0100', include_content=true, max_file_size=104857600) "
            "to allow up to 100MB files."
        ),
        "schema": MediaGetParams,
        "handler": get_media_file_tool,
    },
    "upload_media_file": {
        "description": (
            "Upload and attach a new media file from the local filesystem. "
            "REQUIRED: file_path (absolute path like '/home/user/photos/grandma.jpg'). "
            "OPTIONAL: description (for creating new media object). "
            "Creates new media object with the uploaded file attached. "
            "Returns media's handle and gramps_id. "
            "Supports images (jpg, png, gif), PDFs, and other media types."
        ),
        "schema": MediaFileUploadParams,
        "handler": upload_media_file_tool,
    },
    "update_media_file": {
        "description": (
            "Replace the file attached to an existing media object. "
            "REQUIRED: handle (media object identifier), "
            "file_path (absolute path to new file). "
            "Keeps the media object but swaps out its file. "
            "Use for correcting image quality, updating documents, etc."
        ),
        "schema": MediaFileUpdateParams,
        "handler": update_media_file_tool,
    },
    # ========================================================================
    # Event & Type Reference Tools (2 tools)
    # ========================================================================
    "get_event_span": {
        "description": (
            "Calculate the time span (duration) between two events. "
            "REQUIRED: Two event handles/gramps_ids. "
            "OPTIONAL: as_age (return as person's age), precision (1-3 significant levels). "
            "Returns time difference. Perfect for 'How old was X when Y happened' questions. "
            "Use for biographical analysis and timeline understanding."
        ),
        "schema": EventSpanParams,
        "handler": get_event_span_tool,
    },
    "get_types": {
        "description": (
            "Get all valid enumerated type values used in the tree: "
            "event types (Birth, Death, Marriage, Burial, etc.), "
            "place types (City, Country, Region, etc.), name types, relationship types. "
            "RETURNS: Dictionary of all type names and their descriptions. "
            "Use this as a reference when creating new records to understand valid options. "
            "No parameters required."
        ),
        "schema": EmptyParams,
        "handler": get_types_tool,
    },
}


# Create FastMCP app with stateless HTTP (no SSE)
app = FastMCP("gramps", stateless_http=True, json_response=True)


# ============================================================================
# Dynamic FastMCP Tool Registration
# ============================================================================


# Register all tools dynamically from the registry
def register_tools():
    """Register all tools from the registry with FastMCP.

    Builds a flat function signature from each Pydantic model so that
    FastMCP exposes every field as a top-level tool parameter instead of
    nesting them under an ``arguments`` wrapper.
    """
    for tool_name, tool_config in TOOL_REGISTRY.items():
        schema = tool_config["schema"]
        handler_func = tool_config["handler"]
        description = tool_config["description"]

        # Create the async handler function with proper schema annotation
        # Pass the validated Pydantic model directly to the handler
        # Handlers will check if they receive a BaseModel and skip re-validation
        if schema == EmptyParams:
            # For tools with no parameters, make arguments optional
            async def create_handler(arguments: Optional[EmptyParams] = None, handler=handler_func):
                return await handler(arguments or {})

            create_handler.__annotations__ = {"arguments": Optional[EmptyParams]}
        else:
            async def create_handler(arguments, handler=handler_func):
                return await handler(arguments)

            create_handler.__annotations__ = {"arguments": schema}

        # Build inspect.Parameter list from Pydantic model fields
        params = []
        annotations = {}
        for field_name, field_info in schema.model_fields.items():
            has_default = (
                field_info.default is not None
                or field_info.default_factory is not None
                or not field_info.is_required()
            )
            default = (
                field_info.default
                if has_default
                else inspect.Parameter.empty
            )
            params.append(
                inspect.Parameter(
                    field_name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=default,
                )
            )
            annotations[field_name] = field_info.annotation

        async def create_handler(
            *args, handler=handler_func, model=schema, **kwargs
        ):
            # Log raw parameters received from FastMCP
            logger.info(f"[TOOL INVOKED] {tool_name} | Raw kwargs: {kwargs}")
            
            # Reason: FastMCP may wrap parameters under a 'query' key instead of
            # passing flat kwargs. Unwrap if necessary so validators work correctly.
            # Only unwrap if 'query' is the ONLY key AND its value is a dict (not a string).
            # This distinguishes between:
            #   - Wrapped: {'query': {'pagesize': '10', ...}} -> unwrap to {'pagesize': '10', ...}
            #   - Search: {'query': 'smith', 'page': '1'} -> keep as-is
            if (kwargs and 'query' in kwargs and len(kwargs) == 1 
                and isinstance(kwargs['query'], dict)):
                unwrapped_kwargs = kwargs['query']
                logger.info(f"[UNWRAP] {tool_name} | Unwrapped from query wrapper: {unwrapped_kwargs}")
            else:
                unwrapped_kwargs = kwargs
                if kwargs:
                    logger.info(f"[NO UNWRAP] {tool_name} | Using kwargs as-is (not wrapped)")
            
            # Validate using Pydantic model (invokes field_validators for type coercion)
            try:
                validated = model(**unwrapped_kwargs)
                validated_data = validated.model_dump()
                logger.info(f"[VALIDATED] {tool_name} | After type coercion: {validated_data}")
            except Exception as e:
                logger.error(f"[VALIDATION ERROR] {tool_name} | Error: {e}")
                raise
            
            return await handler(validated_data)

        # Set proper metadata so FastMCP generates a flat schema
        create_handler.__name__ = tool_name
        create_handler.__doc__ = description
        create_handler.__annotations__ = annotations
        create_handler.__signature__ = inspect.Signature(params)

        # Register with FastMCP
        app.tool(description=description)(create_handler)


register_tools()


# ============================================================================
# Resource Management
# ============================================================================


def load_resource(filename: str) -> str:
    """Load content from resources folder with error handling."""
    try:
        # Get the path to the resources directory relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        resource_path = os.path.join(current_dir, "resources", filename)

        with open(resource_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Resource file '{filename}' not found."
    except Exception as e:
        return f"Error loading resource '{filename}': {str(e)}"


@app.resource("gql://documentation")
def get_gql_documentation() -> str:
    """
    Complete GQL documentation, syntax, examples, and property
    reference for Gramps queries.
    """
    return load_resource("gql-documentation.md")


@app.resource("gramps://usage-guide")
def get_usage_guide() -> str:
    """
    IMPORTANT: Read this first before using ANY creation tools -
    explains proper genealogy workflow and tool usage order.
    """
    return load_resource("gramps-usage-guide.md")


# Add custom routes to the FastMCP app
@app.custom_route("/", ["GET"])
async def root(request):
    """Root endpoint with server information."""
    from starlette.responses import JSONResponse

    return JSONResponse(
        {
            "service": "Gramps MCP Server",
            "version": "1.0.0",
            "description": "MCP server for Gramps Web API genealogy operations",
            "mcp_endpoint": "/mcp",
            "tools_count": 39,
        }
    )


@app.custom_route("/health", ["GET"])
async def health_check(request):
    """Health check endpoint."""
    from starlette.responses import JSONResponse

    return JSONResponse(
        {"status": "healthy", "service": "Gramps MCP Server", "tools": 39}
    )


async def run_stdio_server():
    """Run the MCP server with stdio transport."""
    # Create a standard MCP server for stdio transport
    server = Server("gramps")

    @server.list_tools()
    async def handle_list_tools():
        """List all available tools."""
        return [
            Tool(
                name=tool_name,
                description=tool_config["description"],
                inputSchema=tool_config["schema"].model_json_schema(),
            )
            for tool_name, tool_config in TOOL_REGISTRY.items()
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        """Handle tool calls."""
        if name in TOOL_REGISTRY:
            return await TOOL_REGISTRY[name]["handler"](arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    # Run the server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    # Determine transport type from command line arguments or environment
    transport_type = sys.argv[1] if len(sys.argv) > 1 else "streamable-http"

    if transport_type == "stdio":
        # Run with stdio transport for CLI usage
        asyncio.run(run_stdio_server())
    else:
        # Run the FastMCP server with streamable HTTP transport
        # Configure server settings
        app.settings.host = "0.0.0.0"  # Listen on all interfaces for Docker
        app.settings.port = 8000

        # Run with streamable-http transport for production use
        app.run(transport="streamable-http")
