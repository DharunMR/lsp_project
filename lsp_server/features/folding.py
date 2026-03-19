from regex import FortranRegularExpressions as FRE

def get_folding_ranges(file_obj):
    ranges = []
    stack = [] 
    lines = file_obj.text.splitlines()

    for i, line in enumerate(lines):
        line_content = line.split('!')[0]
        line_upper = line_content.upper().strip()
        
        if not line_upper:
            continue

        if FRE.END_WORD.search(line_content):
            if stack:
                start_line = stack.pop()
                if i > start_line:
                    ranges.append({
                        "startLine": start_line,
                        "endLine": i - 1,
                        "kind": "region"
                    })
            continue

        is_start = False
        
        if FRE.SUB.search(line_content) or FRE.FUN.search(line_content):
            is_start = True
        elif FRE.PROG.search(line_content):
            is_start = True
        elif FRE.IF.search(line_content) and ("THEN" in line_upper):
            is_start = True
        elif FRE.DO.search(line_content):
            is_start = True
        elif FRE.SELECT.search(line_content):
            is_start = True
        elif FRE.MOD.search(line_content):
            is_start = True

        if is_start:
            stack.append(i)

    return ranges

def get_code_lens(file_obj):
    lenses = []
    for s in file_obj.symbols:
        if s.kind in ['program', 'subroutine']:
            lenses.append({
                "range": {
                    "start": {"line": s.line, "character": s.col},
                    "end": {"line": s.line, "character": s.col + len(s.name)}
                },
                "command": {
                    "title": "▶ Run Program" if s.kind == 'program' else f"Go to {s.name}",
                    "command": "fortran.run" if s.kind == 'program' else "editor.action.showReferences",
                    "arguments": [file_obj.uri, {"line": s.line, "character": s.col}] if s.kind != 'program' else []
                }
            })
    return lenses