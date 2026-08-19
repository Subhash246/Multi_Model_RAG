"""
PDF parser implementation.

Currently uses pypdf for text extraction.

Layout-aware extraction, OCR, tables, and other multimodal
processing will be introduced behind this parser boundary later.
"""

from io import BytesIO

from pypdf import PdfReader

from app.services.parsing.base import BaseParser
from app.services.parsing.models import (
    NormalizedDocument,
    ParsedPage,
)


class PDFParser(BaseParser):

    def parse(
        self,
        file_data: bytes,
        content_type: str,
        document_id: str,
    ) -> NormalizedDocument:
        """
        Extract text page-by-page from a PDF.
        """

        reader = PdfReader(BytesIO(file_data))

        pages: list[ParsedPage] = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            text = page.extract_text() or ""

            pages.append(
                ParsedPage(
                    page_number=page_number,
                    text=text,
                )
            )

        return NormalizedDocument(
            document_id=document_id,
            content_type=content_type,
            pages=pages,
            metadata={},
            extraction={
                "parser": "pypdf",
                "page_count": len(pages),
                "character_count": sum(
                    len(page.text)
                    for page in pages
                ),
            },
        )