import unittest
import gzip
import json
from reactomegsa_viz import HtmlReportGenerator
import os
import tempfile

currentdir = os.path.dirname(__file__)

class HtmlReportGeneratorTest(unittest.TestCase):
    def setUp(self):
        # create the path to the test file
        with gzip.open(os.path.join(currentdir, "result.json.gz"), "rb") as result_reader:
            self._analysis_result = json.load(result_reader)

    def test_html_creation(self):
        html_code = HtmlReportGenerator.create_report(self._analysis_result, r_script_token="TEST")

        self.assertIsNotNone(html_code, "HTML code not returned")

        # a rather random length check
        self.assertGreater(len(html_code), 1000, "HTML code too short")

    def test_writing_html_code(self):
        # create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_file_name = tmp.name

            # remove again to write to this path
            os.unlink(temp_file_name)
            
            no_code = HtmlReportGenerator.create_report(self._analysis_result, r_script_token="TEST", out_html=temp_file_name)

            self.assertIsNone(no_code)
            self.assertTrue(os.path.exists(temp_file_name))

            # unlink
            os.unlink(temp_file_name)