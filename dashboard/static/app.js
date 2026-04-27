let allJobs = [];

async function loadAll() {
  await Promise.all([loadStats(), loadJobs()]);
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const s = await res.json();
    document.getElementById('stat-total').textContent    = s.total;
    document.getElementById('stat-new').textContent      = s.new;
    document.getElementById('stat-reviewed').textContent = s.reviewed;
    document.getElementById('stat-applied').textContent  = s.applied;
    document.getElementById('stat-rejected').textContent = s.rejected;
    document.getElementById('stat-avg').textContent      = s.avg_score || '—';
  } catch (e) {
    console.error('Failed to load stats', e);
  }
}

async function loadJobs() {
  try {
    const res = await fetch('/api/jobs');
    allJobs = await res.json();
    applyFilters();
  } catch (e) {
    document.getElementById('job-list').innerHTML = '<p class="empty-msg">Failed to load jobs.</p>';
  }
}

function applyFilters() {
  const status   = document.getElementById('filter-status').value;
  const minScore = parseFloat(document.getElementById('filter-score').value) || 0;
  const search   = document.getElementById('filter-search').value.toLowerCase();

  const filtered = allJobs.filter(j => {
    if (status && j.status !== status) return false;
    if (j.relevance_score < minScore) return false;
    if (search && !j.title.toLowerCase().includes(search) && !j.company.toLowerCase().includes(search)) return false;
    return true;
  });

  renderJobs(filtered);
}

function renderJobs(jobs) {
  const el = document.getElementById('job-list');
  if (!jobs.length) {
    el.innerHTML = '<p class="empty-msg">No jobs match the current filters.</p>';
    return;
  }

  el.innerHTML = jobs.map(job => {
    const scoreClass = job.relevance_score >= 8 ? 'high' : job.relevance_score >= 6 ? 'mid' : 'low';
    return `
      <div class="job-card" onclick="openModal(${job.id})">
        <div class="job-card-left">
          <div class="job-title">${esc(job.title)}</div>
          <div class="job-meta">
            <span>🏢 ${esc(job.company)}</span>
            ${job.location ? `<span>📍 ${esc(job.location)}</span>` : ''}
            <span>🕐 ${formatDate(job.scraped_at)}</span>
            ${job.source ? `<span>🔗 ${esc(job.source)}</span>` : ''}
          </div>
        </div>
        <div class="job-card-right">
          <span class="score-badge ${scoreClass}">${job.relevance_score}/10</span>
          <span class="status-badge status-${job.status}">${job.status}</span>
        </div>
      </div>`;
  }).join('');
}

async function openModal(id) {
  const job = allJobs.find(j => j.id === id);
  if (!job) return;

  const scoreClass = job.relevance_score >= 8 ? 'high' : job.relevance_score >= 6 ? 'mid' : 'low';

  document.getElementById('modal-content').innerHTML = `
    <h2>${esc(job.title)}</h2>
    <div class="modal-company">
      ${esc(job.company)}
      ${job.location ? ' · ' + esc(job.location) : ''}
      &nbsp;·&nbsp;
      <span class="score-badge ${scoreClass}" style="font-size:0.8rem;padding:2px 8px">${job.relevance_score}/10</span>
      &nbsp;
      <span class="status-badge status-${job.status}">${job.status}</span>
    </div>

    ${job.relevance_reason ? `
      <div class="modal-section">
        <h3>AI Relevance Reason</h3>
        <p>${esc(job.relevance_reason)}</p>
      </div>` : ''}

    ${job.skills_required ? `
      <div class="modal-section">
        <h3>Skills Required</h3>
        <p>${esc(job.skills_required)}</p>
      </div>` : ''}

    ${job.resume_bullets ? `
      <div class="modal-section">
        <h3>Tailored Resume Bullets</h3>
        <pre>${esc(job.resume_bullets)}</pre>
      </div>` : ''}

    ${job.cover_letter ? `
      <div class="modal-section">
        <h3>Cover Letter</h3>
        <pre>${esc(job.cover_letter)}</pre>
      </div>` : ''}

    ${job.description ? `
      <div class="modal-section">
        <h3>Job Description</h3>
        <p>${esc(job.description.slice(0, 800))}${job.description.length > 800 ? '…' : ''}</p>
      </div>` : ''}

    <div class="modal-actions">
      <a href="${esc(job.url)}" target="_blank" rel="noopener">View on LinkedIn ↗</a>
      <div style="flex:1"></div>
      <button class="btn btn-purple" onclick="setStatus(${job.id}, 'reviewed')">Mark Reviewed</button>
      <button class="btn btn-green"  onclick="setStatus(${job.id}, 'applied')">Mark Applied</button>
      <button class="btn btn-red"    onclick="setStatus(${job.id}, 'rejected')">Reject</button>
    </div>`;

  document.getElementById('modal-overlay').classList.add('open');
}

async function setStatus(id, status) {
  await fetch(`/api/jobs/${id}/status?status=${status}`, { method: 'PATCH' });
  const job = allJobs.find(j => j.id === id);
  if (job) job.status = status;
  closeModal();
  loadAll();
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('open');
}

function esc(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

document.addEventListener('DOMContentLoaded', loadAll);
