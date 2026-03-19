import re

class Symbol:
    def __init__(self, name, kind, line, col):
        self.name = name
        self.kind = kind  # 'program', 'subroutine', 'variable', 'keyword'
        self.line = line
        self.col = col

class FortranFile:
    def __init__(self, uri, text):
        self.uri = uri
        self.text = text
        self.symbols = []
        self.parse()

    def parse(self):
        """Simple symbolic parser to populate the symbols list."""
        self.symbols = []
        lines = self.text.splitlines()

        # 1. Define Regex Patterns
        patterns = {
            'program': r'^\s*PROGRAM\s+(\w+)',
            'subroutine': r'^\s*SUBROUTINE\s+(\w+)',
            'variable': r'^\s*(?:INTEGER|REAL|COMPLEX|LOGICAL|CHARACTER).*?::\s*(\w+)',
            'keyword': r'\b(IF|THEN|ELSE|END|PROGRAM|SUBROUTINE|INTEGER|REAL|DO|WHILE|RETURN)\b'
        }

        for i, line in enumerate(lines):
            # Check for structural blocks (Program/Subroutine)
            for kind in ['program', 'subroutine']:
                match = re.search(patterns[kind], line, re.IGNORECASE)
                if match:
                    self.symbols.append(Symbol(match.group(1), kind, i, match.start(1)))

            # Check for Variable Declarations (INTEGER :: jk)
            var_match = re.search(patterns['variable'], line, re.IGNORECASE)
            if var_match:
                self.symbols.append(Symbol(var_match.group(1), 'variable', i, var_match.start(1)))

            # Check for Keywords (to fix the "white text" problem)
            # We find all keywords and add them as symbols so semantic.py can color them
            for kw_match in re.finditer(patterns['keyword'], line, re.IGNORECASE):
                # We only add it if it's not already part of a structural match
                self.symbols.append(Symbol(kw_match.group(0), 'keyword', i, kw_match.start()))

            # Catch usage of variables (very basic logic)
            # This finds 'jk' or 'fghj' when used in assignments or IF statements
            words = re.finditer(r'\b[a-zA-Z_]\w*\b', line)
            for w in words:
                name = w.group(0)
                # If it's not a keyword and not already found, treat it as a variable usage
                if not re.match(patterns['keyword'], name, re.IGNORECASE):
                    # Only add if not already in symbols for this line
                    if not any(s.line == i and s.col == w.start() for s in self.symbols):
                        self.symbols.append(Symbol(name, 'variable', i, w.start()))

class WorkspaceManager:
    def __init__(self):
        self.documents = {}

    def update(self, uri, text):
        self.documents[uri] = FortranFile(uri, text)
        # Here you could add diagnostic logic (syntax errors)
        return [] 

    def get(self, uri):
        return self.documents.get(uri)