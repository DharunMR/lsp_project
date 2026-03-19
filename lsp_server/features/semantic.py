import re

def get_semantic_tokens(file_obj):
    data = []
    last_line = 0
    last_col = 0

    # 1. Sort symbols by line, then by column (Essential!)
    sorted_syms = sorted(file_obj.symbols, key=lambda x: (x.line, x.col))

    for sym in sorted_syms:
        # Calculate deltas
        delta_line = sym.line - last_line
        
        if delta_line > 0:
            # New line: delta_start is the absolute column
            delta_start = sym.col
        else:
            # Same line: delta_start is relative to the PREVIOUS token's start
            delta_start = sym.col - last_col
        
        # Determine type based on your main.py legend:
        # 0: variable, 1: function, 2: keyword
        if sym.kind in ['subroutine', 'function', 'program']:
            token_type = 1
        elif sym.kind in ['keyword']:
            token_type = 2
        else:
            token_type = 0 # variable/default
        
        # [deltaLine, deltaStart, length, tokenType, tokenModifiers]
        data.extend([
            delta_line, 
            delta_start, 
            len(sym.name), 
            token_type, 
            0 # modifiers
        ])
        
        # CRITICAL: Update trackers for the next token
        last_line = sym.line
        last_col = sym.col

    return {"data": data}

def get_document_highlights(file_obj, line, char):
    """Highlights all occurrences of the variable under cursor."""
    lines = file_obj.text.splitlines()
    if line >= len(lines): return []
    
    match = re.search(r'\b\w+\b', lines[line][max(0, char-20):char+20])
    if not match: return []
    target_word = match.group(0)

    highlights = []
    for i, l in enumerate(lines):
        for m in re.finditer(rf'\b{target_word}\b', l):
            highlights.append({
                "range": {
                    "start": {"line": i, "character": m.start()},
                    "end": {"line": i, "character": m.end()}
                },
                "kind": 1 # Text highlight
            })
    return highlights