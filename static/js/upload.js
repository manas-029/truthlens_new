document.addEventListener('DOMContentLoaded', () => {
  const dropZone = document.getElementById('upload-drop');
  const fileInput = document.getElementById('file-input');
  const form = document.getElementById('scan-form');
  const fileNameLabel = document.getElementById('file-name-label');
  const tabs = document.querySelectorAll('.modality-tab');
  const mediaTypeInput = document.getElementById('media_type_input');
  const progress = document.getElementById('upload-progress');
  const maxBytes = 200 * 1024 * 1024;

  const allowed = {
    video: ['mp4', 'mov', 'avi', 'mkv', 'webm'],
    image: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    audio: ['mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac'],
  };

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      tabs.forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');
      mediaTypeInput.value = tab.dataset.mediaType;
      fileInput.accept = tab.dataset.accept || '*';
      fileInput.value = '';
      if (fileNameLabel) fileNameLabel.textContent = '';
    });
  });

  if (!dropZone) return;

  ['dragenter', 'dragover'].forEach((evt) =>
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    })
  );
  ['dragleave', 'drop'].forEach((evt) =>
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
    })
  );
  dropZone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length) {
      fileInput.files = files;
      updateLabel(files[0]);
    }
  });
  dropZone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) updateLabel(fileInput.files[0]);
  });

  function validate(file) {
    const mediaType = mediaTypeInput.value;
    const ext = file.name.split('.').pop().toLowerCase();
    if (!allowed[mediaType].includes(ext)) return `Choose a supported ${mediaType} file.`;
    if (file.size > maxBytes) return 'File is larger than the 200 MB limit.';
    return '';
  }

  function updateLabel(file) {
    const error = validate(file);
    if (fileNameLabel) {
      fileNameLabel.textContent = error || `Selected: ${file.name}`;
      fileNameLabel.style.color = error ? 'var(--fake)' : 'var(--accent)';
    }
  }

  if (form) {
    form.addEventListener('submit', (event) => {
      const file = fileInput.files[0];
      const error = file ? validate(file) : 'Choose a file first.';
      if (error) {
        event.preventDefault();
        if (fileNameLabel) {
          fileNameLabel.textContent = error;
          fileNameLabel.style.color = 'var(--fake)';
        }
        return;
      }
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Uploading...';
      }
      if (progress) {
        progress.style.display = 'block';
        progress.removeAttribute('value');
      }
    });
  }
});
