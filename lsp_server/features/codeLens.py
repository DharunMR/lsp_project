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