---
sidebar_position: 2
title: Contribute
description: Learn how to contribute.
---

# Contributing

## Getting Started

Welcome to the Neko project! We're excited to have you contribute. This guide will walk you through everything you need to know to make meaningful contributions to our project.

### First Time Contributing?

If you're new to open source contribution, don't worry! Here's what you need to know:

1. **Fork the Repository**: Create your own copy of the project
2. **Clone Your Fork**: Download the code to your local machine
3. **Create a Branch**: Make your changes in a separate branch
4. **Make Changes**: Implement your feature or fix
5. **Commit Your Changes**: Save your work with proper commit messages
6. **Push to Your Fork**: Upload your changes
7. **Create a Pull Request**: Submit your contribution for review

For a detailed walkthrough, check out [GitHub's official guide](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project).

## Commit Conventions

We follow conventional commit standards to maintain a clean and readable git history. This helps with automated changelog generation and version management.

### Using Comet for Commits

We highly recommend using [Comet](https://github.com/Fastiraz/comet) to generate conventional commits with a user-friendly terminal interface:

```bash
# Install comet
go install github.com/Fastiraz/comet@latest

# Use comet to create commits
comet
```

Comet will guide you through creating properly formatted commit messages that follow the conventional commit specification.

## Coding Conventions

### Backend (Python)

We follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for all Python code in the backend.

#### Key Guidelines:

**Naming Conventions:**
- Use `snake_case` for variables, functions, and module names
- Use `PascalCase` for class names
- Use `UPPER_CASE` for constants

```python
# Good
user_name = "john_doe"
MAX_RETRIES = 3

class UserManager:
  def get_user_data(self):
    pass

# Bad
userName = "john_doe"
maxRetries = 3

class userManager:
  def getUserData(self):
    pass
```

**Code Formatting:**
- Line length: 80 characters maximum
- Use 2 spaces for indentation
- Add docstrings to all public functions and classes
- Use type hints where appropriate

```python
def calculate_user_score(user_id: int, bonus_points: int = 0) -> float:
  """Calculate the total score for a user.

  Args:
    user_id: The unique identifier for the user.
    bonus_points: Additional points to add to the score.

  Returns:
    The calculated user score as a float.
  """
  # Implementation here
  pass
```

### Frontend (React)

**Note:** Frontend coding conventions are currently being evaluated and will be established in the future. For now, focus on writing clean, readable code and following common React best practices.

## Questions?

If you have any questions about contributing, feel free to:
- Open an issue for discussion
- Reach out to the maintainers

Thank you for contributing to Neko! 🐱
