import math
import re
import unicodedata
from dataclasses import dataclass
from io import BytesIO

import pypdfium2 as pdfium
import pytesseract
from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError
from pytesseract import TesseractError


class DocumentProcessingError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class PageText:
    page_number: int
    content: str


@dataclass(frozen=True)
class TextChunk:
    ordinal: int
    page_number: int
    content: str
    token_count: int


def extract_pages(pdf_bytes: bytes, max_pages: int) -> list[PageText]:
    try:
        reader = PdfReader(BytesIO(pdf_bytes), strict=True)
        if reader.is_encrypted:
            raise DocumentProcessingError(
                "encrypted_pdf", "Password-protected PDFs are not supported."
            )
        page_count = len(reader.pages)
        if page_count == 0:
            raise DocumentProcessingError("empty_pdf", "The PDF has no pages.")
        if page_count > max_pages:
            raise DocumentProcessingError("page_limit_exceeded", "The PDF exceeds the page limit.")
    except DocumentProcessingError:
        raise
    except (PdfReadError, PdfStreamError, ValueError) as exc:
        raise DocumentProcessingError("invalid_pdf", "The PDF could not be read.") from exc

    rendered_document = None
    pages: list[PageText] = []
    try:
        for page_index, page in enumerate(reader.pages):
            try:
                text = page.extract_text(extraction_mode="layout") or ""
            except (PdfReadError, PdfStreamError, ValueError) as exc:
                raise DocumentProcessingError(
                    "page_extraction_failed", "A PDF page could not be extracted."
                ) from exc
            if len(text.strip()) < 40:
                if rendered_document is None:
                    rendered_document = pdfium.PdfDocument(pdf_bytes)
                text = _ocr_page(rendered_document, page_index)
            normalized = _normalize_text(text)
            if normalized:
                pages.append(PageText(page_number=page_index + 1, content=normalized))
    except DocumentProcessingError:
        raise
    except (RuntimeError, ValueError) as exc:
        raise DocumentProcessingError(
            "document_processing_failed", "The PDF could not be processed."
        ) from exc
    finally:
        if rendered_document is not None:
            rendered_document.close()

    if not pages:
        raise DocumentProcessingError(
            "no_extractable_text",
            "No readable text was found. Check the scan quality and OCR language.",
        )
    return pages


def _ocr_page(document: pdfium.PdfDocument, page_index: int) -> str:
    page = document[page_index]
    bitmap = None
    image = None
    try:
        width, height = page.get_size()
        if width <= 0 or height <= 0:
            raise DocumentProcessingError("invalid_page_size", "A PDF page has invalid dimensions.")
        scale = min(2.0, math.sqrt(20_000_000 / (width * height)))
        if scale < 0.5:
            raise DocumentProcessingError(
                "page_size_limit_exceeded", "A PDF page is too large to OCR."
            )
        bitmap = page.render(scale=scale)
        image = bitmap.to_pil()
        return pytesseract.image_to_string(image, lang="eng", timeout=15)
    except pytesseract.TesseractNotFoundError as exc:
        raise DocumentProcessingError("ocr_unavailable", "Tesseract OCR is not installed.") from exc
    except TesseractError as exc:
        raise DocumentProcessingError("ocr_failed", "OCR could not read a scanned page.") from exc
    finally:
        if image is not None:
            image.close()
        if bitmap is not None:
            bitmap.close()
        page.close()


def chunk_pages(
    pages: list[PageText],
    max_chunks: int,
    target_characters: int = 4000,
    overlap_characters: int = 400,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    for page in pages:
        text = page.content
        start = 0
        while start < len(text):
            end = min(start + target_characters, len(text))
            if end < len(text):
                boundary = text.rfind(" ", start + target_characters // 2, end)
                if boundary > start:
                    end = boundary
            content = text[start:end].strip()
            if content:
                chunks.append(
                    TextChunk(
                        ordinal=len(chunks),
                        page_number=page.page_number,
                        content=content,
                        token_count=max(1, math.ceil(len(content) / 4)),
                    )
                )
                if len(chunks) > max_chunks:
                    raise DocumentProcessingError(
                        "chunk_limit_exceeded", "The PDF exceeds the document chunk limit."
                    )
            if end >= len(text):
                break
            start = max(start + 1, end - overlap_characters)
    return chunks


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = "".join(
        character for character in normalized if character.isprintable() or character in "\n\t"
    )
    return re.sub(r"[ \t]+\n", "\n", normalized).strip()
