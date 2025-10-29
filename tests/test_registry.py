"""Tests for Registry class compression functionality."""

import gzip
import json
import lzma
import tempfile
from pathlib import Path

import pytest

from randonneur_data import DEFAULT_DATA_DIR, Registry


def create_minimal_datapackage(name: str, size: int = 100) -> dict:
    """Create a minimal valid datapackage structure."""
    return {
        "name": name,
        "description": f"Test datapackage {name}",
        "contributors": [
            {
                "title": "Test Author",
                "path": "https://example.com",
                "role": "author",
            }
        ],
        "mapping": {
            "source": {
                "expression language": "like JSONPath",
                "labels": {"identifier": "test"},
            },
            "target": {
                "expression language": "XPath",
                "labels": {"identifier": "test"},
            },
        },
        "source_id": "test-source",
        "target_id": "test-target",
        "graph_context": ["edges"],
        "licenses": [
            {
                "name": "CC BY 4.0",
                "path": "https://creativecommons.org/licenses/by/4.0/",
                "title": "Creative Commons Attribution 4.0 International",
            }
        ],
        # Add padding to control file size
        "padding": "x" * size,
    }


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def registry(temp_dir):
    """Create a Registry instance with a temporary directory."""
    registry_file = temp_dir / "registry.json"
    return Registry(filepath=registry_file)


class TestGzipCompression:
    """Tests for .gz file compression and decompression."""

    def test_add_file_creates_gz_for_large_files(self, registry, temp_dir):
        """Test that large files (>200KB) are compressed to .gz format."""
        # Create a large test file (>200KB) in a separate source directory
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        test_file = source_dir / "test-large.json"
        datapackage = create_minimal_datapackage("test-large", size=250000)
        
        with open(test_file, "w") as f:
            json.dump(datapackage, f)
        
        # Mock validate_file to skip validation
        registry.validate_file = lambda x: None
        
        result_path = registry.add_file(test_file)
        
        # Check that file was created as .gz
        assert result_path.suffix == ".gz"
        assert result_path.name == "test-large.gz"
        
        # Check registry entry
        metadata = registry["test-large"]
        assert metadata["compression"] == "gzip"
        assert metadata["filename"] == "test-large.gz"
        
        # Verify .gz file exists and is readable
        assert result_path.exists()
        with gzip.open(result_path, "rt", encoding="utf-8") as gz_file:
            loaded_data = json.load(gz_file)
        assert loaded_data["name"] == "test-large"

    def test_add_file_keeps_small_files_uncompressed(self, registry, temp_dir):
        """Test that small files (<200KB) remain uncompressed."""
        # Create a small test file in a separate source directory
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        test_file = source_dir / "test-small.json"
        datapackage = create_minimal_datapackage("test-small", size=100)
        
        with open(test_file, "w") as f:
            json.dump(datapackage, f)
        
        # Mock validate_file to skip validation
        registry.validate_file = lambda x: None
        
        result_path = registry.add_file(test_file)
        
        # Check that file was not compressed
        assert result_path.suffix == ".json"
        assert result_path.name == "test-small.json"
        
        # Check registry entry
        metadata = registry["test-small"]
        assert metadata["compression"] is False
        assert metadata["filename"] == "test-small.json"

    def test_get_file_loads_gz_files(self, registry, temp_dir):
        """Test that get_file correctly loads .gz compressed files."""
        # Create and register a .gz file manually
        datapackage = create_minimal_datapackage("test-gz-load", size=100)
        gz_file = temp_dir / "test-gz-load.gz"
        
        with gzip.open(gz_file, "wt", encoding="utf-8") as gz:
            json.dump(datapackage, gz)
        
        # Register it manually
        registry["test-gz-load"] = {
            "name": "test-gz-load",
            "filename": "test-gz-load.gz",
            "compression": "gzip",
        }
        
        # Test loading
        loaded_data = registry.get_file("test-gz-load")
        assert loaded_data["name"] == "test-gz-load"
        assert loaded_data["description"] == "Test datapackage test-gz-load"

    def test_get_file_loads_uncompressed_files(self, registry, temp_dir):
        """Test that get_file correctly loads uncompressed files."""
        datapackage = create_minimal_datapackage("test-uncompressed", size=100)
        json_file = temp_dir / "test-uncompressed.json"
        
        with open(json_file, "w") as f:
            json.dump(datapackage, f)
        
        # Register it manually
        registry["test-uncompressed"] = {
            "name": "test-uncompressed",
            "filename": "test-uncompressed.json",
            "compression": False,
        }
        
        # Test loading
        loaded_data = registry.get_file("test-uncompressed")
        assert loaded_data["name"] == "test-uncompressed"
        assert loaded_data["description"] == "Test datapackage test-uncompressed"


