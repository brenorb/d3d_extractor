import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import fitz
from fastapi.testclient import TestClient

with patch.dict(sys.modules, {
    "src.extraction.extractor": SimpleNamespace(LabDataExtractor=object),
    "src.ocr.processor": SimpleNamespace(OcrProcessor=object),
}):
    from api import main


def synthetic_pdf() -> bytes:
    with fitz.open() as document:
        for index in range(2):
            page = document.new_page()
            page.insert_text((50, 50), f"Fixture page {index}")
        return document.tobytes()


class UploadCleanupTests(unittest.TestCase):
    def request(self, split_pages):
        with tempfile.TemporaryDirectory() as root:
            with (
                patch.object(tempfile, "tempdir", root),
                patch.object(main, "split_pdf_into_pages", side_effect=split_pages),
                patch.object(main, "get_ocr_processor", return_value=SimpleNamespace(
                    process=lambda _path: {"fixture": "synthetic text"}
                )),
                patch.object(main, "get_extractor", return_value=SimpleNamespace(
                    extract=lambda _text: {"fixture": "ok"}
                )),
                TestClient(main.app) as client,
            ):
                response = client.post("/process-lab-results", files={
                    "file": ("synthetic.pdf", synthetic_pdf(), "application/pdf"),
                })
            leftovers = sorted(str(path.relative_to(root)) for path in Path(root).rglob("*"))
            return response, leftovers

    def test_success_removes_source_and_page_workspace(self):
        response, leftovers = self.request(main.split_pdf_into_pages)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["pages_processed"], 2)
        self.assertEqual(leftovers, [])

    def test_splitter_failure_removes_pages_it_did_not_return(self):
        original_split = main.split_pdf_into_pages

        def fail_after_saving_pages(*args, **kwargs):
            original_split(*args, **kwargs)
            raise RuntimeError("fixture splitter failure after writing pages")

        response, leftovers = self.request(fail_after_saving_pages)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(leftovers, [])
