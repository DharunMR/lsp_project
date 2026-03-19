import re

def get_folding_ranges(file_obj):
    ranges = []
    stack = []
    start_re = re.compile(r'^\s*(SUBROUTINE|FUNCTION|MODULE|DO|IF)\b', re.I)
    end_re = re.compile(r'^\s*END\s*(SUBROUTINE|FUNCTION|MODULE|DO|IF)?\b', re.I)

    for i, line in enumerate(file_obj.text.splitlines()):
        if start_re.search(line):
            stack.append(i)
        elif end_re.search(line) and stack:
            start = stack.pop()
            if i > start:
                ranges.append({"startLine": start, "endLine": i})
    return ranges

def get_code_lens(file_obj):
    """Adds clickable actions above subroutines/programs."""
    lenses = []
    for s in file_obj.symbols:
        if s.kind in ['program', 'subroutine']:
            lenses.append({
                "range": {
                    "start": {"line": s.line, "character": s.col},
                    "end": {"line": s.line, "character": s.col + len(s.name)}
                },
                "command": {
                    "title": "▶ Run Procedure" if s.kind == 'program' else f"{s.kind.capitalize()} Ref",
                    "command": "fortran.run" if s.kind == 'program' else ""
                }
            })
    return lenses