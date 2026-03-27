#!/usr/bin/env python3
"""
Download the redMaPPer DR18 cluster catalog from SDSS.
"""

import os
import sys
import hashlib
from pathlib import Path

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
URL = "https://data.sdss.org/sas/dr18/eboss/lss/redmapper_dr18_v1.0.fits"
FILENAME = "redmapper_dr18.fits"          # shorter name for local use
CHECKSUM = None                           # optional SHA1 if known
# The official SHA1 for verification can be added if needed.
# For DR18, the sums are often provided in a .sha1sum file.

# ----------------------------------------------------------------------
# Helper: download with wget if available
# ----------------------------------------------------------------------
def download_with_wget(url, dest):
    import subprocess
    try:
        subprocess.run(["wget", "-O", dest, url], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# ----------------------------------------------------------------------
# Helper: download with urllib + progress bar
# ----------------------------------------------------------------------
def download_with_urllib(url, dest):
    import urllib.request
    from urllib.error import URLError

    class ProgressHook:
        def __init__(self, total=None):
            self.total = total
            self.downloaded = 0
            self.last_reported = 0

        def __call__(self, count, block_size, total_size):
            self.downloaded = min(count * block_size, total_size)
            if self.total is None:
                self.total = total_size
            if self.total > 0:
                percent = self.downloaded * 100 / self.total
                if percent - self.last_reported >= 5 or self.downloaded == self.total:
                    print(f"\rDownloading: {self.downloaded / 1024 / 1024:.1f} MB of {self.total / 1024 / 1024:.1f} MB ({percent:.1f}%)", end='')
                    self.last_reported = percent
        def finish(self):
            print()

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            progress = ProgressHook(total_size)
            with open(dest, 'wb') as f:
                block_size = 8192
                downloaded = 0
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress(downloaded, block_size, total_size)
            progress.finish()
        return True
    except URLError as e:
        print(f"\nError downloading: {e}")
        return False

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    dest = Path(FILENAME)

    if dest.exists():
        print(f"File '{FILENAME}' already exists. Skipping download.")
        return

    print(f"Downloading redMaPPer DR18 cluster catalog to '{FILENAME}'...")
    print(f"Source: {URL}")

    # First try wget (often faster and more robust)
    if download_with_wget(URL, str(dest)):
        print("Download completed (wget).")
    else:
        print("wget not available, falling back to urllib...")
        if download_with_urllib(URL, str(dest)):
            print("Download completed (urllib).")
        else:
            print("Download failed. Please check your internet connection and the URL.")
            sys.exit(1)

    # Optionally verify checksum if known (not implemented here)
    print("File saved as", dest.resolve())

if __name__ == "__main__":
    main()