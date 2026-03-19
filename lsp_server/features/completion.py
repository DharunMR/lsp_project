import json, os

def get_completions(file_obj):
    items = []
    # Dynamic Symbols
    for s in file_obj.symbols:
        kind = 6 if s.kind == 'variable' else 3
        items.append({
            "label": s.name, 
            "kind": kind, 
            "detail": s.kind,
            "insertText": f"{s.name}{s.signature}" if s.kind in ['function', 'subroutine'] else s.name
        })
    
    # Static Snippets
    path = os.path.join(os.path.dirname(__file__), 'words.json')
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                items.extend(json.load(f).get("words", []))
        except: pass
    return {"isIncomplete": False, "items": items}