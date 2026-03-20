# Custom Fortran-Style LSP for Text Files
A high-performance Language Server Protocol (LSP) implementation designed for .txt files, inspired by fortls but extending beyond its original capabilities. This server brings professional IDE features using Fortran-inspired logic.
## Features

- Semantic Tokens: Intelligent syntax highlighting that distinguishes between variables, subroutines, and keywords

<img width="300" height="364" alt="Screenshot_2026-03-20_20 31 29 (Edited)" src="https://github.com/user-attachments/assets/21b930e1-3cc1-465c-b27f-058253ed07ea" />



- Folding Ranges: Collapse and expand PROGRAM, SUBROUTINE, and IF/DO blocks

<img width="364" height="453" alt="Screenshot_2026-03-20_20 31 47" src="https://github.com/user-attachments/assets/f2edb5cc-2adf-4ed7-9b2a-96cb8737c758" />



- Hover Support: Detailed information about symbols under your cursor.

<img width="200" height="113" alt="Screenshot_2026-03-20_20 42 35" src="https://github.com/user-attachments/assets/4cd96993-0ce4-4657-9c1a-af1db68c7554" />



- Code Lens: Actionable links appearing above PROGRAM and SUBROUTINE declarations, allowing for quick navigation or "Run" triggers.

<img width="213" height="80" alt="Screenshot_2026-03-20_20 31 29 (Edited 2)" src="https://github.com/user-attachments/assets/108cd28c-3f06-4fc9-867e-af2913c5b410" />



- Auto-completion: Smart suggestions for Fortran keywords (IF, PROGRAM, CALL), built-in types (INTEGER, REAL), and locally defined variables or subroutines.

- Document Highlights: Click a variable to see all its occurrences in the file.
