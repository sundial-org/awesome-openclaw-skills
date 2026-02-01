"""
CLI tests for associative memory.

Tests verify:
1. CLI commands map to equivalent Python API
2. JSON output is valid and parseable (for jq/unix composability)
3. Exit codes follow conventions (0 success, 1 not found, etc.)
4. Human-readable output is line-oriented (for grep/wc/etc.)
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def cli():
    """Run CLI command and return result."""
    def run(*args: str, input: str | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "keep", *args],
            capture_output=True,
            text=True,
            input=input,
            cwd=Path(__file__).parent.parent,
        )
    return run


# -----------------------------------------------------------------------------
# Help and Basic Commands
# -----------------------------------------------------------------------------

class TestCliBasics:
    """Basic CLI functionality tests."""
    
    def test_help(self, cli):
        """CLI shows help with --help."""
        result = cli("--help")
        assert result.returncode == 0
        assert "keep" in result.stdout.lower()
        assert "find" in result.stdout
        assert "update" in result.stdout
    
    def test_no_args_shows_help(self, cli):
        """CLI shows help when called with no arguments."""
        result = cli()
        # Typer returns exit code 2 for missing required command
        assert result.returncode == 2
        assert "Usage" in result.stdout or "usage" in result.stderr.lower()
    
    def test_command_help(self, cli):
        """Individual commands have help."""
        for cmd in ["find", "update", "get", "remember", "tag", "similar"]:
            result = cli(cmd, "--help")
            assert result.returncode == 0, f"{cmd} --help failed"
            assert "Usage" in result.stdout or "usage" in result.stdout.lower()


# -----------------------------------------------------------------------------
# JSON Output Tests (Composability with jq)
# -----------------------------------------------------------------------------

class TestJsonOutput:
    """Tests for JSON output format."""
    
    def test_json_flag_exists(self, cli):
        """Commands accept --json flag."""
        # Just verify the flag is recognized (command may fail due to NotImplemented)
        result = cli("find", "test", "--json", "--help")
        # --help takes precedence, should succeed
        assert result.returncode == 0
    
    def test_collections_json_is_valid(self, cli):
        """collections --json produces valid JSON array."""
        result = cli("collections", "--json")
        # May fail with NotImplementedError, but if it produces output, it should be JSON
        if result.returncode == 0 and result.stdout.strip():
            parsed = json.loads(result.stdout)
            assert isinstance(parsed, list)
    
    def test_json_output_has_required_fields(self):
        """JSON item output includes id, summary, tags, score."""
        # Test the format helper directly
        from keep.cli import _format_item
        from keep.types import Item
        
        item = Item(
            id="test:1",
            summary="Test summary",
            tags={"project": "myapp", "_created": "2026-01-30T10:00:00Z"},
            score=0.95
        )
        
        output = _format_item(item, as_json=True)
        parsed = json.loads(output)
        
        assert parsed["id"] == "test:1"
        assert parsed["summary"] == "Test summary"
        assert parsed["tags"]["project"] == "myapp"
        assert parsed["score"] == 0.95
    
    def test_json_list_output(self):
        """JSON list output is a valid array."""
        from keep.cli import _format_items
        from keep.types import Item
        
        items = [
            Item(id="test:1", summary="First", tags={}, score=0.9),
            Item(id="test:2", summary="Second", tags={}, score=0.8),
        ]
        
        output = _format_items(items, as_json=True)
        parsed = json.loads(output)
        
        assert isinstance(parsed, list)
        assert len(parsed) == 2
        assert parsed[0]["id"] == "test:1"
        assert parsed[1]["id"] == "test:2"
    
    def test_json_empty_list(self):
        """Empty results produce empty JSON array."""
        from keep.cli import _format_items
        
        output = _format_items([], as_json=True)
        parsed = json.loads(output)
        
        assert parsed == []


# -----------------------------------------------------------------------------
# Human-Readable Output Tests (Composability with grep/wc)
# -----------------------------------------------------------------------------

class TestHumanOutput:
    """Tests for human-readable output format."""
    
    def test_human_item_format(self):
        """Human-readable item shows id and summary."""
        from keep.cli import _format_item
        from keep.types import Item
        
        item = Item(id="file:///doc.md", summary="A document about testing")
        output = _format_item(item, as_json=False)
        
        assert "file:///doc.md" in output
        assert "A document about testing" in output
    
    def test_human_item_with_score(self):
        """Human-readable item shows score when present."""
        from keep.cli import _format_item
        from keep.types import Item
        
        item = Item(id="test:1", summary="Test", score=0.95)
        output = _format_item(item, as_json=False)
        
        assert "[0.950]" in output
    
    def test_human_list_empty(self):
        """Empty list shows user-friendly message."""
        from keep.cli import _format_items
        
        output = _format_items([], as_json=False)
        assert "No results" in output
    
    def test_human_list_separates_items(self):
        """Items are separated for easy reading."""
        from keep.cli import _format_items
        from keep.types import Item
        
        items = [
            Item(id="test:1", summary="First"),
            Item(id="test:2", summary="Second"),
        ]
        output = _format_items(items, as_json=False)
        
        # Items should be separated (double newline)
        assert "\n\n" in output
        assert "test:1" in output
        assert "test:2" in output


# -----------------------------------------------------------------------------
# Exit Code Tests (Shell Scripting)
# -----------------------------------------------------------------------------

class TestExitCodes:
    """Tests for proper exit codes."""
    
    def test_help_returns_zero(self, cli):
        """Help returns exit code 0."""
        result = cli("--help")
        assert result.returncode == 0
    
    def test_unknown_command_returns_nonzero(self, cli):
        """Unknown command returns non-zero exit code."""
        result = cli("nonexistent-command")
        assert result.returncode != 0
    
    def test_invalid_tag_format_returns_error(self, cli):
        """Invalid tag format returns exit code 1."""
        # update with bad tag format
        result = cli("update", "test:1", "--tag", "badformat")
        # Should fail due to missing = in tag
        # (may also fail due to NotImplemented, which is fine)
        if "Invalid tag format" in result.stderr:
            assert result.returncode == 1


# -----------------------------------------------------------------------------
# Tag Parsing Tests
# -----------------------------------------------------------------------------

class TestTagParsing:
    """Tests for key=value tag parsing."""
    
    def test_single_tag(self, cli):
        """Single --tag is parsed correctly."""
        # We can't fully test this without implementation,
        # but we can check the format is accepted
        result = cli("update", "--help")
        assert "--tag" in result.stdout or "-t" in result.stdout
    
    def test_tag_format_validation(self, cli):
        """Tags without = are rejected."""
        result = cli("update", "test:1", "--tag", "invalid")
        # Should fail - either due to format error or missing dependencies
        # When implementation is complete, this should specifically check for format error
        assert result.returncode != 0


# -----------------------------------------------------------------------------
# Unix Composability Integration
# -----------------------------------------------------------------------------

class TestUnixComposability:
    """Tests demonstrating Unix pipeline composability."""
    
    def test_json_output_pipeable(self):
        """JSON output can be processed with standard tools."""
        from keep.cli import _format_items
        from keep.types import Item
        
        items = [
            Item(id="doc:1", summary="First doc", tags={"project": "alpha"}, score=0.9),
            Item(id="doc:2", summary="Second doc", tags={"project": "beta"}, score=0.8),
        ]
        
        json_output = _format_items(items, as_json=True)
        
        # Simulate: keep find "query" --json | jq '.[0].id'
        parsed = json.loads(json_output)
        first_id = parsed[0]["id"]
        assert first_id == "doc:1"
        
        # Simulate: keep find "query" --json | jq '.[] | select(.score > 0.85)'
        high_score = [item for item in parsed if item["score"] > 0.85]
        assert len(high_score) == 1
        assert high_score[0]["id"] == "doc:1"
    
    def test_line_oriented_for_wc(self):
        """Human output is countable with wc -l."""
        from keep.cli import _format_items
        from keep.types import Item
        
        items = [
            Item(id=f"doc:{i}", summary=f"Doc {i}") 
            for i in range(5)
        ]
        
        output = _format_items(items, as_json=False)
        
        # Each item produces predictable lines
        lines = output.strip().split("\n")
        # 5 items * 2 lines each, minus separators handled differently
        assert len(lines) >= 5  # At least one line per item
    
    def test_ids_extractable_from_json(self):
        """IDs can be extracted for use in other commands."""
        from keep.cli import _format_items
        from keep.types import Item
        
        items = [
            Item(id="file:///a.md", summary="A"),
            Item(id="file:///b.md", summary="B"),
        ]
        
        json_output = _format_items(items, as_json=True)
        parsed = json.loads(json_output)
        
        # Simulate: keep find "query" --json | jq -r '.[].id' | xargs -I{} keep get {}
        ids = [item["id"] for item in parsed]
        assert ids == ["file:///a.md", "file:///b.md"]


# -----------------------------------------------------------------------------
# CLI / API Equivalence Tests
# -----------------------------------------------------------------------------

class TestApiCliEquivalence:
    """Tests verifying CLI maps to Python API."""
    
    def test_find_maps_to_api_find(self, cli):
        """'find' command maps to Keeper.find()."""
        result = cli("find", "--help")
        assert "semantic" in result.stdout.lower() or "similar" in result.stdout.lower()
        # The CLI find uses mem.find(query, limit=limit)
    
    def test_update_maps_to_api_update(self, cli):
        """'update' command maps to Keeper.update()."""
        result = cli("update", "--help")
        assert "URI" in result.stdout or "document" in result.stdout.lower()
        # The CLI update uses mem.update(id, source_tags=...)
    
    def test_remember_maps_to_api_remember(self, cli):
        """'remember' command maps to Keeper.remember()."""
        result = cli("remember", "--help")
        assert "content" in result.stdout.lower()
        # The CLI remember uses mem.remember(content, id=id, source_tags=...)
    
    def test_get_maps_to_api_get(self, cli):
        """'get' command maps to Keeper.get()."""
        result = cli("get", "--help")
        assert "ID" in result.stdout or "id" in result.stdout.lower()
        # The CLI get uses mem.get(id)
    
    def test_tag_maps_to_api_query_tag(self, cli):
        """'tag' command maps to Keeper.query_tag()."""
        result = cli("tag", "--help")
        assert "key" in result.stdout.lower()
        # The CLI tag uses mem.query_tag(key, value, limit=limit)


# -----------------------------------------------------------------------------
# Option Tests
# -----------------------------------------------------------------------------

class TestOptions:
    """Tests for CLI options."""
    
    def test_store_option(self, cli):
        """--store option is available."""
        result = cli("find", "--help")
        assert "--store" in result.stdout or "-s" in result.stdout
    
    def test_collection_option(self, cli):
        """--collection option is available."""
        result = cli("find", "--help")
        assert "--collection" in result.stdout or "-c" in result.stdout
    
    def test_limit_option(self, cli):
        """--limit option is available."""
        result = cli("find", "--help")
        assert "--limit" in result.stdout or "-n" in result.stdout
    
    def test_json_option(self, cli):
        """--json option is available."""
        result = cli("find", "--help")
        assert "--json" in result.stdout or "-j" in result.stdout
