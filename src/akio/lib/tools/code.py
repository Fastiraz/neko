#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
from typing import Dict


def read_file(file_path: str = None) -> str:
  """
  Utility function to read a file and return its content.

  Args:
    file_path (str): Path to the file to read.

  Returns:
    str: File content if successful, None if failed.
  """
  if file_path is None:
    return "No file path was provided."
  try:
    with open(file_path, 'r', encoding='utf-8') as f:
      return f.read()
  except Exception as e:
    return f"Error reading file {file_path}: {e}"


def write_file(
  file_path: str,
  content: str,
  mode: str = 'w'
) -> bool:
  """
  This function allow the AI agent to write into a file.

  Args:
    file_path (str): The file path to write into.
    content (str): The content to write to the file.
    mode (str): File mode ('w' for write, 'a' for append). Default is 'w'.

  Returns:
    bool: True if successful, False otherwise.
  """
  try:
    with open(file_path, mode, encoding='utf-8') as f:
      f.write(content)
    return True
  except Exception as e:
    print(f"Error writing to file {file_path}: {e}")
    return False


def get_project_context(
  project_path: str,
  max_file_size: int = 100000
) -> Dict:
  """
  This function allows the AI agent to retrieve the project content recursively for his context.

  Args:
    project_path (str): The root path of the project to analyze.
    max_file_size (int): Maximum file size in bytes to include (default: 100KB).

  Returns:
    dict: Dictionary containing project structure and file contents.
  """
  project_context = {
    'structure': [],
    'files': {},
    'total_files': 0,
    'skipped_files': []
  }

  # Define file extensions to include
  code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx',
                     '.java', '.cpp', '.c', '.h', '.cs',
                     '.go', '.rs', '.php', '.rb', '.swift',
                     '.kt', '.scala', '.sh', '.bat',
                     '.html', '.css', '.scss', '.sass',
                     '.less', '.vue', '.svelte', '.json',
                     '.xml', '.yaml', '.yml', '.toml',
                     '.ini', '.cfg', '.conf', '.md', '.txt'}

  try:
    for root, dirs, files in os.walk(project_path):
      # Skip common build/dependency directories
      dirs[:] = [d for d in dirs if d not in {
        '.git', 'node_modules', '__pycache__','.pytest_cache',
        'venv', 'env', 'build', 'dist'}]

      for file in files:
        file_path = os.path.join(root, file)
        relative_path = os.path.relpath(file_path, project_path)

        # Get file extension
        _, ext = os.path.splitext(file)

        # Add to structure
        project_context['structure'].append(relative_path)
        project_context['total_files'] += 1

        # Read file content if it's a code file and not too large
        if ext.lower() in code_extensions:
          try:
            file_size = os.path.getsize(file_path)
            if file_size <= max_file_size:
              with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                project_context['files'][relative_path] = {
                  'content': content,
                  'size': file_size,
                  'lines': len(content.splitlines())
                }
            else:
              project_context['skipped_files'].append(f"{relative_path} (too large: {file_size} bytes)")
          except Exception as e:
            project_context['skipped_files'].append(f"{relative_path} (read error: {e})")

    return project_context

  except Exception as e:
    print(f"Error reading project context: {e}")
    return None