class TestBackwardCompatibility:
    """Tests for backward compatibility with .xz files."""

    def test_get_file_loads_existing_xz_files(self, registry, temp_dir):
        """Test that get_file can still load existing .xz (lzma) files."""
        # Create and register an .xz file manually (simulating old format)
        datapackage = create_minimal_datapackage("test-xz-backward", size=100)
        xz_file = temp_dir / "test-xz-backward.xz"
        
        with lzma.open(xz_file, "wb") as xz:
            xz.write(json.dumps(datapackage).encode("utf-8"))
        
        # Register it manually with old format
        registry["test-xz-backward"] = {
            "name": "test-xz-backward",
            "filename": "test-xz-backward.xz",
            "compression": "lzma",
        }
        
        # Test loading
        loaded_data = registry.get_file("test-xz-backward")
        assert loaded_data["name"] == "test-xz-backward"
        assert loaded_data["description"] == "Test datapackage test-xz-backward"

    def test_gzip_and_lzma_both_supported(self, registry, temp_dir):
        """Test that both gzip and lzma compressed files can be loaded."""
        # Create gzip file
        gz_datapackage = create_minimal_datapackage("test-gz", size=100)
        gz_file = temp_dir / "test-gz.gz"
        with gzip.open(gz_file, "wt", encoding="utf-8") as gz:
            json.dump(gz_datapackage, gz)
        
        registry["test-gz"] = {
            "name": "test-gz",
            "filename": "test-gz.gz",
            "compression": "gzip",
        }
        
        # Create lzma file
        xz_datapackage = create_minimal_datapackage("test-xz", size=100)
        xz_file = temp_dir / "test-xz.xz"
        with lzma.open(xz_file, "wb") as xz:
            xz.write(json.dumps(xz_datapackage).encode("utf-8"))
        
        registry["test-xz"] = {
            "name": "test-xz",
            "filename": "test-xz.xz",
            "compression": "lzma",
        }
        
        # Test both can be loaded
        gz_data = registry.get_file("test-gz")
        xz_data = registry.get_file("test-xz")
        
        assert gz_data["name"] == "test-gz"
        assert xz_data["name"] == "test-xz"


class TestCompressionEdgeCases:
    """Tests for edge cases in compression logic."""

    def test_exact_threshold_size(self, registry, temp_dir):
        """Test behavior at exactly 200KB threshold."""
        # Create a file at exactly 200KB in a separate source directory
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        test_file = source_dir / "test-threshold.json"
        datapackage = create_minimal_datapackage("test-threshold", size=200000)
        
        with open(test_file, "w") as f:
            json.dump(datapackage, f)
        
        file_size = test_file.stat().st_size
        
        # Mock validate_file to skip validation
        registry.validate_file = lambda x: None
        
        result_path = registry.add_file(test_file)
        
        # Files at exactly 200KB should NOT be compressed (size > 2e5, not >=)
        if file_size > 200000:
            assert result_path.suffix == ".gz"
            assert registry["test-threshold"]["compression"] == "gzip"
        else:
            assert result_path.suffix == ".json"
            assert registry["test-threshold"]["compression"] is False

    def test_gzip_file_integrity(self, registry, temp_dir):
        """Test that .gz files maintain data integrity."""
        # Create a complex datapackage in a separate source directory
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        test_file = source_dir / "test-complex.json"
        complex_datapackage = create_minimal_datapackage("test-complex", size=250000)
        complex_datapackage["nested"] = {
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "special_chars": "test with émojis 🎉 and unicode 中文",
        }
        
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(complex_datapackage, f, ensure_ascii=False)
        
        # Mock validate_file to skip validation
        registry.validate_file = lambda x: None
        
        result_path = registry.add_file(test_file)
        
        # Load and verify integrity
        loaded_data = registry.get_file("test-complex")
        assert loaded_data["name"] == "test-complex"
        assert loaded_data["nested"]["list"] == [1, 2, 3]
        assert loaded_data["nested"]["dict"]["key"] == "value"
        assert loaded_data["nested"]["special_chars"] == "test with émojis 🎉 and unicode 中文"


