#!/bin/bash
# Setup safety features for a new project
# Usage: ./setup-project-safety.sh [project-directory]

PROJECT_DIR="${1:-.}"
SAFETY_LOG="/logs/safety/checks.log"

log_safety() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [SETUP] $@" | tee -a "$SAFETY_LOG"
}

echo "Setting up safety features for project: $PROJECT_DIR"
log_safety "Setting up safety features for project: $PROJECT_DIR"

cd "$PROJECT_DIR" || exit 1

# Initialize git if not already a repo
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    log_safety "Initialized git repository"
fi

# Copy gitignore template if .gitignore doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore from template..."
    cp /home/developer/.config/gitignore.template .gitignore
    log_safety "Created .gitignore from template"
else
    echo ".gitignore already exists, skipping..."
fi

# Set up pre-commit hooks
if [ ! -f ".pre-commit-config.yaml" ]; then
    echo "Setting up pre-commit hooks..."
    cp /home/developer/.config/.pre-commit-config.yaml .pre-commit-config.yaml

    # Install pre-commit hooks
    if command -v pre-commit &> /dev/null; then
        pre-commit install
        log_safety "Installed pre-commit hooks"
    fi
else
    echo ".pre-commit-config.yaml already exists, skipping..."
fi

# Initialize detect-secrets baseline
if command -v detect-secrets &> /dev/null; then
    if [ ! -f ".secrets.baseline" ]; then
        echo "Creating secrets detection baseline..."
        detect-secrets scan > .secrets.baseline 2>/dev/null || true
        log_safety "Created .secrets.baseline"
    fi
fi

# Create Python project structure if Python files exist
if ls *.py &> /dev/null || [ -d "src" ]; then
    echo "Python project detected..."

    # Create pyproject.toml if it doesn't exist
    if [ ! -f "pyproject.toml" ]; then
        echo "Creating pyproject.toml..."
        cat > pyproject.toml << 'EOF'
[project]
name = "my-project"
version = "0.1.0"
description = "Add your description here"
requires-python = ">=3.11"
dependencies = []

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "S",   # flake8-bandit (security)
    "N",   # pep8-naming
]
ignore = []

[tool.bandit]
exclude_dirs = ["tests", "test"]
skips = []

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
EOF
        log_safety "Created pyproject.toml with safety configurations"
    fi
fi

# Set git configuration for safety
git config core.hooksPath /home/developer/.config/git/hooks
log_safety "Configured git hooks path"

# Run initial safety scan
echo ""
echo "Running initial safety scan..."
if command -v gitleaks &> /dev/null; then
    echo "Scanning for secrets..."
    gitleaks detect --no-git --verbose --redact >> "$SAFETY_LOG" 2>&1 || echo "⚠️  Check logs for potential issues"
fi

echo ""
echo "✅ Safety features configured!"
echo ""
echo "Configured:"
echo "  - Git repository initialized"
echo "  - .gitignore with sensitive patterns"
echo "  - Pre-commit hooks for safety checks"
echo "  - Secrets detection baseline"
echo "  - Python project configuration (if applicable)"
echo ""
echo "To commit changes, git will automatically:"
echo "  - Scan for secrets"
echo "  - Check for large files"
echo "  - Warn about sensitive files"
echo "  - Run code quality checks (Python)"
echo ""

log_safety "Project safety setup complete"
