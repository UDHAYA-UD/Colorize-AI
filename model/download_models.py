"""
Downloads the 3 files needed for the colorization model:
  1. colorization_deploy_v2.prototxt   (~10 KB)
  2. pts_in_hull.npy                   (~5 KB)
  3. colorization_release_v2.caffemodel (~123 MB)

Run this once, locally, before starting the Flask app:
    python model/download_models.py
"""

import os
import sys
import urllib.request

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

# Keep this consistent with the size check in app.py's load_model().
MIN_MODEL_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB

FILES = {
    "colorization_deploy_v2.prototxt": (
        "https://raw.githubusercontent.com/richzhang/colorization/caffe/"
        "colorization/models/colorization_deploy_v2.prototxt"
    ),
    "pts_in_hull.npy": (
        "https://raw.githubusercontent.com/richzhang/colorization/caffe/"
        "colorization/resources/pts_in_hull.npy"
    ),
    "colorization_release_v2.caffemodel": (
        "https://storage.openvinotoolkit.org/repositories/datumaro/models/"
        "colorization/colorization_release_v2.caffemodel"
    ),
}


def download(url, dest_path):
    print(f"Downloading:\n  {url}\n  -> {dest_path}")

    def _progress(block_num, block_size, total_size):
        if total_size <= 0:
            return
        downloaded = block_num * block_size
        pct = min(100, downloaded * 100 // total_size)
        sys.stdout.write(f"\r  {pct}% ({downloaded // (1024*1024)} MB / {total_size // (1024*1024)} MB)")
        sys.stdout.flush()

    urllib.request.urlretrieve(url, dest_path, _progress)
    print()


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)

    for filename, url in FILES.items():
        dest_path = os.path.join(MODEL_DIR, filename)

        if os.path.exists(dest_path):
            existing_size = os.path.getsize(dest_path)
            if filename.endswith(".caffemodel") and existing_size < MIN_MODEL_SIZE_BYTES:
                print(f"{filename} exists but is only {existing_size} bytes — re-downloading.")
            else:
                print(f"{filename} already exists ({existing_size} bytes) — skipping.")
                continue

        try:
            download(url, dest_path)
        except Exception as e:
            print(f"\n[ERROR] Failed to download {filename}: {e}")
            print("If this keeps failing (the Berkeley server can be slow/unstable),")
            print("search 'colorization_release_v2.caffemodel download mirror' and")
            print(f"place the file manually at:\n  {dest_path}")
            continue

    # Final validation
    caffemodel_path = os.path.join(MODEL_DIR, "colorization_release_v2.caffemodel")
    if os.path.exists(caffemodel_path):
        size = os.path.getsize(caffemodel_path)
        if size < MIN_MODEL_SIZE_BYTES:
            print(f"\n[WARNING] caffemodel is only {size} bytes (expected ~123 MB).")
            print("The download likely failed partway or got redirected to an error page.")
        else:
            print(f"\ncaffemodel OK: {size // (1024*1024)} MB")

    print("\nDone. If all 3 files are present and the caffemodel is ~123 MB, you're ready to run app.py")


if __name__ == "__main__":
    main()
