from regex import FortranRegularExpressions as FRE
import re

class Symbol:
    def __init__(self, name, kind, line, col, signature=""):
        self.name = name
        self.kind = kind  # 'program', 'subroutine', 'variable', 'keyword'
        self.line = line
        self.col = col
        self.signature = signature

class FortranFile:
    def __init__(self, uri, text):
        self.uri = uri
        self.text = text
        self.lines = text.splitlines()
        self.symbols = []
        self.parse()

    def parse(self):
        """
        Processes the file line-by-line to build a list of symbols.
        Order of operations matters to prevent keywords from 'stealing' 
        the coordinates of program or variable names.
        """
        self.symbols = []
        lines = self.text.splitlines()

        for i, line in enumerate(lines):
            prog_match = FRE.PROG.search(line)
            if prog_match:
                self.symbols.append(Symbol(prog_match.group(1), 'program', i, prog_match.start(1)))

            sub_match = FRE.SUB.search(line)
            if sub_match:
                sig_match = FRE.SUB_PAREN.search(line, sub_match.end())
                sig = sig_match.group(0) if sig_match else "()"
                self.symbols.append(Symbol(sub_match.group(1), 'subroutine', i, sub_match.start(1), sig))

            var_match = FRE.VAR.search(line)
            if var_match:
                name_match = FRE.WORD.search(line, var_match.end())
                if name_match:
                    self.symbols.append(Symbol(name_match.group(0), 'variable', i, name_match.start()))

            keyword_pattern = r"\b(IF|THEN|ELSE|END|PROGRAM|SUBROUTINE|INTEGER|DO)\b"
            for kw in re.finditer(keyword_pattern, line, re.IGNORECASE):
                # Only add if this spot isn't already a Program or Subroutine name
                if not any(s.line == i and s.col == kw.start() for s in self.symbols):
                    self.symbols.append(Symbol(kw.group(0), 'keyword', i, kw.start()))

            # 4. IDENTIFY USAGE (Words that aren't keywords or names yet)
            # This catches 'fghj' or 'joke' in your example
            for word_match in FRE.WORD.finditer(line):
                word = word_match.group(0)
                # Ignore numbers and booleans
                if FRE.NUMBER.match(word) or FRE.LOGICAL.match(word):
                    continue
                # If the coordinate is empty, it's a variable usage
                if not any(s.line == i and s.col == word_match.start() for s in self.symbols):
                    self.symbols.append(Symbol(word, 'variable', i, word_match.start()))

class WorkspaceManager:
    def __init__(self):
        self.documents = {}

    def update(self, uri, text):
        self.documents[uri] = FortranFile(uri, text)
        # Here you could add diagnostic logic (syntax errors)
        return [] 

    def get(self, uri):
        return self.documents.get(uri)