const dropZone = document.querySelector("#drop-zone");
const fileInput = document.querySelector("#xray-input");
const uploadEmpty = document.querySelector("#upload-empty");
const uploadPreview = document.querySelector("#upload-preview");
const previewImage = document.querySelector("#preview-image");
const fileName = document.querySelector("#file-name");
const fileSize = document.querySelector("#file-size");
const fileType = document.querySelector("#file-type");
const removeImage = document.querySelector("#remove-image");
const analyzeButton = document.querySelector("#analyze-button");
const sampleButton = document.querySelector("#sample-button");
const statusSampleButton = document.querySelector("#status-sample-button");
const statusCard = document.querySelector("#status-card");
const statusTitle = document.querySelector("#status-title");
const statusMessage = document.querySelector("#status-message");
const resultCard = document.querySelector("#result-card");
const resultImage = document.querySelector("#result-image");
const angleValue = document.querySelector("#angle-value");
const angleExplanation = document.querySelector("#angle-explanation");
const upperVertebra = document.querySelector("#upper-vertebra");
const lowerVertebra = document.querySelector("#lower-vertebra");
const annotatedLink = document.querySelector("#annotated-link");
const startOver = document.querySelector("#start-over");

const defaultCapabilities = {
  real_xray_upload_enabled: false,
  accepted_image_types: ["image/png", "image/jpeg"],
  max_upload_size_mb: 10,
  message:
    "Automated landmark detection is not connected yet. Your image has not been uploaded.",
};

let capabilities = defaultCapabilities;
let selectedFile = null;
let previewUrl = null;

function formatBytes(bytes) {
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function showStatus(title, message) {
  statusTitle.textContent = title;
  statusMessage.textContent = message;
  statusCard.hidden = false;
  resultCard.hidden = true;
  statusCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function clearPreview() {
  selectedFile = null;
  fileInput.value = "";
  if (previewUrl) {
    URL.revokeObjectURL(previewUrl);
    previewUrl = null;
  }
  previewImage.removeAttribute("src");
  uploadPreview.hidden = true;
  uploadEmpty.hidden = false;
}

function validateFile(file) {
  if (!capabilities.accepted_image_types.includes(file.type)) {
    return "Please choose a PNG or JPEG image. DICOM support is planned for a later version.";
  }

  const maximumBytes = capabilities.max_upload_size_mb * 1024 * 1024;
  if (file.size > maximumBytes) {
    return `Please choose an image smaller than ${capabilities.max_upload_size_mb} MB.`;
  }

  return null;
}

function showPreview(file) {
  const error = validateFile(file);
  if (error) {
    showStatus("That file cannot be previewed", error);
    clearPreview();
    return;
  }

  clearPreview();
  selectedFile = file;
  previewUrl = URL.createObjectURL(file);
  previewImage.src = previewUrl;
  fileName.textContent = file.name;
  fileSize.textContent = `${formatBytes(file.size)} · Preview stays on this device`;
  fileType.textContent = file.type === "image/png" ? "PNG" : "JPG";
  uploadEmpty.hidden = true;
  uploadPreview.hidden = false;
  statusCard.hidden = true;
  resultCard.hidden = true;
}

async function loadCapabilities() {
  try {
    const response = await fetch("/api/v1/capabilities", {
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      throw new Error("Capability request failed");
    }
    capabilities = await response.json();
  } catch (_error) {
    capabilities = defaultCapabilities;
  }
}

async function runSample() {
  sampleButton.disabled = true;
  statusSampleButton.disabled = true;
  sampleButton.querySelector("strong").textContent = "Analyzing the sample…";
  statusCard.hidden = true;

  try {
    const response = await fetch("/api/v1/demo/synthetic", {
      method: "POST",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      throw new Error("The sample analysis could not be completed.");
    }

    const result = await response.json();
    const measurement = result.measurement;
    const angle = Number(measurement.cobb_angle_degrees);

    angleValue.textContent = `${angle.toFixed(1)}°`;
    upperVertebra.textContent = measurement.upper_endplate.vertebra_label;
    lowerVertebra.textContent = measurement.lower_endplate.vertebra_label;
    angleExplanation.textContent =
      `For this synthetic example, the selected ${measurement.upper_endplate.vertebra_label} ` +
      `and ${measurement.lower_endplate.vertebra_label} endplates differ by ${angle.toFixed(1)}°. ` +
      "The highlighted lines make the calculation visible and auditable.";
    resultImage.src = result.artifacts.annotated_image_url;
    annotatedLink.href = result.artifacts.annotated_image_url;
    resultCard.hidden = false;
    resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showStatus(
      "The sample is temporarily unavailable",
      error instanceof Error ? error.message : "Please try again in a moment.",
    );
  } finally {
    sampleButton.disabled = false;
    statusSampleButton.disabled = false;
    sampleButton.querySelector("strong").textContent = "Try the safe sample X-ray";
  }
}

dropZone.addEventListener("click", (event) => {
  if (
    event.target !== fileInput &&
    event.target !== removeImage &&
    !removeImage.contains(event.target)
  ) {
    fileInput.click();
  }
});

dropZone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    fileInput.click();
  }
});

fileInput.addEventListener("change", () => {
  const [file] = fileInput.files;
  if (file) {
    showPreview(file);
  }
});

for (const eventName of ["dragenter", "dragover"]) {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("is-dragging");
  });
}

for (const eventName of ["dragleave", "drop"]) {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("is-dragging");
  });
}

dropZone.addEventListener("drop", (event) => {
  const [file] = event.dataTransfer.files;
  if (file) {
    showPreview(file);
  }
});

removeImage.addEventListener("click", (event) => {
  event.stopPropagation();
  clearPreview();
  statusCard.hidden = true;
});

analyzeButton.addEventListener("click", () => {
  if (!selectedFile) {
    showStatus(
      "Choose an X-ray first",
      "Add a PNG or JPEG above, or try the safe sample to see the current workflow.",
    );
    return;
  }

  if (!capabilities.real_xray_upload_enabled) {
    showStatus(
      "The landmark AI is the next milestone",
      `${capabilities.message} We will not invent a Cobb angle or send your image to the server.`,
    );
  }
});

sampleButton.addEventListener("click", runSample);
statusSampleButton.addEventListener("click", runSample);

startOver.addEventListener("click", () => {
  resultCard.hidden = true;
  statusCard.hidden = true;
  clearPreview();
  document.querySelector("#analyzer").scrollIntoView({ behavior: "smooth" });
});

window.addEventListener("beforeunload", () => {
  if (previewUrl) {
    URL.revokeObjectURL(previewUrl);
  }
});

loadCapabilities();
