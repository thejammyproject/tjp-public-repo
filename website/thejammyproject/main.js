// Footer year
const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

// Mobile menu toggle + close behavior
const btn = document.getElementById('navToggle');
const menu = document.getElementById('site-menu');

if (btn && menu) {
  btn.addEventListener('click', () => {
    const isOpen = menu.classList.toggle('open');
    btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  // Close when a link is clicked
  menu.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      menu.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    });
  });

  // Close when clicking outside
  document.addEventListener('click', (e) => {
    if (!btn.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    }
  });

  // Optional: close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      menu.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
    }
  });
}

// Role-detail dialogs use an explicit open state so they also work in browsers
// where the native dialog top-layer API is unavailable or unreliable.
let activeDialog = null;
let dialogTrigger = null;
let roleRequest = 0;

async function openRoleDialog(dialog, trigger) {
  if (activeDialog) closeRoleDialog();
  activeDialog = dialog;
  dialogTrigger = trigger;
  const content = dialog.querySelector('#role-dialog-content');
  const role = trigger.dataset.role;
  const request = ++roleRequest;
  content.innerHTML = '<h2 id="role-dialog-title">Loading role details…</h2>';
  dialog.setAttribute('open', '');
  dialog.setAttribute('aria-modal', 'true');
  document.body.classList.add('modal-open');
  dialog.querySelector('.dialog-close')?.focus();

  if (!/^[a-z0-9-]+$/.test(role)) return;
  try {
    const response = await fetch(`modals/${role}.html`, { cache: 'default' });
    if (!response.ok) throw new Error('Role content unavailable');
    const markup = await response.text();
    if (activeDialog === dialog && request === roleRequest) content.innerHTML = markup;
  } catch {
    if (activeDialog === dialog && request === roleRequest) {
      content.innerHTML = '<h2 id="role-dialog-title">Role details unavailable</h2><p>Please try again shortly.</p>';
    }
  }
}

function closeRoleDialog() {
  if (!activeDialog) return;
  activeDialog.removeAttribute('open');
  activeDialog.removeAttribute('aria-modal');
  document.body.classList.remove('modal-open');
  const trigger = dialogTrigger;
  activeDialog = null;
  dialogTrigger = null;
  trigger?.focus();
}

document.addEventListener('click', event => {
  const trigger = event.target.closest?.('[data-role]');
  if (trigger) {
    const dialog = document.getElementById('role-dialog');
    if (dialog) openRoleDialog(dialog, trigger);
    return;
  }
  if (event.target.closest?.('.dialog-close')) closeRoleDialog();
  else if (activeDialog && !event.target.closest?.('.role-dialog')) closeRoleDialog();
});

document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && activeDialog) closeRoleDialog();
});
