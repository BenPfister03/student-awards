"""Package Guide chat transcripts the agent already wrote under docs/transcripts/.

The Guide agent (Copilot Agent, Cursor, or OpenCode) must collect every project
Guide chat into ``docs/transcripts/*.md`` before ``python manage.py report``.
This module does **not** scrape Cursor ``agent-transcripts`` or assume any IDE.
It only indexes existing markdown, writes INDEX.md, and builds the zip/PDF appendix.
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "docs" / "transcripts"
TRANSCRIPTS_HEADING = "## Session transcripts"
_TRANSCRIPTS_SECTION_RE = re.compile(
    r"^## Session transcripts\n.*?(?=^## (?:Competency \(student-judge\)|Skill integrity)|\Z)",
    re.MULTILINE | re.DOTALL,
)
_SKIP_NAMES = frozenset({"index.md", "readme.md"})


@dataclass(frozen=True)
class TranscriptExportResult:
    """Paths packaged for one report export."""

    out_dir: Path
    index_path: Path | None
    markdown_files: tuple[Path, ...]
    zip_path: Path | None
    source_roots: tuple[Path, ...]
    found: int


def list_transcript_markdown(out_dir: Path | None = None) -> list[Path]:
    """Return ``docs/transcripts/*.md`` files the Guide agent wrote (sorted)."""
    dest = out_dir or DEFAULT_OUT
    if not dest.is_dir():
        return []
    files: list[Path] = []
    for path in sorted(dest.glob("*.md")):
        if path.name.lower() in _SKIP_NAMES:
            continue
        if path.is_file():
            files.append(path)
    return files


def package_transcripts(
    *,
    out_dir: Path | None = None,
    make_zip: bool = True,
) -> TranscriptExportResult:
    """Index agent-written transcripts, write INDEX.md, and optionally zip them.

    Does not invent or discover chats. Empty folder means the Guide has not
    pulled transcripts yet.
    """
    dest = out_dir or DEFAULT_OUT
    dest.mkdir(parents=True, exist_ok=True)
    written = list_transcript_markdown(dest)

    index = dest / "INDEX.md"
    index_body = [
        "# Session transcripts",
        "",
        "Filled by the **Guide agent** (Copilot Agent, Cursor, or OpenCode) when",
        "building the report — one markdown file per Guide chat for this project.",
        "`python manage.py report` only packages these files; it does not scrape an IDE.",
        "",
        f"Chats packaged: **{len(written)}**",
        "",
    ]
    if written:
        index_body.append("| Chat | File |")
        index_body.append("| --- | --- |")
        for md in written:
            index_body.append(f"| `{md.stem}` | [{md.name}]({md.name}) |")
        index_body.append("")
    else:
        index_body.extend(
            [
                "_No transcript markdown found in this folder._",
                "",
                "Before export, the Guide must open every Guide chat for this project",
                "(all phases — Copilot Agent / Cursor / OpenCode) and write each to",
                "`docs/transcripts/<slug>.md` with student and assistant turns.",
                "",
            ]
        )
    index.write_text("\n".join(index_body), encoding="utf-8")

    zip_path: Path | None = None
    if make_zip:
        zip_path = dest.parent / "transcripts.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(dest.iterdir()):
                if path.is_file():
                    zf.write(path, arcname=f"transcripts/{path.name}")
        print(f"Wrote {zip_path}")

    print(f"Packaged {len(written)} transcript(s) from {dest}")
    return TranscriptExportResult(
        out_dir=dest,
        index_path=index if index.is_file() else None,
        markdown_files=tuple(written),
        zip_path=zip_path if zip_path and zip_path.is_file() else None,
        source_roots=(dest,),
        found=len(written),
    )


# Back-compat alias used by report_pdf / cli
def export_project_transcripts(
    *,
    out_dir: Path | None = None,
    repo: Path = REPO_ROOT,
    make_zip: bool = True,
) -> TranscriptExportResult:
    """Package transcripts already under docs/transcripts/ (agent-written)."""
    del repo  # unused; kept for call-site compatibility
    return package_transcripts(out_dir=out_dir, make_zip=make_zip)


def merge_transcripts_section(
    markdown: str,
    result: TranscriptExportResult,
) -> str:
    """Insert or replace the Session transcripts section in docs/report.md."""
    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    if result.found:
        bullets = "\n".join(
            f"- [`{path.stem}`](transcripts/{path.name})" for path in result.markdown_files
        )
        detail = (
            f"Guide packaged **{result.found}** chat(s) in `docs/transcripts/` "
            f"(and `docs/transcripts.zip`).\n\n"
            f"Index: [docs/transcripts/INDEX.md](transcripts/INDEX.md)\n\n"
            f"{bullets}\n"
        )
    else:
        detail = (
            "No transcript markdown in `docs/transcripts/` yet.\n\n"
            "The Guide agent must pull every Guide chat for this project "
            "(Copilot Agent, Cursor, or OpenCode — do not assume Cursor) and write "
            "each to `docs/transcripts/<slug>.md`, then re-run "
            "`python manage.py report`.\n"
        )
    section = (
        f"{TRANSCRIPTS_HEADING}\n\n"
        "Filled when the Guide builds the report: the agent writes chat markdown "
        "into `docs/transcripts/`; `python manage.py report` packages them.\n\n"
        f"{detail}"
    )

    def _insert_section(_match: re.Match[str]) -> str:
        return section.rstrip() + "\n\n"

    if _TRANSCRIPTS_SECTION_RE.search(text):
        text = _TRANSCRIPTS_SECTION_RE.sub(_insert_section, text, count=1)
    elif re.search(r"^## Competency \(student-judge\)\s*$", text, re.MULTILINE):
        text = re.sub(
            r"^## Competency \(student-judge\)\s*$",
            lambda _m: section + "\n## Competency (student-judge)",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    elif re.search(r"^## Skill integrity\s*$", text, re.MULTILINE):
        text = re.sub(
            r"^## Skill integrity\s*$",
            lambda _m: section + "\n## Skill integrity",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        text = text.rstrip() + "\n\n" + section
    if not text.endswith("\n"):
        text += "\n"
    return text


def appendix_markdown(result: TranscriptExportResult) -> str:
    """Markdown appended into the PDF after the main report body."""
    parts = [
        "# Appendix - Session transcripts",
        "",
        "Full Guide chats written by the agent at report build time.",
        "",
    ]
    if not result.markdown_files:
        parts.append("_No transcripts found. Guide must pull chats into docs/transcripts/._")
        parts.append("")
        return "\n".join(parts)
    for path in result.markdown_files:
        parts.append(path.read_text(encoding="utf-8", errors="replace"))
        parts.append("")
        parts.append("---")
        parts.append("")
    return "\n".join(parts)
