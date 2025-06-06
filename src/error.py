def format_error(error_type: str, message: str, filename: str, source: str, line: int, column: int) -> str:
    """Formats an error message with line, column, and code snippet."""
    lines = source.splitlines()
    if 1 <= line <= len(lines):
        code_line = lines[line - 1].rstrip()
        marker = ' ' * (column - 1) + '^'
    else:
        code_line = '<unknown>'
        marker = ''
    return (
        f"{error_type}: {message}\n"
        f"  File: {filename}\n"
        f"  Line: {line}, Column: {column}\n"
        f"  {code_line}\n"
        f"  {marker}"
    )