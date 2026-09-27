"""Keep custom CSS and JavaScript in sync with the HTML across deployments."""

from hashlib import sha256
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def versioned_url(url: str, docs_dir: str) -> str:
    parts = urlsplit(url)
    if parts.scheme or parts.netloc:
        return url
    # Normalize checkout line endings so Windows and Linux produce the same URL.
    content = (Path(docs_dir) / parts.path).read_bytes().replace(b"\r\n", b"\n")
    version = sha256(content).hexdigest()[:16]
    query = [(key, value) for key, value in parse_qsl(parts.query) if key != "v"]
    query.append(("v", version))
    return urlunsplit(parts._replace(query=urlencode(query)))


def on_pre_build(config, **kwargs):
    """Recompute on every build, including rebuilds by mkdocs serve."""
    config.extra_css = [versioned_url(url, config.docs_dir) for url in config.extra_css]
    scripts = []
    for script in config.extra_javascript:
        if isinstance(script, str):
            scripts.append(versioned_url(script, config.docs_dir))
        else:
            # Preserve module/defer/async options supported by MkDocs.
            script.path = versioned_url(script.path, config.docs_dir)
            scripts.append(script)
    config.extra_javascript = scripts