class TestRealRegistry:
    """Tests using the actual library registry.json and data files."""

    @pytest.fixture
    def default_registry(self):
        """Create a Registry instance using the default data directory."""
        return Registry()

    def test_registry_loads_from_default_location(self, default_registry):
        """Test that default registry loads from the library data directory."""
        assert len(default_registry) > 0
        assert default_registry.data_dir == DEFAULT_DATA_DIR

    def test_registry_contains_expected_entries(self, default_registry):
        """Test that registry contains expected datapackage entries."""
        # Check for some known entries
        assert "simapro-ecoinvent-3.10-cutoff" in default_registry
        assert "generic-brightway-unit-conversions" in default_registry
        
        # Verify entry structure
        entry = default_registry["simapro-ecoinvent-3.10-cutoff"]
        assert "name" in entry
        assert "description" in entry
        assert "filename" in entry
        assert "compression" in entry
        assert "mapping" in entry
        assert "contributors" in entry

    def test_load_gzip_file_from_registry(self, default_registry):
        """Test loading a .gz compressed file from the real registry."""
        # Find an entry with gzip compression
        gzip_entry = None
        for entry_name, entry_data in default_registry.items():
            if entry_data.get("compression") == "gzip":
                gzip_entry = (entry_name, entry_data)
                break
        
        if gzip_entry is None:
            pytest.skip("No gzip-compressed files found in registry")
        
        entry_name, entry_data = gzip_entry
        
        # Load the file
        data = default_registry.get_file(entry_name)
        
        # Verify expected structure
        assert "name" in data
        assert data["name"] == entry_name
        assert "description" in data
        assert "mapping" in data
        assert "source_id" in data
        assert "target_id" in data
        
        # Verify mapping structure
        assert "source" in data["mapping"]
        assert "target" in data["mapping"]
        assert "expression language" in data["mapping"]["source"]
        assert "labels" in data["mapping"]["source"]

    def test_load_uncompressed_file_from_registry(self, default_registry):
        """Test loading an uncompressed JSON file from the real registry."""
        # Find an entry with no compression
        uncompressed_entry = None
        for entry_name, entry_data in default_registry.items():
            if entry_data.get("compression") is False:
                uncompressed_entry = (entry_name, entry_data)
                break
        
        if uncompressed_entry is None:
            pytest.skip("No uncompressed files found in registry")
        
        entry_name, entry_data = uncompressed_entry
        
        # Load the file
        data = default_registry.get_file(entry_name)
        
        # Verify expected structure
        assert "name" in data
        assert data["name"] == entry_name
        assert "description" in data
        assert "mapping" in data
        
        # Verify the file exists and matches
        file_path = default_registry.data_dir / entry_data["filename"]
        assert file_path.exists()
        assert file_path.suffix == ".json"

    def test_load_multiple_compression_formats(self, default_registry):
        """Test that registry can handle multiple compression formats."""
        found_gzip = False
        found_uncompressed = False
        found_lzma = False
        
        for entry_name in default_registry:
            entry_data = default_registry[entry_name]
            compression = entry_data.get("compression")
            
            if compression == "gzip":
                data = default_registry.get_file(entry_name)
                assert "name" in data
                found_gzip = True
            elif compression is False:
                data = default_registry.get_file(entry_name)
                assert "name" in data
                found_uncompressed = True
            elif compression == "lzma":
                data = default_registry.get_file(entry_name)
                assert "name" in data
                found_lzma = True
        
        # Should have at least gzip and uncompressed files
        assert found_gzip, "No gzip files found in registry"
        assert found_uncompressed, "No uncompressed files found in registry"
        # lzma files might not exist if conversion was done

    def test_specific_entry_contents(self, default_registry):
        """Test that a specific entry has expected content structure."""
        if "generic-brightway-unit-conversions" not in default_registry:
            pytest.skip("generic-brightway-unit-conversions not in registry")
        
        # Load the file
        data = default_registry.get_file("generic-brightway-unit-conversions")
        
        # Verify structure
        assert data["name"] == "generic-brightway-unit-conversions"
        assert "description" in data
        assert isinstance(data["description"], str)
        assert "mapping" in data
        assert "source" in data["mapping"]
        assert "target" in data["mapping"]
        assert "contributors" in data
        assert isinstance(data["contributors"], list)
        assert len(data["contributors"]) > 0

    def test_entry_with_verbs(self, default_registry):
        """Test loading an entry that contains transformation verbs (create, update, etc.)."""
        # Find an entry that might have verb data
        entry_with_data = None
        for entry_name in default_registry:
            try:
                data = default_registry.get_file(entry_name)
                # Check if it has any of the verb keys
                if any(verb in data for verb in ["create", "replace", "update", "delete", "disaggregate"]):
                    entry_with_data = entry_name
                    break
            except Exception:
                continue
        
        if entry_with_data is None:
            pytest.skip("No entries with verb data found in registry")
        
        # Load the entry
        data = default_registry.get_file(entry_with_data)
        
        # Verify it has at least one verb
        verbs = ["create", "replace", "update", "delete", "disaggregate"]
        assert any(verb in data for verb in verbs)
        
        # Verify verb data is a list
        for verb in verbs:
            if verb in data:
                assert isinstance(data[verb], list), f"{verb} should be a list"

    def test_registry_entry_metadata(self, default_registry):
        """Test that registry entry metadata matches loaded file metadata."""
        # Test with a known entry
        entry_name = "simapro-ecoinvent-3.10-cutoff"
        if entry_name not in default_registry:
            pytest.skip(f"{entry_name} not in registry")
        
        # Get registry metadata
        metadata = default_registry[entry_name]
        
        # Load the actual file
        file_data = default_registry.get_file(entry_name)
        
        # Verify key metadata matches
        assert metadata["name"] == file_data["name"]
        assert metadata["source_id"] == file_data["source_id"]
        assert metadata["target_id"] == file_data["target_id"]
        
        # Verify file exists
        file_path = default_registry.data_dir / metadata["filename"]
        assert file_path.exists()
        
        # Verify compression type
        if metadata["compression"] == "gzip":
            assert file_path.suffix == ".gz"
        elif metadata["compression"] is False:
            assert file_path.suffix == ".json"
        elif metadata["compression"] == "lzma":
            assert file_path.suffix == ".xz"
