"""
Routes documents to the appropriate parser based on content type.
"""

from app.services.parsing.base import BaseParser
from app.services.parsing.pdf import PDFParser


class ParserRouter:

    def __init__(self) -> None:

        self._parsers: dict[str, BaseParser] = {
            "application/pdf": PDFParser(),
        }

    def get_parser(
        self,
        content_type: str,
    ) -> BaseParser:

        parser = self._parsers.get(content_type)

        if parser is None:
            raise ValueError(
                f"No parser available for content type: {content_type}"
            )

        return parser