/* Scholars HUB — main.js */

// The Flask backend (app.py) can run on a different origin than this
// static frontend (e.g. this frontend on GitHub Pages, backend on
// Render/Railway/PythonAnywhere). Change this one line to point the
// contact + booking forms at wherever the Flask API is deployed.
// For local testing, run: cd backend && python3 app.py  (defaults to
// http://127.0.0.1:5000) and leave this as-is.
const API_BASE_URL = window.SCHOLARS_HUB_API_BASE || 'http://127.0.0.1:5000';

document.addEventListener('DOMContentLoaded', () => {

  // Footer year
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Animate on scroll
  if (window.AOS) {
    AOS.init({ duration: 700, once: true, offset: 60, easing: 'ease-out-cubic' });
  }

  // Sticky header shrink shadow
  const header = document.getElementById('siteHeader');
  window.addEventListener('scroll', () => {
    if (!header) return;
    header.classList.toggle('is-scrolled', window.scrollY > 12);
  });

  // Mobile nav toggle
  const navToggle = document.getElementById('navToggle');
  const mainNav = document.getElementById('mainNav');
  if (navToggle && mainNav) {
    navToggle.addEventListener('click', () => {
      const isOpen = mainNav.classList.toggle('is-open');
      navToggle.classList.toggle('is-open', isOpen);
      navToggle.setAttribute('aria-expanded', String(isOpen));
    });
    mainNav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mainNav.classList.remove('is-open');
        navToggle.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Generic form submit handler -> posts JSON to a Flask API endpoint
  const handleFormSubmit = (formId, endpoint) => {
    const form = document.getElementById(formId);
    if (!form) return;
    const statusBox = form.querySelector('.form-status');
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());

      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Sending...'; }
      if (statusBox) { statusBox.className = 'form-status'; statusBox.textContent = ''; }

      try {
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        const result = await res.json();

        if (statusBox) {
          statusBox.classList.add(result.success ? 'is-success' : 'is-error');
          statusBox.textContent = result.success
            ? result.message
            : (result.error || 'Something went wrong. Please try again.');
        }
        if (result.success) form.reset();
      } catch (err) {
        if (statusBox) {
          statusBox.classList.add('is-error');
          statusBox.textContent = 'Network error - please check your connection and try again.';
        }
      } finally {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = submitBtn.dataset.label || 'Submit'; }
      }
    });
  };

  handleFormSubmit('contactForm', `${API_BASE_URL}/api/contact`);
  handleFormSubmit('bookingForm', `${API_BASE_URL}/api/book-service`);

  // Project filter buttons
  const filterButtons = document.querySelectorAll('.filter-btn');
  const projectCards = document.querySelectorAll('.project-card');
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      filterButtons.forEach(b => b.classList.remove('is-active'));
      btn.classList.add('is-active');
      const cat = btn.dataset.filter;
      projectCards.forEach(card => {
        card.style.display = (cat === 'all' || card.dataset.category === cat) ? '' : 'none';
      });
    });
  });

  // Gallery tabs (same pattern as project filters)
  const galleryTabs = document.querySelectorAll('.gallery-tab');
  const galleryItems = document.querySelectorAll('.gallery-item');
  galleryTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      galleryTabs.forEach(t => t.classList.remove('is-active'));
      tab.classList.add('is-active');
      const cat = tab.dataset.filter;
      galleryItems.forEach(item => {
        item.style.display = (cat === 'all' || item.dataset.category === cat) ? '' : 'none';
      });
    });
  });

  // Lightbox
  const lightbox = document.getElementById('lightbox');
  if (lightbox) {
    const lightboxIcon = lightbox.querySelector('.lightbox-icon');
    const lightboxTitle = lightbox.querySelector('.lightbox-title');
    const lightboxClose = lightbox.querySelector('.lightbox-close');

    document.querySelectorAll('.gallery-item').forEach(item => {
      item.addEventListener('click', () => {
        if (lightboxIcon) lightboxIcon.className = 'fa-solid ' + (item.dataset.icon || 'fa-image') + ' lightbox-icon';
        if (lightboxTitle) lightboxTitle.textContent = item.dataset.title || '';
        lightbox.classList.add('is-open');
      });
    });
    const closeLightbox = () => lightbox.classList.remove('is-open');
    if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => { if (e.target === lightbox) closeLightbox(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeLightbox(); });
  }

  // Pre-fill "Service Required" on the booking form when arriving via a service card's "Book Service" link
  const params = new URLSearchParams(window.location.search);
  const serviceField = document.getElementById('service_required');
  if (serviceField && params.get('service')) {
    serviceField.value = params.get('service');
  }

  // Pre-select the subject dropdown on the contact page when arriving via a "Learn More" link
  const subjectField = document.getElementById('subject');
  if (subjectField && params.get('subject')) {
    subjectField.value = params.get('subject');
  }
});
