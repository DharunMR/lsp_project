import re

class Symbol:
    def __init__(self, name, kind, line, col, signature="()"):
        self.name = name
        self.kind = kind  # 'variable', 'subroutine', 'function', 'program'
        self.line = line
        self.col = col
        self.signature = signature # Useful for signature help

class FortranDocument:
    def __init__(self, uri, text):
        self.uri = uri
        self.text = text
        self.symbols = []
        self.diagnostics = []
        self.refresh()

    def refresh(self):
        self.symbols = []
        self.diagnostics = []
        lines = self.text.splitlines()
        
        # Regex definitions
        proc_re = re.compile(r'^\s*(SUBROUTINE|FUNCTION|PROGRAM)\s+([a-zA-Z]\w*)\s*(\(.*\))?', re.I)
        var_re = re.compile(r'\b(INTEGER|REAL|COMPLEX|LOGICAL|CHARACTER|TYPE)\b.*::\s*([a-zA-Z]\w*)', re.I)
        
        has_implicit_none = False

        for i, line in enumerate(lines):
            clean = line.split('!')[0] # Strip comments
            
            if "implicit none" in clean.lower():
                has_implicit_none = True

            # Extract Procedures
            if m := proc_re.search(clean):
                sig = m.group(3) if m.group(3) else "()"
                self.symbols.append(Symbol(m.group(2), m.group(1).lower(), i, clean.find(m.group(2)), sig))
            
            # Extract Variables
            elif m := var_re.search(clean):
                name = m.group(2)
                self.symbols.append(Symbol(name, 'variable', i, clean.find(name)))

        # Diagnostics: Enforce Implicit None
        if not has_implicit_none and len(lines) > 0:
            self.diagnostics.append({
                "range": {"start": {"line": 0, "character": 0}, "end": {"line": 0, "character": 10}},
                "message": "Best Practice: Missing 'implicit none' statement.",
                "severity": 2 # 1=Error, 2=Warning, 3=Information
            })

class WorkspaceManager:
    def __init__(self):
        self.docs = {}

    def update(self, uri, text):
        self.docs[uri] = FortranDocument(uri, text)
        return self.docs[uri].diagnostics

    def get(self, uri):
        return self.docs.get(uri)