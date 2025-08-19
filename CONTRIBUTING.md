# Contributing to Hospitable Python SDK

Thank you for your interest in contributing to the Hospitable Python SDK! We welcome contributions from the community.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/hospitable-python.git
   cd hospitable-python
   ```
3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- A Hospitable account with API access (for testing)

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

### Environment Variables
For testing, set up your environment:
```bash
export HOSPITABLE_TOKEN="your_test_token_here"
```

## Code Standards

### Code Style
We use the following tools to maintain code quality:

- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

Run all checks:
```bash
# Format code
black hospitable/

# Check linting
flake8 hospitable/

# Type checking
mypy hospitable/
```

### Code Guidelines

1. **Follow PEP 8** style guidelines
2. **Add type hints** to all functions and methods
3. **Write docstrings** for all public functions and classes
4. **Keep functions focused** and small
5. **Use descriptive variable names**
6. **Add error handling** where appropriate

### Example Code Style

```python
from typing import Optional, List, Dict, Any

def get_properties(
    self,
    include: Optional[str] = None,
    page: int = 1,
    per_page: int = 10,
) -> List[Property]:
    """
    Get a list of properties.
    
    Args:
        include: Relationships to include
        page: Page number
        per_page: Results per page
        
    Returns:
        List of property objects
        
    Raises:
        AuthenticationError: If authentication fails
        ValidationError: If parameters are invalid
    """
    # Implementation here
```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hospitable

# Run specific test file
pytest tests/test_client.py
```

### Writing Tests
- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names
- Mock external API calls in unit tests

### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── conftest.py     # Test configuration
└── fixtures/       # Test data
```

## Making Changes

### Workflow
1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code standards

3. **Add tests** for your changes

4. **Update documentation** if needed

5. **Run the test suite**:
   ```bash
   pytest
   black hospitable/
   flake8 hospitable/
   mypy hospitable/
   ```

6. **Commit your changes**:
   ```bash
   git commit -m "Add: your feature description"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub

### Commit Message Format
Use conventional commit format:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

Examples:
```
feat: add calendar batch update method
fix: handle rate limit retry headers correctly
docs: update authentication guide with OAuth examples
test: add integration tests for reservations endpoint
```

## Documentation

### Types of Documentation
1. **Code documentation** (docstrings)
2. **API reference** (docs/api-reference.md)
3. **User guides** (docs/*.md)
4. **README** updates

### Documentation Guidelines
- Use clear, concise language
- Include code examples
- Update relevant documentation when changing APIs
- Test all code examples

## Pull Request Process

### Before Submitting
- [ ] Tests pass locally
- [ ] Code is formatted (black)
- [ ] Linting passes (flake8)
- [ ] Type checking passes (mypy)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (for significant changes)

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
```

## Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Breaking changes increment MAJOR
- New features increment MINOR  
- Bug fixes increment PATCH

### Release Checklist
1. Update version in `setup.py` and `__init__.py`
2. Update CHANGELOG.md
3. Create release PR
4. Tag release after merge
5. Publish to PyPI

## Getting Help

### Resources
- [Hospitable API Documentation](https://developer.hospitable.com/docs/public-api-docs/)
- [Python Packaging Guide](https://packaging.python.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

### Communication
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Email**: team-platform@hospitable.com for API-specific questions

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inspiring community for all.

### Standards
- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Enforcement
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project maintainers.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributor statistics

Thank you for contributing to the Hospitable Python SDK!