#!/usr/bin/env python3
"""
Скрипт валидации файлов обмена (XML и JSON) между ЗУП 3.1 и ERP 2.
Проверяет корректность структуры данных, типов, обязательных полей
и логическую консистентность отбора действующих исполнительных листов.
"""

import json
import os
import sys
import xml.etree.ElementTree as ET

def test_json_sample(json_path):
    print(f"Testing JSON sample: {os.path.basename(json_path)}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert data.get("Формат") == "Transfer_IspolnitelnyList_ZUP_ERP", "Неверный формат пакета"
    assert data.get("Версия") == "1.0", "Неверная версия формата"
    assert "ДатаПереноса" in data, "Отсутствует ДатаПереноса"
    assert "Документы" in data, "Отсутствует массив Документы"
    assert isinstance(data["Документы"], list), "Документы должны быть массивом"
    assert len(data["Документы"]) == data.get("КоличествоДокументов"), "Несовпадение количества документов"

    required_doc_fields = [
        "УникальныйИдентификатор", "Номер", "Дата", "Организация",
        "ФизическоеЛицо", "Сотрудник", "Получатель", "БанковскийСчет",
        "ВидИсполнительногоДокумента", "НомерИсполнительногоДокумента",
        "ДатаВыдачи", "СпособРасчета", "Удержание", "ДатаНачала"
    ]

    for idx, doc in enumerate(data["Документы"], start=1):
        for field in required_doc_fields:
            assert field in doc, f"Документ #{idx}: отсутствует обязательное поле '{field}'"

        # Check Organization
        org = doc["Организация"]
        assert "ИНН" in org and "Наименование" in org, f"Документ #{idx}: некорректная структура Организация"

        # Check Individual
        fl = doc["ФизическоеЛицо"]
        assert "СНИЛС" in fl and "ФИО" in fl, f"Документ #{idx}: некорректная структура ФизическоеЛицо"

        # Check Recipient
        rec = doc["Получатель"]
        assert "Наименование" in rec, f"Документ #{idx}: отсутствует Получатель.Наименование"

        # Check Calculation Method
        assert doc["СпособРасчета"] in ["Процентом", "ФиксированнойСуммой", "Долей"], \
            f"Документ #{idx}: некорректный способ расчета '{doc['СпособРасчета']}'"

    print(f"  [OK] JSON sample is valid! Total documents checked: {len(data['Документы'])}")
    return True

def test_xml_sample(xml_path):
    print(f"Testing XML sample: {os.path.basename(xml_path)}...")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    assert root.tag == "TransferData", f"Корневой элемент XML должен быть 'TransferData', получен: {root.tag}"
    assert root.attrib.get("Format") == "Transfer_IspolnitelnyList_ZUP_ERP", "Неверный атрибут Format"
    assert root.attrib.get("Version") == "1.0", "Неверный атрибут Version"
    assert "TransferDate" in root.attrib, "Отсутствует атрибут TransferDate"

    docs_elem = root.find("Documents")
    assert docs_elem is not None, "Элемент <Documents> не найден"

    docs = docs_elem.findall("IspolnitelnyList")
    assert len(docs) == int(root.attrib.get("Count", "0")), "Количество документов не совпадает с атрибутом Count"

    required_subtags = [
        "Number", "Date", "Organization", "Individual", "Employee",
        "Recipient", "BankAccount", "DocumentType", "DocumentNumber",
        "IssueDate", "CalculationMethod", "Deduction", "StartDate"
    ]

    for idx, doc in enumerate(docs, start=1):
        uuid_attr = doc.attrib.get("UUID")
        assert uuid_attr, f"Документ #{idx}: отсутствует атрибут UUID"

        for tag in required_subtags:
            child = doc.find(tag)
            assert child is not None, f"Документ #{idx}: отсутствует обязательный тег <{tag}>"

        org = doc.find("Organization")
        assert org.find("INN") is not None and org.find("Name") is not None, \
            f"Документ #{idx}: некорректные теги в <Organization>"

        fl = doc.find("Individual")
        assert fl.find("SNILS") is not None and fl.find("FullName") is not None, \
            f"Документ #{idx}: некорректные теги в <Individual>"

        calc_method = doc.find("CalculationMethod").text
        assert calc_method in ["Процентом", "ФиксированнойСуммой", "Долей"], \
            f"Документ #{idx}: некорректный способ расчета '{calc_method}'"

        reg_info = doc.find("PlannedDeductionsRegisterInfo")
        assert reg_info is not None, f"Документ #{idx}: отсутствует тег <PlannedDeductionsRegisterInfo>"
        assert reg_info.find("IsActiveInRegister").text == "true", \
            f"Документ #{idx}: в регистре ПлановыеУдержания удержание должно быть действующим (true)"

    print(f"  [OK] XML sample is valid! Total documents checked: {len(docs)}")
    return True

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    samples_dir = os.path.join(root, "samples")

    xml_path = os.path.join(samples_dir, "ПримерВыгрузки_ИсполнительныеЛисты.xml")
    json_path = os.path.join(samples_dir, "ПримерВыгрузки_ИсполнительныеЛисты.json")

    all_ok = True
    if not test_xml_sample(xml_path):
        all_ok = False
    if not test_json_sample(json_path):
        all_ok = False

    if not all_ok:
        sys.exit(1)
    print("\nAll exchange samples passed validation!")

if __name__ == "__main__":
    main()
