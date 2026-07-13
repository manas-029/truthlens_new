document.addEventListener('DOMContentLoaded', () => {
  const video = document.getElementById('live-video');
  const startBtn = document.getElementById('live-start-btn');
  const statusBadge = document.getElementById('live-status');
  const scoreEl = document.getElementById('live-score');
  if (!video || !startBtn) return;

  let stream = null;
  let interval = null;

  startBtn.addEventListener('click', async () => {
    if (stream) {
      stopLive();
      return;
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      startBtn.textContent = 'Stop Live Check';
      statusBadge.textContent = 'Monitoring…';
      statusBadge.className = 'badge badge-uncertain';

      interval = setInterval(() => {
        // Client-side sampling hook: in production this captures a frame via
        // canvas.drawImage(video,...) and POSTs it to a lightweight scoring
        // endpoint. Here we simulate the live score so the UX is fully demoable.
        const fakeLikelihood = Math.round(Math.random() * 40 + 5);
        scoreEl.textContent = fakeLikelihood + '%';
        if (fakeLikelihood > 30) {
          statusBadge.textContent = 'Possible anomaly';
          statusBadge.className = 'badge badge-uncertain';
        } else {
          statusBadge.textContent = 'Looks authentic';
          statusBadge.className = 'badge badge-real';
        }
      }, 2000);
    } catch (err) {
      truthlensToast('Camera access denied or unavailable.');
    }
  });

  function stopLive() {
    if (stream) stream.getTracks().forEach((t) => t.stop());
    stream = null;
    clearInterval(interval);
    startBtn.textContent = 'Start Live Check';
    statusBadge.textContent = 'Idle';
    statusBadge.className = 'badge badge-uncertain';
    scoreEl.textContent = '--';
  }
});
