const fileInput = document.querySelector('#fileInput');
const dropzone = document.querySelector('#dropzone');
const preview = document.querySelector('#preview');
const sourcePreview = document.querySelector('#sourcePreview');
const resultPreview = document.querySelector('#resultPreview');
const fileName = document.querySelector('#fileName');
const removeButton = document.querySelector('#removeButton');
const downloadButton = document.querySelector('#downloadButton');
const resetButton = document.querySelector('#resetButton');
const status = document.querySelector('#status');

let selectedFile = null;
let sourceUrl = null;
let resultUrl = null;

function reset() {
  if (sourceUrl) URL.revokeObjectURL(sourceUrl);
  if (resultUrl) URL.revokeObjectURL(resultUrl);
  selectedFile = null; sourceUrl = null; resultUrl = null;
  fileInput.value = '';
  preview.hidden = true;
  dropzone.hidden = false;
  resultPreview.hidden = true;
  downloadButton.hidden = true;
  removeButton.hidden = false;
  status.textContent = '';
}

function selectFile(file) {
  if (!file || !['image/jpeg','image/png','image/webp'].includes(file.type)) {
    status.textContent = 'Choose a JPG, PNG or WebP image.';
    return;
  }
  if (file.size > 22 * 1024 * 1024) {
    status.textContent = 'That image is larger than 22 MB.';
    return;
  }
  if (sourceUrl) URL.revokeObjectURL(sourceUrl);
  if (resultUrl) URL.revokeObjectURL(resultUrl);
  selectedFile = file;
  sourceUrl = URL.createObjectURL(file);
  sourcePreview.src = sourceUrl;
  fileName.textContent = file.name;
  preview.hidden = false;
  dropzone.hidden = true;
  resultPreview.hidden = true;
  downloadButton.hidden = true;
  removeButton.hidden = false;
  status.textContent = 'Ready.';
}

fileInput.addEventListener('change', () => selectFile(fileInput.files[0]));
resetButton.addEventListener('click', reset);

['dragenter','dragover'].forEach(type => dropzone.addEventListener(type, event => {
  event.preventDefault(); dropzone.classList.add('dragging');
}));
['dragleave','drop'].forEach(type => dropzone.addEventListener(type, event => {
  event.preventDefault(); dropzone.classList.remove('dragging');
}));
dropzone.addEventListener('drop', event => selectFile(event.dataTransfer.files[0]));

removeButton.addEventListener('click', async () => {
  if (!selectedFile) return;
  removeButton.disabled = true;
  status.textContent = 'Removing background…';
  try {
    const form = new FormData();
    form.append('file', selectedFile);
    const response = await fetch('/remove', { method:'POST', body:form });
    if (!response.ok) {
      let message = 'Background removal failed.';
      try { message = (await response.json()).error || message; } catch {}
      throw new Error(message);
    }
    const blob = await response.blob();
    if (resultUrl) URL.revokeObjectURL(resultUrl);
    resultUrl = URL.createObjectURL(blob);
    resultPreview.src = resultUrl;
    resultPreview.hidden = false;
    sourcePreview.hidden = true;
    removeButton.hidden = true;
    downloadButton.href = resultUrl;
    downloadButton.download = `${selectedFile.name.replace(/\.[^.]+$/, '')}-no-background.png`;
    downloadButton.hidden = false;
    status.textContent = 'Background removed.';
  } catch (error) {
    status.textContent = error.message || 'Background removal failed.';
  } finally {
    removeButton.disabled = false;
  }
});
