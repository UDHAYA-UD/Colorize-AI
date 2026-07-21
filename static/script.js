const dropzone = document.getElementById("dropzone");
const dropzoneContent = document.getElementById("dropzoneContent");
const fileInput = document.getElementById("fileInput");
const colorizeBtn = document.getElementById("colorizeBtn");
const resetBtn = document.getElementById("resetBtn");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const originalImg = document.getElementById("originalImg");
const colorizedImg = document.getElementById("colorizedImg");
const downloadLink = document.getElementById("downloadLink");
const scanner = document.getElementById("scanner");
const compareContainer = document.getElementById("compareContainer");
const compareHandle = document.getElementById("compareHandle");

let selectedFile = null;

function setStatus(msg, isError = false) {
  statusEl.textContent = msg;
  statusEl.className = "status" + (isError ? " error" : "");
}

function showPreview(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    dropzoneContent.innerHTML = `<img class="preview" src="${e.target.result}" alt="Selected image">`;
  };
  reader.readAsDataURL(file);
}

function handleFile(file) {
  if (!file) return;
  if (!file.type.startsWith("image/")) {
    setStatus("Please choose an image file.", true);
    return;
  }
  selectedFile = file;
  colorizeBtn.disabled = false;
  setStatus("");
  showPreview(file);
}

dropzone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", (e) => {
  handleFile(e.target.files[0]);
});

["dragenter", "dragover"].forEach((evt) => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach((evt) => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  });
});

dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  handleFile(file);
});

colorizeBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  colorizeBtn.disabled = true;
  setStatus("Colorizing… this can take a few seconds.");
  resultsEl.hidden = true;
  scanner.hidden = false;

  const formData = new FormData();
  formData.append("image", selectedFile);

  try {
    const res = await fetch("/api/colorize", {
      method: "POST",
      body: formData,
    });
    
    const contentType = res.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error("Server crashed or ran out of memory. Try uploading a smaller image.");
    }

    const data = await res.json();

    if (!res.ok || !data.success) {
      throw new Error(data.error || "Something went wrong.");
    }

    originalImg.src = data.original;
    colorizedImg.src = data.colorized;
    downloadLink.href = data.colorized;
    downloadLink.hidden = false;

    // Reset slider to middle
    colorizedImg.style.clipPath = `polygon(0 0, 50% 0, 50% 100%, 0 100%)`;
    compareHandle.style.left = `50%`;

    resultsEl.hidden = false;
    scanner.hidden = true;
    setStatus("Done.");
    resetBtn.hidden = false;
  } catch (err) {
    scanner.hidden = true;
    setStatus(err.message, true);
    colorizeBtn.disabled = false;
  }
});

resetBtn.addEventListener("click", () => {
  selectedFile = null;
  fileInput.value = "";
  colorizeBtn.disabled = true;
  resetBtn.hidden = true;
  resultsEl.hidden = true;
  scanner.hidden = true;
  setStatus("");
  dropzoneContent.innerHTML = `
    <div class="dz-icon">📷</div>
    <p><strong>Click to upload</strong> or drag & drop</p>
    <p class="dz-hint">PNG, JPG, WEBP, BMP</p>
  `;
});

// Slider logic
let isDragging = false;

const updateSlider = (e) => {
  if (!isDragging) return;
  const rect = compareContainer.getBoundingClientRect();
  let x = e.clientX;
  if (x === undefined && e.touches) {
    x = e.touches[0].clientX;
  }
  if (x === undefined) return;
  
  x = x - rect.left;
  let percentage = (x / rect.width) * 100;
  if (percentage < 0) percentage = 0;
  if (percentage > 100) percentage = 100;

  colorizedImg.style.clipPath = `polygon(0 0, ${percentage}% 0, ${percentage}% 100%, 0 100%)`;
  compareHandle.style.left = `${percentage}%`;
};

compareContainer.addEventListener('mousedown', () => isDragging = true);
compareContainer.addEventListener('touchstart', () => isDragging = true, {passive: true});
window.addEventListener('mouseup', () => isDragging = false);
window.addEventListener('touchend', () => isDragging = false);
window.addEventListener('mousemove', updateSlider);
window.addEventListener('touchmove', updateSlider, {passive: true});

// Custom Cursor Logic
const cursor = document.getElementById('cursor');
const cursorFollower = document.getElementById('cursor-follower');

document.addEventListener('mousemove', (e) => {
  cursor.style.left = e.clientX + 'px';
  cursor.style.top = e.clientY + 'px';
  
  cursorFollower.style.left = e.clientX + 'px';
  cursorFollower.style.top = e.clientY + 'px';
});

// Add hover effects for the custom cursor
const interactables = document.querySelectorAll('button, .dropzone, a, .image-compare-container');
interactables.forEach(el => {
  el.addEventListener('mouseenter', () => {
    cursor.classList.add('hover');
    cursorFollower.classList.add('hover');
  });
  el.addEventListener('mouseleave', () => {
    cursor.classList.remove('hover');
    cursorFollower.classList.remove('hover');
  });
});
