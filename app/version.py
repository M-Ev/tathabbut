"""The deployed version, for /api/health and every /api/check reply."""
from pathlib import Path


def _git_commit() -> str | None:
    """The deployed commit, read from .git without the git program (the Space clones the repo)."""
    g = Path(__file__).resolve().parent.parent / ".git"
    try:
        head = (g / "HEAD").read_text().strip()
        if head.startswith("ref: "):
            ref = head[5:]
            f = g / ref
            if f.exists():
                return f.read_text().strip()[:7]
            for line in (g / "packed-refs").read_text().splitlines():
                if line.endswith(" " + ref):
                    return line[:7]
            return None
        return head[:7]
    except OSError:
        return None


VERSION = {"commit": _git_commit()}
