import re

def _get_word_at(file_obj, line, char):
    lines = file_obj.text.splitlines()
    if line >= len(lines): return None
    match = re.search(r'\b\w+\b', lines[line][max(0, char-20):char+20])
    return match.group(0) if match else None

def get_hover(file_obj, line, char):
    word = _get_word_at(file_obj, line, char)
    if not word: return None
    
    for s in file_obj.symbols:
        if s.name.upper() == word.upper():
            md = f"```fortran\n{s.kind.upper()} :: {s.name}{s.signature if s.signature != '()' else ''}\n```\nDefined at line {s.line+1}"
            return {"contents": {"kind": "markdown", "value": md}}
    return None

def get_definition(file_obj, line, char):
    word = _get_word_at(file_obj, line, char)
    if not word: return None
    for s in file_obj.symbols:
        if s.name.upper() == word.upper():
            return {
                "uri": file_obj.uri,
                "range": {"start": {"line": s.line, "character": s.col}, "end": {"line": s.line, "character": s.col + len(s.name)}}
            }
    return None

def get_signature_help(file_obj, line, char):
    lines = file_obj.text.splitlines()
    if line >= len(lines): return None
    
    text_before_cursor = lines[line][:char]
    match = re.search(r'\b(\w+)\s*\(.*$', text_before_cursor)
    
    if match:
        func_name = match.group(1)
        for s in file_obj.symbols:
            if s.name.upper() == func_name.upper() and s.kind in ['subroutine', 'function']:
                return {
                    "signatures": [{
                        "label": f"{s.name}{s.signature}",
                        "documentation": f"{s.kind.capitalize()} signature",
                        "parameters": [{"label": param.strip()} for param in s.signature.strip("()").split(",") if param]
                    }],
                    "activeSignature": 0,
                    "activeParameter": text_before_cursor.count(',')
                }
    return None