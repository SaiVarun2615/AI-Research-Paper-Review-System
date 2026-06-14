# Contributing to AI Research Review System

Thank you for your interest in contributing to the AI Research Review System! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

### Our Standards

- **Respect differing viewpoints and experiences**
- **Accept constructive criticism gracefully**
- **Focus on what is best for the community**
- **Show empathy towards other community members**

### Unacceptable Behavior

- Harassment, discriminatory language, or inappropriate content
- Personal attacks or insults
- Public or private harassment
- Publishing others' private information without permission
- Other unethical or unprofessional conduct

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic knowledge of Python and web development

### Setting Up Development Environment

1. **Fork the Repository**

   ```bash
   # Fork the repository on GitHub
   # Clone your fork
   git clone https://github.com/yourusername/ai-research-review-system.git
   cd ai-research-review-system
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run Tests**

   ```bash
   pytest tests/
   ```

---

## 🔄 Development Workflow

### Branching Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: New features
- **bugfix/***: Bug fixes
- **hotfix/***: Urgent production fixes

### Creating a Feature Branch

```bash
# Ensure you're on the latest main branch
git checkout main
git pull origin main

# Create a new feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Write clear, descriptive commit messages**

   ```bash
   git commit -m "Add: Semantic Scholar API rate limiting"
   ```

2. **Follow commit message conventions**

   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Docs:` for documentation changes
   - `Refactor:` for code refactoring
   - `Test:` for test additions/changes

3. **Test your changes**

   ```bash
   pytest tests/
   python scripts/app.py  # Manual testing
   ```

---

## 📤 Pull Request Process

### Before Submitting

1. **Update Documentation**
   - Update README.md if needed
   - Add docstrings to new functions
   - Update CHANGELOG.md

2. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

3. **Check Code Style**
   - Follow PEP 8 guidelines
   - Use meaningful variable names
   - Add comments for complex logic

### Submitting a Pull Request

1. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request on GitHub**
   - Provide a clear title
   - Describe your changes
   - Reference related issues
   - Add screenshots if applicable

3. **PR Template**

   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Tests added/updated
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows project style
   - [ ] Self-reviewed the code
   - [ ] Commented complex code
   - [ ] Updated documentation
   - [ ] No new warnings
   - [ ] Added tests
   - [ ] All tests passing
   ```

---

## 📐 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to all functions and classes

### Example

```python
def fetch_papers(query: str, limit: int = 10) -> list:
    """
    Fetch papers from Semantic Scholar API.

    Args:
        query: Search query string
        limit: Maximum number of papers to fetch

    Returns:
        List of paper dictionaries with metadata
    """
    # Implementation
    pass
```

### Code Organization

- Keep functions focused and single-purpose
- Use type hints where appropriate
- Separate concerns into different modules
- Avoid code duplication

### Error Handling

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

---

## 🧪 Testing Guidelines

### Writing Tests

- Write tests for new features
- Aim for high code coverage
- Use descriptive test names
- Test edge cases and error conditions

### Example Test

```python
def test_fetch_papers_success():
    """Test successful paper fetching."""
    query = "machine learning"
    papers = fetch_papers(query, limit=5)
    
    assert len(papers) <= 5
    assert all('title' in paper for paper in papers)
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_paper_fetcher.py

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html
```

---

## 📚 Documentation

### Code Documentation

- Add docstrings to all public functions
- Use Google style docstrings
- Document parameters and return values
- Include usage examples

### README Updates

- Update README.md for significant changes
- Add new features to the features list
- Update installation instructions if needed
- Add screenshots for UI changes

### API Documentation

- Document API integrations
- Include example requests/responses
- Note rate limits and authentication

---

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to...
2. Click on...
3. Scroll down to...
4. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 10]
- Python Version: [e.g., 3.9]
- Package Version: [e.g., 1.0.0]

## Additional Context
Screenshots, logs, or other context
```

---

## 💡 Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Problem Statement
What problem does this solve?

## Proposed Solution
How should this be implemented?

## Alternatives Considered
What other approaches were considered?

## Additional Context
Any other relevant information
```

---

## ❓ Questions

For questions about the project:

1. Check existing documentation
2. Search existing issues
3. Create a new issue with the "question" label

---

## 📧 Contact

For questions or discussions:

- Open an issue on GitHub
- Email: [your-email@example.com]

---

Thank you for contributing to the AI Research Review System! 🎉
