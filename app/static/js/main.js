// ===== MULTIMARCAS BRAZO - MAIN JS =====

// Theme Management
const THEME_KEY = 'brazo-theme';

function getTheme() {
  return localStorage.getItem(THEME_KEY) || 'dark';
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);
  const btn = document.getElementById('themeToggle');
  if (btn) {
    btn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
    btn.title = theme === 'dark' ? 'Modo claro' : 'Modo oscuro';
  }
}

function toggleTheme() {
  const current = getTheme();
  setTheme(current === 'dark' ? 'light' : 'dark');
}

// Apply theme immediately to prevent flash
document.documentElement.setAttribute('data-theme', getTheme());

document.addEventListener('DOMContentLoaded', () => {
  // Init theme
  setTheme(getTheme());

  // Flash messages auto-dismiss
  const flashes = document.querySelectorAll('.flash-msg');
  flashes.forEach((flash, i) => {
    setTimeout(() => {
      flash.style.animation = 'slideIn 0.3s ease reverse';
      setTimeout(() => flash.remove(), 300);
    }, 4000 + (i * 500));
  });

  // Flash close buttons
  document.querySelectorAll('.flash-close').forEach(btn => {
    btn.addEventListener('click', () => {
      const msg = btn.closest('.flash-msg');
      msg.style.animation = 'slideIn 0.3s ease reverse';
      setTimeout(() => msg.remove(), 300);
    });
  });

  // Navbar active link
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

  // Fade up animations (intersection observer)
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.animate-on-scroll').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

  // Navbar scroll effect
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        navbar.style.boxShadow = '0 2px 40px rgba(232,0,13,0.08)';
      } else {
        navbar.style.boxShadow = '';
      }
    });
  }

  // Confirm delete dialogs
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      if (!confirm(el.dataset.confirm)) {
        e.preventDefault();
      }
    });
  });

  // Auto-close dropdowns
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown-wrapper')) {
      document.querySelectorAll('.dropdown-menu-brazo').forEach(d => {
        d.classList.remove('show');
      });
    }
  });
});

// Dropdown toggle
function toggleDropdown(id) {
  const menu = document.getElementById(id);
  if (menu) menu.classList.toggle('show');
}

// Format currency COP
function formatCOP(value) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency', currency: 'COP', minimumFractionDigits: 0
  }).format(value);
}

// Ripple effect on buttons
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.btn-primary-brazo, .btn-outline-brazo');
  if (!btn) return;
  const ripple = document.createElement('span');
  const rect = btn.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  ripple.style.cssText = `
    position:absolute;width:${size}px;height:${size}px;
    left:${e.clientX-rect.left-size/2}px;top:${e.clientY-rect.top-size/2}px;
    border-radius:50%;background:rgba(255,255,255,0.2);
    transform:scale(0);animation:ripple 0.5s ease;pointer-events:none;
  `;
  if (getComputedStyle(btn).position === 'static') btn.style.position = 'relative';
  btn.style.overflow = 'hidden';
  btn.appendChild(ripple);
  setTimeout(() => ripple.remove(), 500);
});

// CSS for ripple
const style = document.createElement('style');
style.textContent = `@keyframes ripple{to{transform:scale(2);opacity:0;}}`;
document.head.appendChild(style);