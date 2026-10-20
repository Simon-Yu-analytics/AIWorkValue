"""Package original source and aggregate deliverables, excluding participant data."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT.parent / "AIWorkValue_Project.zip"
TOP_FILES = {"README.md", "requirements.txt", "Makefile", ".gitignore",
             "LICENSE", "THIRD_PARTY_NOTICES.md"}
DIRECTORIES = {".github", ".streamlit", "dashboard", "src", "scripts", "tests", "docs", "sql", "notebooks", "reports", "figures"}
BLOCKED = {"__pycache__", ".cache", ".venv", ".git"}


def main():
    files = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if not path.is_file() or any(part in BLOCKED for part in relative.parts):
            continue
        if path.suffix in {".pyc", ".zip"} or path.name in {".DS_Store", "secrets.toml", ".env"}:
            continue
        if (relative.as_posix() in {"data/source-manifest.json", "data/README.md"}
                or relative.parts[:2] == ("data", "scenarios")
                or relative.parts[0] in DIRECTORIES
                or (len(relative.parts) == 1 and path.name in TOP_FILES)):
            files.append((path, relative))
    assert all("raw" not in relative.parts and "processed" not in relative.parts
               for _, relative in files)
    manifest = {
        "description": "Original code and aggregate deliverables; source and participant-level data excluded.",
        "files": [{"path": relative.as_posix(), "bytes": path.stat().st_size,
                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                  for path, relative in files],
    }
    with zipfile.ZipFile(DESTINATION, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, relative in files:
            archive.write(path, (Path(ROOT.name) / relative).as_posix())
        archive.writestr(f"{ROOT.name}/PACKAGE_MANIFEST.json",
                         json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Packaged {len(files)} files + checksum manifest: {DESTINATION}")


if __name__ == "__main__":
    main()
