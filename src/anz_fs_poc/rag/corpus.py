from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Chunk:
    doc_id: str
    section: str
    text: str
    effective: str = ""
    jurisdiction: str = "AU"


_DOC_ID_RE = re.compile(r"\*\*doc_id:\*\*\s*(\S+)", re.I)
_EFFECTIVE_RE = re.compile(r"\*\*effective:\*\*\s*(\S+)", re.I)
_HEADING_RE = re.compile(r"^(#{2,3})\s+(.*)$", re.M)


def _parse_doc(path: Path) -> list[Chunk]:
    raw = path.read_text(encoding="utf-8")
    doc_id_match = _DOC_ID_RE.search(raw)
    doc_id = doc_id_match.group(1) if doc_id_match else path.stem
    effective_match = _EFFECTIVE_RE.search(raw)
    effective = effective_match.group(1) if effective_match else ""

    parts = _HEADING_RE.split(raw)
    # parts: [preamble, level, title, body, level, title, body, ...]
    chunks: list[Chunk] = []
    if len(parts) == 1:
        chunks.append(Chunk(doc_id=doc_id, section="document", text=raw.strip(), effective=effective))
        return chunks

    # Skip preamble (parts[0]); then triples of (level, title, body)
    i = 1
    while i + 2 < len(parts):
        title = parts[i + 1].strip()
        body = parts[i + 2].strip()
        if body:
            chunks.append(
                Chunk(
                    doc_id=doc_id,
                    section=title,
                    text=f"{title}\n{body}",
                    effective=effective,
                )
            )
        i += 3
    return chunks


def load_corpus(corpus_dir: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(corpus_dir.glob("*.md")):
        chunks.extend(_parse_doc(path))
    return chunks
