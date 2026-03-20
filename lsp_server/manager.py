from dataclasses import dataclass
from typing import List, Dict, Optional
import re
from regex import FortranRegularExpressions as FRE

@dataclass(slots=True, frozen=True)
class Symbol:
    name: str
    kind: str
    line: int
    col: int
    signature: str = ""

class FortranFile:
    def __init__(self, uri: str, text: str):
        self.uri = uri
        self.text = text
        self.lines = text.splitlines()
        self.symbols: List[Symbol] = []
        self.parse()

    def parse(self):
        self.symbols = []
        keyword_pattern = re.compile(
            r"\b(IF|THEN|ELSE|END|DO|CALL|USE|CONTAINS|IMPLICIT|NONE|ONLY|SELECT|CASE|ALLOCATABLE|PARAMETER|INTENT|IN|OUT)\b", 
            re.IGNORECASE
        )
        
        type_pattern = re.compile(r"\b(INTEGER|REAL|LOGICAL|CHARACTER|COMPLEX|DOUBLE\s+PRECISION|TYPE)\b", re.IGNORECASE)

        for i, line in enumerate(self.lines):
            line_len = len(line)
            if line_len == 0: continue
            
            mask = [False] * line_len

            def add_symbol(name: str, kind: str, start: int, end: int, sig: str = ""):
                if 0 <= start < line_len and not any(mask[start:end]):
                    self.symbols.append(Symbol(name, kind, i, start, sig))
                    for j in range(start, end): mask[j] = True

            for m in FRE.FREE_COMMENT.finditer(line):
                add_symbol(m.group(0), 'comment', m.start(), m.end())
            
            for m in list(FRE.SQ_STRING.finditer(line)) + list(FRE.DQ_STRING.finditer(line)):
                add_symbol(m.group(0), 'string', m.start(), m.end())

            for m in FRE.NUMBER.finditer(line):
                add_symbol(m.group(0), 'number', m.start(), m.end())

            if match := re.search(r"\b(PROGRAM)\s+(\w+)\b", line, re.I):
                add_symbol(match.group(1), 'keyword', match.start(1), match.end(1))
                add_symbol(match.group(2), 'program', match.start(2), match.end(2))

            if match := re.search(r"\b(SUBROUTINE)\s+(\w+)\b", line, re.I):
                add_symbol(match.group(1), 'keyword', match.start(1), match.end(1))
                add_symbol(match.group(2), 'subroutine', match.start(2), match.end(2))

            for m in type_pattern.finditer(line):
                add_symbol(m.group(1), 'type', m.start(1), m.end(1))

            for m in keyword_pattern.finditer(line):
                add_symbol(m.group(0), 'keyword', m.start(), m.end())

            for m in FRE.WORD.finditer(line):
                if FRE.LOGICAL.match(m.group(0)):
                    add_symbol(m.group(0), 'keyword', m.start(), m.end())
                else:
                    add_symbol(m.group(0), 'variable', m.start(), m.end())


class WorkspaceManager:
    def __init__(self):
        self.documents: Dict[str, FortranFile] = {}

    def update(self, uri: str, text: str) -> list:
        try:
            self.documents[uri] = FortranFile(uri, text)
            return []
        except Exception as e:
            print(f"Error parsing {uri}: {e}")
            return []

    def get(self, uri: str) -> Optional[FortranFile]:
        return self.documents.get(uri)