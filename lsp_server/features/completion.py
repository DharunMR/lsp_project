import json, os, re

def get_completions(file_obj, line_no, char_no):
    items = []
    
    try:
        line_prefix = file_obj.lines[line_no][:char_no]
        match = re.search(r'(\w+)$', line_prefix)
        prefix = match.group(1).lower() if match else ""
    except (IndexError, AttributeError):
        prefix = ""

    seen_labels = set()

    for s in file_obj.symbols:
        label = s.name
        if label.lower().startswith(prefix) and label not in seen_labels:
            kind = 6 if s.kind == 'variable' else 3
            items.append({
                "label": label, 
                "kind": kind, 
                "detail": s.kind,
                "insertText": f"{label}{s.signature}" if s.kind in ['function', 'subroutine'] else label
            })
            seen_labels.add(label)
    
    path = os.path.join(os.path.dirname(__file__), 'words.json')
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                static_data = json.load(f).get("words", [])
                for word in static_data:
                    label = word.get("label", "")
                    if label.lower().startswith(prefix) and label not in seen_labels:
                        items.append(word)
                        seen_labels.add(label)
        except Exception:
            pass

    return {"isIncomplete": False, "items": items}