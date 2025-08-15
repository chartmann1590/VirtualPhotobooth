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

    // TTS functionality
    function speakWithTTS(text, voice = null) {
        if (!ttsEnabled) return;
        
        const engine = ttsEngine || 'browser';
        const service = ttsService || 'google';
        
        if (engine === 'browser') {
            // Use browser TTS
            if (window.speechSynthesis) {
                const utterance = new SpeechSynthesisUtterance(text);
                if (voice) {
                    const voices = speechSynthesis.getVoices();
                    const selectedVoice = voices.find(v => v.name === voice);
                    if (selectedVoice) utterance.voice = selectedVoice;
                }
                speechSynthesis.cancel();
                speechSynthesis.speak(utterance);
            }
        } else if (engine === 'remote') {
            // Use remote TTS service
            const params = new URLSearchParams({
                text: text,
                service: service,
                voice: voice || getDefaultVoice(service)
            });
            
            const audio = new Audio(`/api/tts/speak?${params.toString()}`);
            audio.play().catch(e => console.error('TTS audio play failed:', e));
        }
    }
    
    function getDefaultVoice(service) {
        switch (service) {
            case 'google': return 'en';
            case 'microsoft': return 'en-US-JennyNeural';
            case 'elevenlabs': return '21m00Tcm4TlvDq8ikWAM';
            default: return 'en';
        }
    }

async function countdown(seconds) {
  if (countdownActive) return;
  countdownActive = true;
  
  // Speak the prompt first
  if (ttsEnabled && ttsPrompt) {
    speakWithTTS(ttsPrompt);
    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for prompt to finish
  }
  
  for (let i = seconds; i > 0; i--) {
    if (!countdownActive) break;
    
    // Update countdown display
    countdownDisplay.textContent = i;
    countdownDisplay.classList.remove('hidden');
    
    // Speak the countdown number
    if (ttsEnabled) {
      speakWithTTS(i.toString());
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  if (countdownActive) {
    countdownDisplay.classList.add('hidden');
    takePhoto();
  }
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
  if ((settings.tts?.engine || 'browser') === 'opentts') {
    await speakViaServer(settings.tts?.prompt || 'Get ready!');
  } else {
    speak(settings.tts?.prompt || 'Get ready!');
  }
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
