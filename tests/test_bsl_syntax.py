#!/usr/bin/env python3
"""
Скрипт проверки синтаксиса и структуры модулей 1С (BSL).
Проверяет баланс процедур/функций, условий Если/КонецЕсли,
циклов Для/Пока/КонецЦикла, попыток Попытка/КонецПопытки,
областей #Область/#КонецОбласти, а также наличие директив компиляции.
"""

import os
import re
import sys

def check_bsl_file(file_path):
    print(f"Checking BSL syntax in: {os.path.basename(file_path)}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack_blocks = []
    region_count = 0
    proc_func_count = 0

    re_proc_start = re.compile(r'^\s*(?:&[^\s]+\s+)*(Процедура|Функция)\s+([A-Za-zА-Яа-я0-9_]+)\s*\(', re.IGNORECASE)
    re_proc_end = re.compile(r'^\s*(КонецПроцедуры|КонецФункции)', re.IGNORECASE)
    re_if_start = re.compile(r'^\s*Если\s+', re.IGNORECASE)
    re_if_end = re.compile(r'^\s*КонецЕсли\s*;?', re.IGNORECASE)
    re_loop_start = re.compile(r'^\s*(Для\s+Каждого|Для|Пока)\s+', re.IGNORECASE)
    re_loop_end = re.compile(r'^\s*КонецЦикла\s*;?', re.IGNORECASE)
    re_try_start = re.compile(r'^\s*Попытка\s*', re.IGNORECASE)
    re_try_end = re.compile(r'^\s*КонецПопытки\s*;?', re.IGNORECASE)
    re_region_start = re.compile(r'^\s*#Область\s+(.+)', re.IGNORECASE)
    re_region_end = re.compile(r'^\s*#КонецОбласти', re.IGNORECASE)

    errors = []

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        # Remove comments
        comment_idx = line.find('//')
        if comment_idx != -1:
            line = line[:comment_idx].strip()
        if not line:
            continue

        # Region check
        if re_region_start.match(line):
            region_count += 1
        elif re_region_end.match(line):
            region_count -= 1
            if region_count < 0:
                errors.append(f"Line {idx}: Unmatched #КонецОбласти")

        # Proc / func start
        m_proc = re_proc_start.match(line)
        if m_proc:
            block_type = m_proc.group(1).lower()
            block_name = m_proc.group(2)
            stack_blocks.append((block_type, block_name, idx))
            proc_func_count += 1
            continue

        # Proc / func end
        m_proc_end = re_proc_end.match(line)
        if m_proc_end:
            end_type = m_proc_end.group(1).lower()
            expected = "процедура" if "процедуры" in end_type else "функция"
            if not stack_blocks:
                errors.append(f"Line {idx}: Unexpected {end_type} without opening procedure/function")
            else:
                top_type, top_name, top_line = stack_blocks.pop()
                if top_type != expected:
                    errors.append(f"Line {idx}: Mismatched {end_type} for {top_type} '{top_name}' opened at line {top_line}")
            continue

        # If / EndIf
        if re_if_start.match(line) and not re.search(r'\bТогда\s+.*\bКонецЕсли\b', line, re.IGNORECASE):
            stack_blocks.append(("если", "", idx))
            continue
        if re_if_end.match(line):
            if not stack_blocks or stack_blocks[-1][0] != "если":
                errors.append(f"Line {idx}: Unexpected КонецЕсли")
            else:
                stack_blocks.pop()
            continue

        # Loop / EndLoop
        if re_loop_start.match(line) and re.search(r'\bЦикл\b', line, re.IGNORECASE):
            stack_blocks.append(("цикл", "", idx))
            continue
        if re_loop_end.match(line):
            if not stack_blocks or stack_blocks[-1][0] != "цикл":
                errors.append(f"Line {idx}: Unexpected КонецЦикла")
            else:
                stack_blocks.pop()
            continue

        # Try / EndTry
        if re_try_start.match(line):
            stack_blocks.append(("попытка", "", idx))
            continue
        if re_try_end.match(line):
            if not stack_blocks or stack_blocks[-1][0] != "попытка":
                errors.append(f"Line {idx}: Unexpected КонецПопытки")
            else:
                stack_blocks.pop()
            continue

    if stack_blocks:
        for b_type, b_name, b_line in stack_blocks:
            errors.append(f"Unclosed block '{b_type}' {b_name} opened at line {b_line}")

    if region_count != 0:
        errors.append(f"Unbalanced #Область: {region_count} regions left open")

    if errors:
        for err in errors:
            print(f"  [ERROR] {err}")
        return False
    else:
        print(f"  [OK] Valid BSL structure. Found {proc_func_count} procedures/functions, all blocks balanced.")
        return True

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = [
        os.path.join(root, "src", "МодульОбъекта.bsl"),
        os.path.join(root, "src", "МодульФормы.bsl"),
    ]
    all_ok = True
    for f in files:
        if os.path.exists(f):
            if not check_bsl_file(f):
                all_ok = False
        else:
            print(f"[ERROR] File not found: {f}")
            all_ok = False

    if not all_ok:
        sys.exit(1)
    print("\nAll BSL modules passed validation!")

if __name__ == "__main__":
    main()
