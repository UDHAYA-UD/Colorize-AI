<div align="center">
  <h1>🎨 ColorizeAI</h1>
  <p><strong>A stunning, deep-learning powered web application that breathes life into vintage black & white photos.</strong></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
    <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV">
    <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5">
    <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3">
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
  </p>
</div>

---

## ✨ Features
- 🚀 **Deep Learning Colorization:** Uses the state-of-the-art Caffe colorization model (Zhang et al.) via OpenCV's `dnn` module.
- 💅 **Dark Neumorphic UI:** A beautifully crafted, modern user interface featuring 3D soft shadows, animated colorful gradients, and interactive components.
- 🔍 **Interactive Image Slider:** Drag the slider to compare the original black-and-white image directly against the colorized result!
- 🖱️ **Custom Cursor Engine:** Engaging custom interactive cursor that responds to hovers and clicks.
- ⚡ **No File Storage:** All image processing is handled in memory via Base64, ensuring user privacy and blazing-fast response times.

## 🛠️ Quick Start

### 1. Install Dependencies
```bash
git clone https://github.com/UDHAYA-UD/Colorize-AI.git
cd Colorize-AI
pip install -r requirements.txt
```

### 2. Download the Models
Run the setup script to automatically fetch the required Caffe deep learning model weights (~123 MB). *This script requires an active internet connection.*
```bash
python model/download_models.py
```

### 3. Start the Application
Launch the Flask backend server.
```bash
python app.py
```
Open **http://localhost:5000** in your browser. Drag and drop a black-and-white photo, hit "Colorize," and watch the magic happen!

---

## 📂 Project Structure
```text
Colorize-AI/
├── app.py                      # Core Flask backend & API routing
├── requirements.txt            # Python package dependencies
├── templates/
│   └── index.html              # Frontend HTML structure
├── static/
│   ├── style.css               # Neumorphic styling & animations
│   └── script.js               # Slider, cursor, and API logic
└── model/
    ├── download_models.py      # Automated model fetcher script
    ├── colorization_deploy_v2.prototxt
    ├── pts_in_hull.npy
    └── colorization_release_v2.caffemodel  (Generated)
```

---

## 🚀 Deployment

**Render.com (Recommended Free Tier)**:
1. Create a **New Web Service** and connect this repository.
2. Set Build Command: `pip install -r requirements.txt && python model/download_models.py`
3. Set Start Command: `gunicorn app:app --timeout 120`

*Note: Free-tier Render instances spin down when idle. The first request after idling will take a little longer while it wakes up.*

**Hugging Face Spaces**:
1. Create a new Space using the **Docker** SDK.
2. Ensure you push the standard `Dockerfile` that installs requirements and runs `download_models.py`.

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/UDHAYA-UD/Colorize-AI/issues).
