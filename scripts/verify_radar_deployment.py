"""Verify the public radar homepage against the exact HTML uploaded to Pages."""
import argparse
import hashlib
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


def verify(index, site_url, attempts=6, delay=10):
    expected = hashlib.sha256(index.read_bytes()).hexdigest()
    url = f"{site_url.rstrip('/')}/?verify={expected[:20]}"
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"Cache-Control": "no-cache", "Accept-Encoding": "identity"})
            with urlopen(request, timeout=20) as response:
                actual = hashlib.sha256(response.read()).hexdigest()
                if response.status == 200 and actual == expected:
                    print(f"Verified public radar HTML against the deployed artifact ({expected}).")
                    return
                error = f"HTTP {response.status}, received SHA-256 {actual}"
        except (OSError, URLError) as exc:
            error = str(exc)
        print(f"Public verification {attempt}/{attempts}: {error}", flush=True)
        if attempt < attempts:
            time.sleep(delay)
    raise SystemExit(f"Deployment verification failed for {url}; expected SHA-256 {expected}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path, help="index.html from the uploaded build")
    parser.add_argument("site_url", help="public Pages site URL")
    args = parser.parse_args()
    verify(args.index, args.site_url)
