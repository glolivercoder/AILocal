
# Package Management with `uv`

These rules define strict guidelines for Python package management using `uv`.

## Installation
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create new project
uv init my-project
cd my-project

# Add dependencies
uv add fastapi uvicorn
uv add --dev pytest black

# Install dependencies
uv sync
```

## Best Practices
- Use `uv` for all package management
- Lock dependencies with `uv lock`
- Use virtual environments
- Specify version constraints
- Use dev dependencies for tools
- Keep requirements files updated

## Project Structure
```
project/
├── pyproject.toml
├── uv.lock
├── src/
│   └── my_project/
└── tests/
```

## Commands
```bash
# Add package
uv add package-name

# Add dev package
uv add --dev package-name

# Remove package
uv remove package-name

# Update packages
uv update

# Run with uv
uv run python script.py
```
