import os
import io
import base64
import uuid
import subprocess

import numpy as np
import cv2
from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__)

# ---------- Config ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")

PROTO_FILE = os.path.join(MODEL_DIR, "colorization_deploy_v2.prototxt")
MODEL_FILE = os.path.join(MODEL_DIR, "colorization_release_v2.caffemodel")
HULL_PTS = os.path.join(MODEL_DIR, "pts_in_hull.npy")

# Keep this consistent with the download script's own size check.
# The real caffemodel is ~123 MB; anything drastically smaller means
# the download failed (e.g. an HTML error page got saved instead).
MIN_MODEL_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "bmp"}

# ---------- Load model once at startup ----------
net = None
model_ready = False
model_error = None


def load_model():
    global net, model_ready, model_error
    try:
        # Check if model exists, if not, download it automatically
        needs_download = False
        if not os.path.exists(PROTO_FILE) or not os.path.exists(HULL_PTS) or not os.path.exists(MODEL_FILE):
            needs_download = True
        elif os.path.exists(MODEL_FILE) and os.path.getsize(MODEL_FILE) < MIN_MODEL_SIZE_BYTES:
            needs_download = True
        
        if needs_download:
            print("[colorizer] Model missing or corrupted. Downloading automatically (this may take a minute)...")
            download_script = os.path.join(BASE_DIR, "model", "download_models.py")
            subprocess.run(["python", download_script], check=True)
            print("[colorizer] Download complete.")

        if not os.path.exists(PROTO_FILE):
            raise FileNotFoundError(f"Missing {PROTO_FILE}")
        if not os.path.exists(HULL_PTS):
            raise FileNotFoundError(f"Missing {HULL_PTS}")
        if not os.path.exists(MODEL_FILE):
            raise FileNotFoundError(f"Missing {MODEL_FILE}")

        model_size = os.path.getsize(MODEL_FILE)
        if model_size < MIN_MODEL_SIZE_BYTES:
            raise ValueError(
                f"{MODEL_FILE} is only {model_size} bytes — looks corrupted "
                f"or incompletely downloaded (expected ~123 MB). "
            )

        net = cv2.dnn.readNetFromCaffe(PROTO_FILE, MODEL_FILE)
        pts = np.load(HULL_PTS)

        class8 = net.getLayerId("class8_ab")
        conv8 = net.getLayerId("conv8_313_rh")
        pts = pts.transpose().reshape(2, 313, 1, 1)
        net.getLayer(class8).blobs = [pts.astype("float32")]
        net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]

        model_ready = True
        model_error = None
        print("[colorizer] Model loaded successfully.")
    except Exception as e:
        model_ready = False
        model_error = str(e)
        print(f"[colorizer] Model NOT loaded: {model_error}")


load_model()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def colorize_image(img_bgr):
    """Takes a BGR uint8 image, returns a BGR uint8 colorized image."""
    scaled = img_bgr.astype("float32") / 255.0
    lab_img = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)

    resized = cv2.resize(lab_img, (224, 224))
    L = cv2.split(resized)[0]
    L -= 50

    net.setInput(cv2.dnn.blobFromImage(L))
    ab_channel = net.forward()[0, :, :, :].transpose((1, 2, 0))
    ab_channel = cv2.resize(ab_channel, (img_bgr.shape[1], img_bgr.shape[0]))

    L_full = cv2.split(lab_img)[0]
    colorized = np.concatenate((L_full[:, :, np.newaxis], ab_channel), axis=2)
    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)
    colorized = (255 * colorized).astype("uint8")
    return colorized


def image_to_base64(img_bgr, ext=".png"):
    success, buffer = cv2.imencode(ext, img_bgr)
    if not success:
        raise RuntimeError("Failed to encode output image")
    return base64.b64encode(buffer).decode("utf-8")


# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html", model_ready=model_ready, model_error=model_error)


@app.route("/api/health")
def health():
    return jsonify({"model_ready": model_ready, "model_error": model_error})


@app.route("/api/colorize", methods=["POST"])
def colorize():
    if not model_ready:
        return jsonify({
            "success": False,
            "error": f"Model is not loaded on the server: {model_error}"
        }), 503

    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image file provided (field name must be 'image')."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename."}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXT))}"}), 400

    try:
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img_bgr is None:
            return jsonify({"success": False, "error": "Could not decode image."}), 400

        colorized = colorize_image(img_bgr)

        original_b64 = image_to_base64(img_bgr)
        colorized_b64 = image_to_base64(colorized)

        return jsonify({
            "success": True,
            "original": f"data:image/png;base64,{original_b64}",
            "colorized": f"data:image/png;base64,{colorized_b64}",
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
