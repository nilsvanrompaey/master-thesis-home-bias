#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
from collections import defaultdict


def count_lines(file_path):
    """Count lines in a file, returning total, code, blank, and comment lines."""
    total_lines = 0
    code_lines = 0
    blank_lines = 0
    comment_lines = 0
    
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        in_multiline_comment = False
        for line in f:
            total_lines += 1
            stripped_line = line.strip()
            
            # Skip blank lines
            if not stripped_line:
                blank_lines += 1
                continue
                
            # Handle multiline comments
            if in_multiline_comment:
                comment_lines += 1
                if '"""' in stripped_line or "'''" in stripped_line:
                    in_multiline_comment = False
                continue
                
            # Check for multiline comment start
            if stripped_line.startswith('"""') or stripped_line.startswith("'''"):
                comment_lines += 1
                if not (stripped_line.endswith('"""') and len(stripped_line) > 3) and not (stripped_line.endswith("'''") and len(stripped_line) > 3):
                    in_multiline_comment = True
                continue
                
            # Check for single line comments
            if stripped_line.startswith('#'):
                comment_lines += 1
                continue
                
            code_lines += 1
            
    return {
        'total': total_lines,
        'code': code_lines, 
        'blank': blank_lines,
        'comments': comment_lines
    }


def find_python_files(directory):
    """Find all Python files in directory recursively."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files


def format_counts(counts, show_files=False):
    """Format the count results for display."""
    result = []
    
    if show_files:
        # Show individual file counts
        result.append("\nFile Details:")
        result.append(f"{'File Path':<60} {'Total':<8} {'Code':<8} {'Blank':<8} {'Comments':<8}")
        result.append("-" * 100)
        
        for file_path, count in sorted(counts['files'].items()):
            result.append(f"{file_path:<60} {count['total']:<8} {count['code']:<8} {count['blank']:<8} {count['comments']:<8}")
    
    # Show summary
    result.append("\nSummary:")
    result.append(f"Total Python files: {counts['file_count']}")
    result.append(f"Total lines: {counts['total']['total']}")
    result.append(f"Code lines: {counts['total']['code']}")
    result.append(f"Blank lines: {counts['total']['blank']}")
    result.append(f"Comment lines: {counts['total']['comments']}")
    
    return "\n".join(result)


def count_python_lines(directory, show_files=False):
    """Count lines in all Python files in a directory."""
    directory = os.path.abspath(directory)
    
    if not os.path.exists(directory):
        return f"Error: Directory '{directory}' does not exist"
    
    if not os.path.isdir(directory):
        return f"Error: '{directory}' is not a directory"
    
    python_files = find_python_files(directory)
    
    if not python_files:
        return f"No Python files found in '{directory}'"
    
    counts = {
        'file_count': len(python_files),
        'files': {},
        'total': {'total': 0, 'code': 0, 'blank': 0, 'comments': 0}
    }
    
    for file_path in python_files:
        try:
            file_counts = count_lines(file_path)
            rel_path = os.path.relpath(file_path, directory)
            counts['files'][rel_path] = file_counts
            
            # Update totals
            for key in file_counts:
                counts['total'][key] += file_counts[key]
        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
    
    return format_counts(counts, show_files)


def main():
    parser = argparse.ArgumentParser(description='Count lines in Python files.')
    parser.add_argument('directory', help='Directory to scan for Python files')
    parser.add_argument('--details', '-d', action='store_true', help='Show details for each file')
    
    args = parser.parse_args()
    result = count_python_lines(args.directory, args.details)
    print(result)


if __name__ == "__main__":
    main()