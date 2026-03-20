from typing import Dict, List, Any
import re

TOKEN_TYPES = [
    "variable",   
    "function",   
    "keyword",    
    "string",     
    "number",     
    "comment",    
    "type",       
    "operator",   
]

KIND_TO_ID: Dict[str, int] = {
    'variable': 0,
    'program': 1,      
    'subroutine': 1,  
    'keyword': 2,
    'string': 3,
    'number': 4,
    'comment': 5,
    'type': 6,
    'operator':7,
}

def get_semantic_tokens(file_obj) -> Dict[str, List[int]]:
    data = []
    last_line = 0
    last_col = 0

    sorted_syms = sorted(file_obj.symbols, key=lambda s: (s.line, s.col))

    for sym in sorted_syms:
        token_type = KIND_TO_ID.get(sym.kind, 0)
        token_modifiers = 0 

        delta_line = sym.line - last_line
        if delta_line > 0:
            delta_start = sym.col
        else:
            delta_start = sym.col - last_col

        data.extend([
            delta_line,               
            delta_start,              
            len(sym.name),            
            token_type,               
            token_modifiers
        ])

        last_line = sym.line
        last_col = sym.col

    return {"data": data}

def get_document_highlights(file_obj, line, char):
    if not file_obj or not file_obj.symbols:
        return []

    target_symbol = None
    for sym in file_obj.symbols:
        if sym.line == line and sym.col <= char <= (sym.col + len(sym.name)):
            target_symbol = sym
            break
            
    if not target_symbol: 
        return []

    highlights = []
    for s in file_obj.symbols:
        if s.name == target_symbol.name and s.kind == target_symbol.kind:
            highlights.append({
                "range": {
                    "start": {"line": s.line, "character": s.col},
                    "end": {"line": s.line, "character": s.col + len(s.name)}
                },
                "kind": 1
            })
            
    return highlights