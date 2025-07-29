#!/usr/bin/env python3
"""
Utility scripts for AI Master 2025 Chatbot project
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run shell command and return result"""
    print(f"Running: {command}")
    return subprocess.run(command, shell=True, check=check)


def setup_dev_environment():
    """Setup complete development environment"""
    print("🚀 Setting up development environment...")

    commands = [
        "uv sync --all-extras",
        "uv run pre-commit install --allow-missing-config || echo 'Pre-commit not configured yet'",
    ]

    for cmd in commands:
        try:
            run_command(cmd)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Command failed: {cmd}")
            print(f"Error: {e}")

    print("✅ Development environment setup complete!")


def check_code_quality():
    """Run all code quality checks"""
    print("🔍 Running code quality checks...")

    checks = [
        ("Black formatting", "uv run black --check ."),
        ("Ruff linting", "uv run ruff check ."),
        ("MyPy type checking", "uv run mypy ."),
    ]

    failed_checks = []

    for name, cmd in checks:
        print(f"\n📋 {name}...")
        try:
            run_command(cmd)
            print(f"✅ {name} passed")
        except subprocess.CalledProcessError:
            print(f"❌ {name} failed")
            failed_checks.append(name)

    if failed_checks:
        print(f"\n❌ Failed checks: {', '.join(failed_checks)}")
        return False
    else:
        print("\n✅ All code quality checks passed!")
        return True


def format_code():
    """Format code with black and fix linting issues"""
    print("🎨 Formatting code...")

    commands = [
        "uv run black .",
        "uv run ruff check --fix .",
    ]

    for cmd in commands:
        run_command(cmd, check=False)

    print("✅ Code formatting complete!")


def clean_project():
    """Clean project cache and temporary files"""
    print("🧹 Cleaning project...")

    # Python cache
    run_command(
        "find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true", check=False
    )
    run_command("find . -type f -name '*.pyc' -delete 2>/dev/null || true", check=False)

    # Test and coverage files
    paths_to_remove = [".pytest_cache", "htmlcov", ".coverage", ".mypy_cache", ".ruff_cache"]

    for path in paths_to_remove:
        if Path(path).exists():
            run_command(f"rm -rf {path}")

    # UV cache
    run_command("uv cache clean", check=False)

    print("✅ Project cleaned!")


def build_project():
    """Build the project package"""
    print("📦 Building project...")
    run_command("uv build")
    print("✅ Project built successfully!")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="AI Master 2025 Chatbot utility scripts")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    subparsers.add_parser("setup", help="Setup development environment")

    # Code quality commands
    subparsers.add_parser("check", help="Run all code quality checks")
    subparsers.add_parser("format", help="Format code and fix linting issues")

    # Maintenance commands
    subparsers.add_parser("clean", help="Clean cache and temporary files")
    subparsers.add_parser("build", help="Build the project package")

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute commands
    if args.command == "setup":
        setup_dev_environment()
    elif args.command == "check":
        success = check_code_quality()
        sys.exit(0 if success else 1)
    elif args.command == "format":
        format_code()
    elif args.command == "clean":
        clean_project()
    elif args.command == "build":
        build_project()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
