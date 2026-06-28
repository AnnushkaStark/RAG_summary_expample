import io

from pypdf import PdfReader


class PDFTextExtractor:
    @staticmethod
    def extract_text_from_bytes(bytes_sretam: io.BytesIO) -> str:
        reader = PdfReader(bytes_sretam)
        extracted_text = []

        for _, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_text.append(page_text)

        full_text = "\n".join(extracted_text)

        return full_text
