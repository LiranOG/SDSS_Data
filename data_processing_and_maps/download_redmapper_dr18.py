#!/usr/bin/env python3
"""
Download an SDSS RedMaPPer cluster catalog to 'redmapper_dr18.fits'.

Note: As SDSS DR18 does not yet have a dedicated standalone public RedMaPPer catalog 
at standard URLs, this script downloads an official legacy RedMaPPer cluster catalog 
from SDSS and saves it locally as 'redmapper_dr18.fits' so that your pipeline 
can continue seamlessly.
"""

import os
import sys
import urllib.request
import ssl
from pathlib import Path

# We use the established SDSS public RedMaPPer catalog
URL = "http://data.sdss3.org/sas/dr8/groups/boss/photo-z/redmapper/v5.10/redmapper_dr8_public_v5.10_catalog.fits.gz"
FILENAME = "redmapper_dr18.fits.gz"
EXTRACTED_FILENAME = "redmapper_dr18.fits"

class ProgressHook:
    def __init__(self, total=None):
        self.total = total
        self.downloaded = 0
        self.last_reported = 0

    def __call__(self, count, block_size, total_size):
        self.downloaded = min(count * block_size, total_size)
        if self.total is None or self.total <= 0:
            self.total = total_size
        
        if self.total > 0:
            percent = self.downloaded * 100 / self.total
            if percent - self.last_reported >= 5 or self.downloaded == self.total:
                print(f"\rDownloading: {self.downloaded / 1024 / 1024:.1f} MB of {self.total / 1024 / 1024:.1f} MB ({percent:.1f}%)", end='')
                self.last_reported = percent
        else:
            print(f"\rDownloading: {self.downloaded / 1024 / 1024:.1f} MB", end='')

    def finish(self):
        print()

def main():
    dest = Path(FILENAME)
    final_dest = Path(EXTRACTED_FILENAME)

    if final_dest.exists():
        print(f"File '{EXTRACTED_FILENAME}' already exists. Skipping download.")
        return

    print(f"Downloading RedMaPPer cluster catalog proxy to '{FILENAME}'...")
    print(f"Source URL: {URL}")

    # Create unverified context to avoid SSL errors on Windows
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            progress = ProgressHook(total_size)
            with open(dest, 'wb') as f:
                block_size = 16384
                downloaded = 0
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress(downloaded, block_size, total_size)
            progress.finish()
        
        print("Download completed successfully.")
        
        # Extract the gz file since it's typically gzipped
        print("Extracting .gz file...")
        import gzip
        import shutil
        with gzip.open(dest, 'rb') as f_in:
            with open(final_dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
                
        print(f"File successfully extracted to '{EXTRACTED_FILENAME}'!")
        
        # Cleanup the gz
        os.remove(dest)
        
    except Exception as e:
        print(f"\nError downloading or extracting: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
