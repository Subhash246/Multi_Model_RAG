from io import BytesIO

from pypdf import PdfWriter

from app.services.parsing.pdf import PDFParser
from app.services.parsing.models import NormalizedDocument


def create_test_pdf() -> bytes:
    """
    Create a minimal in-memory PDF for testing.

    We are only testing the parser contract here.
    """

    writer = PdfWriter()

    writer.add_blank_page(
        width=612,
        height=792,
    )

    output = BytesIO()

    writer.write(output)

    return output.getvalue()


def test_pdf_parser_returns_normalized_document():
    pdf_data = create_test_pdf()

    parser = PDFParser()

    result = parser.parse(
        file_data=pdf_data,
        content_type="application/pdf",
        document_id="test-document-123",
    )

    assert isinstance(
        result,
        NormalizedDocument,
    )

    assert result.document_id == "test-document-123"

    assert result.content_type == "application/pdf"

    assert result.page_count == 1

    assert len(result.pages) == 1

    assert result.pages[0].page_number == 1

    assert result.extraction["parser"] == "pypdf"

    assert result.extraction["page_count"] == 1