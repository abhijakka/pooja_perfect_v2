"""Integration check: validate every frontend GraphQL document against the real schema.

Extracts the query/mutation documents the frontend actually sends and asks graphql-core to
validate each one against the assembled Strawberry public/admin schemas. This is the automated
form of "frontend request -> backend endpoint -> schema -> response" contract checking.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from graphql import build_schema, parse, validate

from app.admin.api.graphql.schema import admin_schema
from app.public.api.graphql.schema import public_schema

FRONTEND = Path(__file__).resolve().parents[4] / "frontend"

# `const NAME = `...`` fragments (e.g. CART_FIELDS) that documents interpolate.
FRAGMENT_RE = re.compile(
    r"(?:export\s+)?const\s+([A-Za-z_$][\w$]*)\s*(?::[^=]*?)?=\s*`([^`]*)`",
    re.DOTALL,
)
INTERP_RE = re.compile(r"\$\{([A-Za-z_$][\w$]*)\}")
# A GraphQL operation always begins with one of these keywords followed by a name, argument
# list or selection set - not by a word character, which avoids matching ids like `subscription-`.
OPERATION_RE = re.compile(r"^\s*(query|mutation|subscription)\b\s*[\w({]")


def _template_at(text: str, pos: int) -> str | None:
    """Return the contents of the template literal whose backtick sits at ``pos``."""
    if text[pos : pos + 1] != "`":
        return None
    end = text.find("`", pos + 1)
    return None if end == -1 else text[pos + 1 : end]


def _expand(doc: str, fragments: dict[str, str], depth: int = 0) -> str:
    """Inline `${FRAGMENT}` placeholders using same-file const declarations."""
    if depth > 6 or "${" not in doc:
        return doc

    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in fragments:
            return _expand(fragments[name], fragments, depth + 1)
        # Not a fragment (e.g. a runtime variable) - drop the selection-set placeholder so
        # the document can still be parsed; field-level coverage comes from the fragments.
        return ""

    return INTERP_RE.sub(repl, doc)


def _read_documents(path: Path) -> list[str]:
    """Extract every template literal that is a GraphQL operation, whatever helper sends it.

    Scanning the literals themselves (instead of the call sites) keeps the check working for
    wrappers such as admin.api.ts's local ``request`` helper.
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    fragments = {name: body for name, body in FRAGMENT_RE.findall(text)}
    docs: list[str] = []
    pos = 0
    while True:
        pos = text.find("`", pos)
        if pos == -1:
            break
        body = _template_at(text, pos)
        pos += 1
        if body is None:
            continue
        expanded = _expand(body, fragments)
        if OPERATION_RE.match(expanded):
            docs.append(expanded)
    return docs


def _targets(path: Path, text: str) -> list[str]:
    """Which routers a file can legitimately send documents to."""
    uses_admin = "adminGraphqlClient" in text
    uses_public = re.search(r"\bgraphqlClient\b", text) is not None
    if uses_admin and not uses_public:
        return ["admin"]
    if uses_admin and uses_public:
        return ["public", "admin"]
    return ["public"]


def main() -> int:
    public_schema_doc = build_schema(public_schema.as_str())
    admin_schema_doc = build_schema(admin_schema.as_str())

    files = [
        p
        for p in FRONTEND.rglob("*.ts")
        if not p.name.endswith((".test.ts", ".d.ts")) and "node_modules" not in p.parts
    ] + [p for p in FRONTEND.rglob("*.tsx") if "node_modules" not in p.parts]

    checked = 0
    failures: list[str] = []
    per_file: list[str] = []

    for path in sorted(files):
        rel = path.relative_to(FRONTEND).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        docs = _read_documents(path)
        if not docs:
            continue
        targets = _targets(path, text)
        per_file.append(f"  {rel} [{'/'.join(targets)}] x{len(docs)}")
        for doc in docs:
            checked += 1
            try:
                parsed = parse(doc)
            except Exception as exc:  # noqa: BLE001 - report, do not abort the sweep
                failures.append(f"{rel} PARSE ERROR: {exc}")
                continue
            # A document only breaks the contract if it fails on every router it can reach.
            per_target = {
                label: validate(admin_schema_doc if label == "admin" else public_schema_doc, parsed)
                for label in targets
            }
            if any(not errs for errs in per_target.values()):
                continue
            for label, errs in per_target.items():
                for err in errs:
                    failures.append(f"{rel} [{label}] {err.message}")

    print(f"GraphQL documents validated: {checked}")
    print("\nBreakdown:")
    for line in per_file:
        print(line)
    print()
    if failures:
        print(f"INVALID: {len(failures)}")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("All frontend GraphQL documents are valid against the live schemas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
