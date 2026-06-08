from abc import ABC, abstractmethod
from pathlib import Path

from PyPDF2 import PdfReader

from cv_analyzer.models import Resume


class FileParser(ABC):

    @abstractmethod
    def parse(self, file_path: str) -> Resume:
        pass

    @staticmethod
    def _clean_text(text: str) -> str:
        text = text.replace("\x00", " ")
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line)


class TextParser(FileParser):

    def parse(self, file_path: str) -> Resume:
        path = Path(file_path)
        raw_text = path.read_text(encoding="utf-8", errors="ignore")
        return Resume(raw_text=self._clean_text(raw_text), filename=path.name)


class PDFParser(FileParser):

    def parse(self, file_path: str) -> Resume:
        path = Path(file_path)
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        raw_text = "\n".join(pages)
        return Resume(raw_text=self._clean_text(raw_text), filename=path.name)


class ParserFactory:

    _parsers: dict[str, type[FileParser]] = {
        ".txt": TextParser,
        ".pdf": PDFParser,
    }

    @classmethod
    def get_parser(cls, file_path: str) -> FileParser:
        suffix = Path(file_path).suffix.lower()
        parser_cls = cls._parsers.get(suffix)
        if parser_cls is None:
            raise ValueError(f"Desteklenmeyen format: {suffix}")
        return parser_cls()
