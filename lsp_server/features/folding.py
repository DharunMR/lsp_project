from regex import FortranRegularExpressions as FRE

def get_folding_ranges(file_obj):
    ranges = []
    stack = [] 
    lines = file_obj.text.splitlines()

    for i, line in enumerate(lines):
        line_content = line.split('!')[0]
        line_upper = line_content.upper().strip()
        
        if not line_upper:
            continue

        if FRE.END_WORD.search(line_content):
            if stack:
                start_line = stack.pop()
                if i > start_line:
                    ranges.append({
                        "startLine": start_line,
                        "endLine": i - 1,
                        "kind": "region"
                    })
            continue

        is_start = False
        
        if FRE.SUB.search(line_content) or FRE.FUN.search(line_content):
            is_start = True
        elif FRE.PROG.search(line_content):
            is_start = True
        elif FRE.IF.search(line_content) and ("THEN" in line_upper):
            is_start = True
        elif FRE.DO.search(line_content):
            is_start = True
        elif FRE.SELECT.search(line_content):
            is_start = True
        elif FRE.MOD.search(line_content):
            is_start = True

        if is_start:
            stack.append(i)

    return ranges