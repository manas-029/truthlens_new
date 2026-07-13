document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-count-to]').forEach((el) => {
    const target = parseFloat(el.dataset.countTo);
    const decimals = el.dataset.countTo.includes('.') ? 2 : 0;
    let current = 0;
    const step = target / 60;
    const tick = () => {
      current += step;
      if (current >= target) {
        el.textContent = target.toLocaleString(undefined, { maximumFractionDigits: decimals });
        return;
      }
      el.textContent = current.toLocaleString(undefined, { maximumFractionDigits: decimals });
      requestAnimationFrame(tick);
    };
    tick();
  });
});
