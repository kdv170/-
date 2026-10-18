from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
OBJECT_MODULE = (
    SOURCE / "ПереносИсполнительныхЛистов" / "Ext" / "ObjectModule.bsl"
)


class ProcessingSourcesTest(unittest.TestCase):
    def test_xml_sources_are_well_formed(self):
        xml_files = list(SOURCE.rglob("*.xml"))
        self.assertGreaterEqual(len(xml_files), 3)
        for xml_file in xml_files:
            with self.subTest(xml_file=xml_file):
                ET.parse(xml_file)

    def test_bsl_blocks_are_balanced(self):
        for module in SOURCE.rglob("*.bsl"):
            text = module.read_text(encoding="utf-8")
            with self.subTest(module=module):
                self.assertEqual(
                    len(re.findall(r"(?im)^\s*(?:процедура|функция)\b", text)),
                    len(re.findall(r"(?im)^\s*конец(?:процедуры|функции)\b", text)),
                )
                self.assertEqual(
                    len(re.findall(r"(?im)^\s*#область\b", text)),
                    len(re.findall(r"(?im)^\s*#конецобласти\b", text)),
                )

    def test_selection_uses_active_planned_deductions_slice(self):
        text = OBJECT_MODULE.read_text(encoding="utf-8")
        self.assertIn(
            "РегистрСведений.ПлановыеУдержания.СрезПоследних(&ДатаПереноса)",
            text,
        )
        self.assertIn("ПлановыеУдержания.Используется", text)
        self.assertIn(
            "ДокументОснование ССЫЛКА Документ.ИсполнительныйЛист", text
        )

    def test_import_has_duplicate_guard_and_per_document_transaction(self):
        text = OBJECT_MODULE.read_text(encoding="utf-8")
        self.assertIn("МаркерИсточника", text)
        self.assertIn("ИсходныйUUID", text)
        self.assertIn("НачатьТранзакцию()", text)
        self.assertIn("ЗафиксироватьТранзакцию()", text)
        self.assertIn("ОтменитьТранзакцию()", text)
        self.assertIn('Блокировка.Добавить("Документ.ИсполнительныйЛист")', text)

    def test_export_applies_effective_conditions_and_remaining_limit(self):
        text = OBJECT_MODULE.read_text(encoding="utf-8")
        self.assertIn("ПлановыеУдержания.Регистратор", text)
        self.assertIn("ДополнитьАктуальнымиУсловиями", text)
        self.assertIn("УдержанияДоПределаПоСотрудникам.Остатки(", text)


if __name__ == "__main__":
    unittest.main()
