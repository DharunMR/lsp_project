from lsp_server.regex import FortranRegularExpressions as FRE

def get_folding_ranges(file_obj):
    ranges = []
    stack = [] 
    lines = file_obj.text.splitlines()

    for i, line in enumerate(lines):
        # 1. Clean the line: Ignore comments and whitespace
        # This prevents "! END IF" from being treated as a real END
        line_content = line.split('!')[0]
        line_upper = line_content.upper().strip()
        
        if not line_upper:
            continue

        # --- 2. Detect End of Blocks FIRST ---
        # We check END first so that "END SUBROUTINE" isn't caught by the "SUB" start regex.
        if FRE.END_WORD.search(line_content):
            if stack:
                start_line = stack.pop()
                if i > start_line:
                    ranges.append({
                        "startLine": start_line,
                        "endLine": i - 1, # Keeps the END line visible
                        "kind": "region"
                    })
            continue # Move to next line once an END is processed

        # --- 3. Detect Start of Blocks ---
        is_start = False
        
        # Check SUBROUTINE / FUNCTION
        if FRE.SUB.search(line_content) or FRE.FUN.search(line_content):
            is_start = True
        # Check PROGRAM
        elif FRE.PROG.search(line_content):
            is_start = True
        # Check IF (...) THEN
        elif FRE.IF.search(line_content) and ("THEN" in line_upper):
            is_start = True
        # Check DO
        elif FRE.DO.search(line_content):
            is_start = True
        # Check SELECT CASE
        elif FRE.SELECT.search(line_content):
            is_start = True
        # Check MODULE (but not 'END MODULE', handled by the END check above)
        elif FRE.MOD.search(line_content):
            is_start = True

        if is_start:
            stack.append(i)

    return ranges

def get_code_lens(file_obj):
    """Adds clickable actions above subroutines/programs."""
    lenses = []
    # Ensure file_obj.symbols was populated in manager.py
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