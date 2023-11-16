from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Email:

    sender: str
    reply_to: str
    recipients: List[str]
    subject: str

    text_content: str
    html_content: Optional[str]

    attachments: List['Attachment']


@dataclass(frozen=True)
class Attachment:

    filename: str
    content_type: str
    file_contents: bytes
