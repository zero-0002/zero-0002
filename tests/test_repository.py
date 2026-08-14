"""
Test suite for zero-0002 repository validation and quality assurance.
"""

import os
import re
from pathlib import Path


class TestRepositoryStructure:
    """Verify repository structure and required files."""
    
    def test_readme_exists(self):
        """Test that README.md exists."""
        assert Path("readme.md").exists(), "README.md file is missing"
    
    def test_readme_contains_content(self):
        """Test that README has meaningful content."""
        with open("readme.md", "r") as f:
            content = f.read()
        assert len(content) > 0, "README.md is empty"
        assert "zero-0002" in content.lower(), "README should contain project name"
    
    def test_contributing_guide_exists(self):
        """Test that CONTRIBUTING.md exists."""
        assert Path("CONTRIBUTING.md").exists(), "CONTRIBUTING.md is missing"
    
    def test_architecture_doc_exists(self):
        """Test that ARCHITECTURE.md exists."""
        assert Path("ARCHITECTURE.md").exists(), "ARCHITECTURE.md is missing"
    
    def test_required_directories_exist(self):
        """Test that required directories exist."""
        required_dirs = [".github", "assets"]
        for dir_name in required_dirs:
            assert Path(dir_name).exists(), f"Required directory '{dir_name}' is missing"
    
    def test_workflows_directory_has_files(self):
        """Test that workflows directory contains CI configuration."""
        workflows_dir = Path(".github/workflows")
        if workflows_dir.exists():
            yml_files = list(workflows_dir.glob("*.yml"))
            assert len(yml_files) > 0, "No workflow files found in .github/workflows"


class TestCodeQuality:
    """Test code quality standards."""
    
    def test_no_large_files(self):
        """Test that no single file exceeds reasonable size."""
        max_size = 10 * 1024 * 1024  # 10MB
        for file_path in Path(".").rglob("*"):
            if file_path.is_file() and not str(file_path).startswith(".git"):
                assert file_path.stat().st_size < max_size, \
                    f"File {file_path} exceeds maximum size"
    
    def test_no_sensitive_data_in_readme(self):
        """Test that README doesn't contain sensitive information."""
        with open("readme.md", "r") as f:
            content = f.read()
        
        # Check for common sensitive patterns
        sensitive_patterns = [
            r"password.*=",
            r"api[_-]key",
            r"secret.*=",
        ]
        
        for pattern in sensitive_patterns:
            assert not re.search(pattern, content, re.IGNORECASE), \
                f"Potential sensitive data found matching pattern: {pattern}"
    
    def test_markdown_files_valid(self):
        """Test that markdown files are properly formatted."""
        md_files = list(Path(".").rglob("*.md"))
        assert len(md_files) > 0, "No markdown files found"
        
        for md_file in md_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            assert len(content) > 0, f"{md_file} is empty"


class TestDocumentation:
    """Test documentation completeness."""
    
    def test_contributing_doc_has_sections(self):
        """Test that CONTRIBUTING.md has required sections."""
        with open("CONTRIBUTING.md", "r") as f:
            content = f.read()
        
        required_sections = [
            "Getting Started",
            "Pull Request",
        ]
        
        for section in required_sections:
            assert section.lower() in content.lower(), \
                f"CONTRIBUTING.md missing section: {section}"
    
    def test_architecture_doc_has_sections(self):
        """Test that ARCHITECTURE.md has required sections."""
        with open("ARCHITECTURE.md", "r") as f:
            content = f.read()
        
        required_sections = [
            "Structure",
            "Development",
        ]
        
        for section in required_sections:
            assert section.lower() in content.lower(), \
                f"ARCHITECTURE.md missing section: {section}"


class TestCommitHistory:
    """Test commit history quality."""
    
    def test_repository_has_commits(self):
        """Test that repository has meaningful commit history."""
        # This can be expanded with actual git log parsing
        assert Path(".git").exists(), "Repository should be a git repository"


if __name__ == "__main__":
    # Run basic tests
    test = TestRepositoryStructure()
    test.test_readme_exists()
    test.test_contributing_guide_exists()
    test.test_architecture_doc_exists()
    print("✓ All basic tests passed!")
