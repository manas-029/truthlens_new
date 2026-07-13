document.addEventListener('DOMContentLoaded', () => {
  const verdictCanvas = document.getElementById('verdictChart');
  const timelineCanvas = document.getElementById('timelineChart');

  if (verdictCanvas && window.Chart) {
    new Chart(verdictCanvas, {
      type: 'doughnut',
      data: {
        labels: ['Fake', 'Real', 'Uncertain'],
        datasets: [{
          data: JSON.parse(verdictCanvas.dataset.values || '[0,0,0]'),
          backgroundColor: ['#ff4d6d', '#2ee6a8', '#ffb648'],
          borderWidth: 0,
        }],
      },
      options: {
        plugins: { legend: { position: 'bottom', labels: { color: '#97a2bd' } } },
      },
    });
  }

  if (timelineCanvas && window.Chart) {
    new Chart(timelineCanvas, {
      type: 'line',
      data: {
        labels: JSON.parse(timelineCanvas.dataset.labels || '[]'),
        datasets: [{
          label: 'Fake-likelihood confidence (%)',
          data: JSON.parse(timelineCanvas.dataset.values || '[]'),
          borderColor: '#00e5ff',
          backgroundColor: 'rgba(0,229,255,0.12)',
          tension: 0.35,
          fill: true,
          pointRadius: 3,
        }],
      },
      options: {
        scales: {
          x: { ticks: { color: '#97a2bd' }, grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { ticks: { color: '#97a2bd' }, grid: { color: 'rgba(255,255,255,0.05)' }, min: 0, max: 100 },
        },
        plugins: { legend: { labels: { color: '#97a2bd' } } },
      },
    });
  }
});
