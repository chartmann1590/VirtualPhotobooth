const video = document.getElementById('camera');
const overlay = document.getElementById('overlay');
const previewCanvas = document.getElementById('previewCanvas');
const frameSelect = document.getElementById('frameSelect');
const startBtn = document.getElementById('startBtn');
const countdownEl = document.getElementById('countdown');
const sharePanel = document.getElementById('sharePanel');
const emailBtn = document.getElementById('emailBtn');
const smsBtn = document.getElementById('smsBtn');

const settings = window.APP_SETTINGS || { tts: { enabled: true, prompt: 'Get ready!', voice: 'default' } };

let currentFrameImg = null;

async function initCamera() {
  const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
  video.srcObject = stream;
  await video.play();
  resizeCanvases();
}

function resizeCanvases() {
  const rect = video.getBoundingClientRect();
  overlay.width = video.videoWidth;
  overlay.height = video.videoHeight;
  previewCanvas.width = video.videoWidth;
  previewCanvas.height = video.videoHeight;
}

window.addEventListener('resize', resizeCanvases);
video.addEventListener('loadedmetadata', resizeCanvases);

frameSelect.addEventListener('change', async () => {
  const frame = frameSelect.value;
  currentFrameImg = null;
  if (!frame) { drawOverlayMask(null); return; }
  const img = new Image();
  img.onload = () => { currentFrameImg = img; drawOverlayMask(img); };
  img.src = `/static/frames/${frame}`;
});

function drawOverlayMask(frameImg) {
  const ctx = overlay.getContext('2d');
  ctx.clearRect(0, 0, overlay.width, overlay.height);
  if (!frameImg) return;
  // Draw frame on overlay for user guidance
  ctx.drawImage(frameImg, 0, 0, overlay.width, overlay.height);
}

function speak(text) {
  if (!settings.tts || !settings.tts.enabled) return;
  const utter = new SpeechSynthesisUtterance(text);
  if (settings.tts.voice && settings.tts.voice !== 'default') {
    const v = speechSynthesis.getVoices().find(v => v.name === settings.tts.voice);
    if (v) utter.voice = v;
  }
  speechSynthesis.cancel();
  speechSynthesis.speak(utter);
}

async function countdown(seconds) {
  for (let i = seconds; i >= 1; i--) {
    countdownEl.textContent = i;
    countdownEl.hidden = false;
    speak(String(i));
    await new Promise(r => setTimeout(r, 1000));
  }
  countdownEl.hidden = true;
}

async function capture() {
  // Prepare offscreen canvas
  const off = document.createElement('canvas');
  off.width = video.videoWidth;
  off.height = video.videoHeight;
  const ctx = off.getContext('2d');
  ctx.drawImage(video, 0, 0, off.width, off.height);
  if (currentFrameImg) {
    ctx.drawImage(currentFrameImg, 0, 0, off.width, off.height);
  }
  const dataUrl = off.toDataURL('image/png');
  // Show preview
  const pctx = previewCanvas.getContext('2d');
  const img = new Image();
  await new Promise(resolve => { img.onload = resolve; img.src = dataUrl; });
  pctx.clearRect(0, 0, previewCanvas.width, previewCanvas.height);
  pctx.drawImage(img, 0, 0, previewCanvas.width, previewCanvas.height);
  return dataUrl;
}

startBtn.addEventListener('click', async () => {
  speak(settings.tts?.prompt || 'Get ready!');
  await countdown(3);
  const imgData = await capture();
  const frame = frameSelect.value || '';
  const res = await fetch('/api/upload_photo', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imgData, frame })
  });
  const data = await res.json();
  if (!res.ok) { alert(data.error || 'Failed to upload'); return; }
  sharePanel.hidden = false;
  sharePanel.dataset.filename = data.filename;
});

emailBtn.addEventListener('click', async () => {
  const email = document.getElementById('emailInput').value;
  const filename = sharePanel.dataset.filename;
  const res = await fetch('/api/share/email', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, email })
  });
  alert(res.ok ? 'Email sent' : 'Failed to send email');
});

smsBtn.addEventListener('click', async () => {
  const phone = document.getElementById('phoneInput').value;
  const filename = sharePanel.dataset.filename;
  const res = await fetch('/api/share/sms', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename, phone })
  });
  alert(res.ok ? 'SMS sent' : 'Failed to send SMS');
});

(async function main() {
  await initCamera();
  // Load default frame if available
  if (frameSelect.options.length > 1) {
    frameSelect.selectedIndex = 1;
    frameSelect.dispatchEvent(new Event('change'));
  }
})();
