import re
from dataclasses import dataclass, field


@dataclass
class PIIFinding:
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        return len(self.emails) + len(self.phones)

    @property
    def has_pii(self) -> bool:
        return self.total_count > 0

    def summary_tr(self) -> str:
        parts = []
        if self.emails:
            parts.append(f"{len(self.emails)} e-posta")
        if self.phones:
            parts.append(f"{len(self.phones)} telefon")
        return " ve ".join(parts) if parts else "yok"


class PIISanitizer:

    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
    )
    PHONE_PATTERN = re.compile(
        r"(?<!\d)"
        r"(?:"
        r"\+?\d{1,3}[\s\-.]?\(?\d{2,4}\)?[\s\-.]?\d{3}[\s\-.]?\d{2}[\s\-.]?\d{2}"
        r"|0\d{3}[\s\-.]?\d{3}[\s\-.]?\d{2}[\s\-.]?\d{2}"
        r"|\(\d{3}\)[\s\-.]?\d{3}[\s\-.]?\d{4}"
        r")"
        r"(?!\d)"
    )

    MASK_EMAIL = "[E-POSTA GİZLENDİ]"
    MASK_PHONE = "[TELEFON GİZLENDİ]"

    def detect(self, text: str) -> PIIFinding:
        emails = self.EMAIL_PATTERN.findall(text)
        phones = self.PHONE_PATTERN.findall(text)
        return PIIFinding(emails=emails, phones=phones)

    def mask(self, text: str) -> str:
        masked = self.EMAIL_PATTERN.sub(self.MASK_EMAIL, text)
        masked = self.PHONE_PATTERN.sub(self.MASK_PHONE, masked)
        return masked

    def analyze(self, text: str, preview_chars: int = 400) -> tuple[PIIFinding, str]:
        finding = self.detect(text)
        masked_full = self.mask(text)
        preview = masked_full[:preview_chars]
        if len(masked_full) > preview_chars:
            preview += "..."
        return finding, preview
