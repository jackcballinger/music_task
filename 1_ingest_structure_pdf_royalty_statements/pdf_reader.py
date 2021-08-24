from pathlib import Path

import pdfplumber
import tabula

class PDFReader:
    def __init__(self, config, pdf_path):
        self._config = config
        self._n_rows = self._config.get('n_rows', None)
        del self._config['n_rows']
        self._pdf_path = pdf_path

    def get_pdf_tables(self, multiple_tables=True, pages='all'):
        return tabula.read_pdf(
            self._pdf_path,
            multiple_tables=multiple_tables,
            pages=pages
        )
    
    def get_pdf_text(self):
        with pdfplumber.open(self._pdf_path) as f:
            pdf_pages = f.pages[int(self._config['pages'].split('-')[0]): int(self._config['pages'].split('-')[1])]
            return [
                {
                    'page_no': i,
                    'text': page.extract_text().splitlines()[:self._n_rows]
                } for i, page in enumerate(pdf_pages)
            ]

    def read_tables(self):
        return self.get_pdf_text(), self.get_pdf_tables(**self._config)