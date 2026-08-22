from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from utils.dates import get_current_period
from utils.files import create_output_folder, safe_filename, unique_path, validate_ruc


class UtilityTests(unittest.TestCase):
    def test_current_period_in_spanish(self):
        self.assertEqual(get_current_period(datetime(2026, 8, 21)), {"year": 2026, "month": 8, "month_name": "Agosto"})

    def test_ruc_format(self):
        self.assertTrue(validate_ruc("0999999999001"))
        self.assertFalse(validate_ruc("0999"))

    def test_safe_unique_file(self):
        period = {"year": 2026, "month": 8, "month_name": "Agosto"}
        with TemporaryDirectory() as temp:
            folder = create_output_folder("0999999999001", period, Path(temp))
            filename = safe_filename("0999999999001", period, "Notas/Crédito", ".xlsx")
            first = unique_path(folder, filename); first.touch()
            self.assertTrue(unique_path(folder, filename).name.endswith("_01.xlsx"))
