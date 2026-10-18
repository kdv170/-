#!/usr/bin/env python3
"""
Скрипт сборки внешней обработки 1С:Предприятие 8.3 (.epf).
Формирует двоичный контейнер формата 1С:Предприятие (compound file)
из исходных файлов модулей и метаданных.
"""

import base64
import hashlib
import io
import os
import shutil
import struct
import tempfile
import uuid
import zlib
from v8unpack.container import Container

def deflate(data: bytes) -> bytes:
    """Сжатие потока алгоритмом Deflate (RFC 1951, raw without zlib header)"""
    comp = zlib.compressobj(level=6, wbits=-15)
    return comp.compress(data) + comp.flush()

def build_epf(src_dir: str, output_epf_path: str):
    print(f"Сборка внешней обработки: {output_epf_path}...")
    
    file_uuid = "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d"
    obj_uuid  = "b2c3d4e5-f6a7-4b5c-9d0e-1f2a3b4c5d6e"
    container_uuid = "c3d4e5f6-a7b8-4c5d-0e1f-2a3b4c5d6e7f"

    files_raw = {}
    
    # Служебные файлы контейнера 1С
    files_raw['root'] = f'{{"2", "{file_uuid}", ""}}'.encode('utf-8')
    files_raw['version'] = '{"216", "0", {"80316", "0"}}'.encode('utf-8')
    files_raw['copyinfo'] = '{"4", {"0"}, {"0"}, {"0"}, {"0", "0"}, {"0"}}'.encode('utf-8')

    # Описание структуры метаданных внешней обработки
    header_content = (
        f'{{1, '
        f'{{c3831ec8-d8d5-4f93-8a22-f9bfae07327f, 0, 0}}, '
        f'0, '
        f'{{c3831ec8-d8d5-4f93-8a22-f9bfae07327f, '
        f'{{1, {container_uuid}, 0, '
        f'{{0, {{0, 0, {obj_uuid}}}, "ПереносИсполнительныхЛистовИзЗУПвERP", '
        f'{{1, "ru", "Перенос документов Исполнительный лист из ЗУП 3.1 в ERP 2"}}, '
        f'"", 0, 0, 0}}}}'
        f'}}'
        f'}}'
    )
    files_raw[file_uuid] = header_content.encode('utf-8')

    # Чтение модуля объекта
    obj_module_path = os.path.join(src_dir, 'МодульОбъекта.bsl')
    with open(obj_module_path, 'r', encoding='utf-8') as f:
        bsl_code = f.read()

    # В 1С модули хранятся с UTF-8 BOM
    files_raw[f'{obj_uuid}.0'] = b'\xef\xbb\xbf' + bsl_code.encode('utf-8')

    # Таблица версий потоков (versions)
    sorted_names = sorted(list(files_raw.keys()))
    versions_parts = [str(len(sorted_names))]
    for name in sorted_names:
        sha = base64.b64encode(hashlib.sha1(files_raw[name]).digest()).decode('ascii')
        versions_parts.append(f'"{name}"')
        versions_parts.append(f'"{sha}"')

    files_raw['versions'] = ('{' + ', '.join(versions_parts) + '}').encode('utf-8')

    # Упаковка в compound-контейнер
    tmp_dir = tempfile.mkdtemp()
    try:
        c = Container()
        with open(output_epf_path, 'w+b') as f:
            c.file = f
            c.write_header(len(files_raw))

            for name, raw_bytes in files_raw.items():
                compressed = deflate(raw_bytes)
                tpath = os.path.join(tmp_dir, name)
                with open(tpath, 'wb') as tf:
                    tf.write(compressed)
                with open(tpath, 'rb') as tf:
                    c.add_file(tf, name, inflate=False)

            c.write_table_off_content()

        print(f"Успешно собран файл EPF: {output_epf_path} (размер: {os.path.getsize(output_epf_path)} байт)")
        
        # Проверка целостности контейнера
        c_verify = Container()
        with open(output_epf_path, 'rb') as f:
            c_verify.read(f)
            entries = sorted(list(c_verify.files.keys()))
            print(f"Потоков в контейнере: {len(entries)} ({', '.join(entries)})")
            assert len(entries) == len(files_raw), "Не совпадает число потоков"
            
        print("Проверка целостности EPF пройдена успешно!\n")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(root_dir, 'src')
    output_path = os.path.join(root_dir, 'ПереносИсполнительныхЛистовИзЗУПвERP.epf')
    build_epf(src_dir, output_path)
