import re

def get_semantic_tokens(file_obj):
    data = []
    last_line = 0
    last_col = 0

    # 1. Sort symbols by line, then by column (This is exactly where it belongs)
    # This ensures the deltas are never negative, which would crash the coloring.
    sorted_syms = sorted(file_obj.symbols, key=lambda x: (x.line, x.col))

    for sym in sorted_syms:
        delta_line = sym.line - last_line
        
        if delta_line > 0:
            # New line: delta_start is the absolute column
            delta_start = sym.col
        else:
            # Same line: delta_start is relative to the PREVIOUS token's START
            delta_start = sym.col - last_col
        
        # Mapping to your legend: 0: variable (Blue), 1: function (Yellow), 2: keyword (Purple)
        if sym.kind in ['subroutine', 'function', 'program']:
            token_type = 1
        elif sym.kind in ['keyword']:
            token_type = 2
        else:
            token_type = 0 
        
        # We use len(sym.name) for the width of the highlight
        data.extend([
            delta_line, 
            delta_start, 
            len(sym.name), 
            token_type, 
            0 
        ])
        
        # Update trackers
        last_line = sym.line
        last_col = sym.col

    return {"data": data}

def get_document_highlights(file_obj, line, char):
    """Highlights all occurrences of the variable under cursor accurately."""
    lines = file_obj.text.splitlines()
    if line >= len(lines): 
        return []
    
    current_line = lines[line]
    
    # IMPROVED: Find the specific word EXACTLY under the cursor
    # Instead of slicing -20/+20, we find all words and see which one contains 'char'
    target_word = None
    for m in re.finditer(r'\b\w+\b', current_line):
        if m.start() <= char <= m.end():
            target_word = m.group(0)
            break
            
    if not target_word: 
        return []

    highlights = []
    for i, l in enumerate(lines):
        # Find every instance of that specific word in the whole file
        for m in re.finditer(rf'\b{target_word}\b', l):
            highlights.append({
                "range": {
                    "start": {"line": i, "character": m.start()},
                    "end": {"line": i, "character": m.end()}
                },
                "kind": 1 # 1 = Read access highlight
            })
    return highlights