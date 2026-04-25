const GENRE_GRADIENTS = {
  lofi:['#667eea','#764ba2'], pop:['#f093fb','#f5576c'], rock:['#4facfe','#00f2fe'],
  jazz:['#fa709a','#fee140'], shoegaze:['#a8edea','#fed6e3'], electronic:['#30cfd0','#330867'],
  classical:['#fddb92','#d1fdff'], _default:['#a855f7','#ec4899'],
};
const GENRE_EMOJI = { lofi:'🌙', pop:'⭐', rock:'🎸', jazz:'🎷', shoegaze:'🌊', electronic:'⚡', classical:'🎻' };

const FLOW_STATES = {
  login: {
    active: ['n-user','n-oauth','n-session'],
    activeClass: 'active',
    step: 'Google OAuth Login',
    files: [
      'users/auth/factory.py → get_auth_strategy()',
      'users/auth/google.py  → GoogleOAuthStrategy',
      'users/auth/service.py → AuthService',
      'users/views.py        → login_view / callback_view',
    ],
    pattern: 'Strategy Pattern', patternClass: 'accent',
    patternDetail: 'AuthStrategy → GoogleOAuthStrategy | MockAuthStrategy\nเลือก strategy จาก AUTH_STRATEGY ใน .env',
    desc: 'ผู้ใช้กด Login → AuthService.get_login_url() สร้าง OAuth URL พร้อม state token → redirect ไป Google → callback พร้อม code → handle_callback() แลก token → ดึง user info → get_or_create User → set session',
  },
  generate_idle: {
    active: ['n-form'],
    activeClass: 'active',
    step: 'Generate Form — Ready',
    files: ['song_api/views.py → generate_song()', 'song_api/urls.py → /api/generate/'],
    pattern: '—', patternClass: 'none', patternDetail: '',
    desc: 'รอผู้ใช้กรอกข้อมูลในฟอร์ม: prompt, genre, mood, vocal, occasion → กด Generate Song',
  },
  generating: {
    active: ['n-form','n-view','n-service','n-factory'],
    activeClass: 'active',
    step: 'Routing → Service → Factory',
    files: [
      'song_api/views.py → generate_song()',
      'song_api/generation/service.py → start()',
      'song_api/generation/factory.py → get_strategy()',
    ],
    pattern: 'Factory Pattern', patternClass: 'accent',
    patternDetail: 'StrategyFactory.get_strategy(provider)\n→ MockStrategy | SunoStrategy',
    desc: 'Request ถูกส่งมาที่ Django View → GenerationService.start() → StrategyFactory อ่าน GENERATOR_STRATEGY จาก .env เพื่อเลือก strategy',
  },
  mock_running: {
    active: ['n-mock','n-instant'],
    activeClass: 'active-teal',
    step: 'MockStrategy — Generating',
    files: ['song_api/generation/mock.py → MockStrategy.generate()'],
    pattern: 'Strategy Pattern', patternClass: 'teal',
    patternDetail: 'MockStrategy implements GenerationStrategy\n→ ไม่เรียก API จริง, return ผลทันที',
    desc: 'MockStrategy สร้าง GenerationResult จำลองทันทีโดยไม่เรียก Suno API — ใช้สำหรับ dev/test',
  },
  suno_pending: {
    active: ['n-suno'],
    activeClass: 'active',
    step: 'SunoStrategy — Calling API',
    files: ['song_api/generation/suno.py → SunoStrategy.generate()'],
    pattern: 'Strategy Pattern', patternClass: 'accent',
    patternDetail: 'SunoStrategy implements GenerationStrategy\n→ POST /api/generate ไปที่ Suno',
    desc: 'SunoStrategy ส่ง HTTP request ไปที่ Suno API พร้อม prompt และ parameters → ได้ job_id กลับมา',
  },
  suno_polling: {
    active: ['n-suno','n-poll'],
    activeClass: 'active',
    step: 'Polling Suno Status',
    files: [
      'song_api/generation/suno.py → poll_status()',
      'song_api/views.py → generation_status()',
    ],
    pattern: '—', patternClass: 'none', patternDetail: '',
    desc: 'เช็ค status ของ job ทุก 3 วินาที จนกว่าจะได้ SUCCESS → ดึง audio URL กลับมา',
  },
  saving: {
    active: ['n-db'],
    activeClass: 'active',
    step: 'Saving to Database',
    files: [
      'song_api/models.py → Song.objects.create()',
      'song_api/views.py → songs_api() POST',
    ],
    pattern: '—', patternClass: 'none', patternDetail: '',
    desc: 'บันทึก Song object ลง Database พร้อม audio_url → พร้อมให้ Library ดึงมาแสดง',
  },
  library: {
    active: ['n-library','n-audio'],
    activeClass: 'active',
    step: 'Library — Displaying Songs',
    files: [
      'song_api/views.py → songs_api() GET',
      'song_api/urls.py → /api/songs/',
    ],
    pattern: '—', patternClass: 'none', patternDetail: '',
    desc: 'GET /api/songs/?username=X → ดึงเพลงทั้งหมดของ user → render Library grid พร้อม audio player',
  },
  sharing_create: {
    active: ['n-audio'],
    activeClass: 'active',
    step: 'Creating Share Link',
    files: [
      'sharing/views.py → create_share_link()',
      'sharing/models.py → ShareLink.objects.create()',
      'sharing/urls.py  → POST /api/share/',
    ],
    pattern: '—', patternClass: 'none', patternDetail: '',
    desc: 'POST /api/share/ {song_id, username} → deactivate link เก่า → สร้าง ShareLink ใหม่พร้อม UUID token → ส่ง URL กลับ → user copy ส่งให้เพื่อน',
  },
  shared: {
    active: ['n-audio'],
    activeClass: 'active',
    step: 'Shared Song — Friend View',
    files: [
      'sharing/views.py → get_share_link()',
      'sharing/models.py → ShareLink (token, is_active)',
      'sharing/urls.py  → GET /api/share/<token>/',
    ],
    pattern: '—', patternClass: 'none', patternDetail: '',
    desc: 'เพื่อนเปิด URL /?token=<uuid> → Frontend GET /api/share/<token>/ → ตรวจ is_active=True → return ข้อมูลเพลง + shared_by → แสดง Shared Song page พร้อม audio player',
  },
};

let currentUser         = null;
let library             = [];
let currentTab          = null;
let currentFlowState    = null;
let lastFormData        = null;
let currentDownloadSong = null;
let currentSharedSong   = null;

function setFlowState(key) {
  currentFlowState = key;
  applyFlowState(key);
}

function applyFlowState(key) {
  const state = FLOW_STATES[key];
  if (!state) return;

  document.querySelectorAll('.fn').forEach(el => el.classList.remove('active','active-teal'));
  state.active.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add(state.activeClass || 'active');
  });

  const stepEl = document.getElementById('detail-step');
  if (stepEl) stepEl.textContent = state.step;

  const filesEl = document.getElementById('detail-files');
  if (filesEl) {
    filesEl.innerHTML = state.files.map(f => `
      <div class="file-chip">
        <span class="file-chip-icon">📄</span>
        <span class="file-chip-path">${esc(f)}</span>
      </div>`).join('');
  }

  const patternEl = document.getElementById('detail-pattern');
  if (patternEl) {
    if (state.pattern === '—') {
      patternEl.innerHTML = `<div class="pattern-box none"><div class="pattern-name">ไม่มี Pattern พิเศษ</div></div>`;
    } else {
      patternEl.innerHTML = `
        <div class="pattern-box ${state.patternClass}">
          <div class="pattern-name">${esc(state.pattern)}</div>
          ${state.patternDetail ? `<div class="pattern-detail">${esc(state.patternDetail)}</div>` : ''}
        </div>`;
    }
  }

  const descEl = document.getElementById('detail-desc');
  if (descEl) descEl.textContent = state.desc;
}

function showPage(name) {
  document.getElementById('page-login').style.display  = name === 'login'  ? '' : 'none';
  document.getElementById('app-shell').style.display   = ['generate','library','flow'].includes(name) ? '' : 'none';
  document.getElementById('page-shared').style.display = name === 'shared' ? '' : 'none';
  document.getElementById('bottom-nav').style.display  = name === 'login'  ? 'none' : '';
}

function switchTab(tab) {
  if (!currentUser) { showPage('login'); return; }
  showPage(tab);
  currentTab = tab;

  const sections = { generate:'main-generate', library:'main-library', flow:'main-flow' };
  Object.entries(sections).forEach(([t, id]) => {
    const el = document.getElementById(id);
    if (el) el.style.display = t === tab ? '' : 'none';
  });

  ['generate','library','flow'].forEach(t => {
    const el = document.getElementById('nav-' + t);
    if (el) el.classList.toggle('active', t === tab);
  });

  const bnavMap = { generate:'gen', library:'lib', flow:'flo' };
  ['gen','lib','flo'].forEach(k => {
    const el = document.getElementById('bnav-' + k);
    if (el) el.classList.toggle('active', bnavMap[tab] === k);
  });

  if (tab === 'library') { fetchLibrary(); }
  if (tab === 'generate' && !document.getElementById('result-section').classList.contains('show')) {
    setFlowState('generate_idle');
  }
  if (tab === 'flow' && currentFlowState) applyFlowState(currentFlowState);
}

async function loadSharedFromToken(token) {
  setFlowState('shared');
  try {
    const resp = await fetch(`/api/share/${token}/`);
    if (!resp.ok) {
      showToast('Link ไม่ถูกต้องหรือหมดอายุแล้ว', 'error');
      showPage('login');
      return;
    }
    const data = await resp.json();
    const song = { ...data.song, audio: data.song.audio_url, token: data.token };
    currentSharedSong = song;

    const colors = gradient(song.genre);
    document.getElementById('shared-art').style.background = `linear-gradient(135deg,${colors[0]},${colors[1]})`;
    document.getElementById('shared-art').textContent = GENRE_EMOJI[song.genre] || '🎵';
    document.getElementById('shared-title').textContent = song.title;
    document.getElementById('shared-meta').textContent  = `${cap(song.genre)} · ${cap(song.mood)} · ${vocalLabel(song.vocal)}`;
    document.getElementById('shared-by').textContent    = `Shared by ${data.shared_by || 'someone'}`;
    document.getElementById('shared-audio').src = song.audio || '';

    showPage('shared');
  } catch (_) {
    showPage('login');
  }
}

function downloadSharedSong() {
  if (!currentSharedSong || !currentSharedSong.token) {
    showToast('No song to download', 'error');
    return;
  }

  const url = `/api/share/${currentSharedSong.token}/download/?fmt=mp3`;
  const a = document.createElement('a');
  a.href = url;
  a.download = `${currentSharedSong.title || 'song'}.mp3`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  showToast('⬇️ Downloading...', 'info');
}

function login() {
  window.location.href = '/auth/login/';
}

async function logout() {
  try {
    await fetch('/auth/logout/', { method: 'POST' });
  } catch (_) {}
  currentUser = null;
  library = [];
  showPage('login');
  showToast('Logged out', 'info');
}

async function checkSession() {
  try {
    const resp = await fetch('/auth/me/');
    if (!resp.ok) return null;
    return await resp.json();
  } catch (_) {
    return null;
  }
}

function _applyUser(user) {
  currentUser = user;
  document.getElementById('sidebar-name').textContent  = user.username;
  document.getElementById('sidebar-email').textContent = user.email;
  document.getElementById('sidebar-avatar').src        = user.avatar;
}

function handleGenerate(e) {
  e.preventDefault();
  const prompt = document.getElementById('f-prompt').value.trim();
  if (!prompt) { showToast('Please enter a prompt', 'error'); return; }

  const formData = {
    prompt,
    title:    document.getElementById('f-title').value.trim() || autoTitle(),
    genre:    document.getElementById('f-genre').value    || 'lofi',
    mood:     document.getElementById('f-mood').value     || 'calm',
    vocal:    document.getElementById('f-vocal').value    || 'none',
    occasion: document.getElementById('f-occasion').value || 'none',
    story:    document.getElementById('f-story').value.trim(),
  };

  _doGenerate(formData);
}

function regenerateSong() {
  if (!lastFormData) {
    showToast('No previous song to regenerate', 'error');
    return;
  }

  document.getElementById('f-prompt').value   = lastFormData.prompt   || '';
  document.getElementById('f-title').value    = lastFormData.title    || '';
  document.getElementById('f-story').value    = lastFormData.story    || '';
  document.getElementById('f-genre').value    = lastFormData.genre    || '';
  document.getElementById('f-mood').value     = lastFormData.mood     || '';
  document.getElementById('f-vocal').value    = lastFormData.vocal    || '';
  document.getElementById('f-occasion').value = lastFormData.occasion || '';

  switchTab('generate');

  document.getElementById('result-section').classList.remove('show');
  setTimeout(() => {
    const promptEl = document.getElementById('f-prompt');
    promptEl.focus();
    promptEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, 100);
  showToast('Settings copied — แก้ไขแล้วกด Generate', 'info');
}

function _doGenerate(formData) {
  lastFormData = formData;

  setFormDisabled(true);
  document.getElementById('result-section').classList.remove('show');

  const overlay = document.getElementById('progress-overlay');
  overlay.classList.add('active');
  _setProgress(0, 'Sending to AI...', '📡');
  setFlowState('generating');

  fetch('/api/generate/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData),
  })
    .then(r => r.json())
    .then(job => {
      if (job.error) throw new Error(job.error);
      _setProgress(20, 'Composing melody...', '🎼');
      setFlowState('mock_running');
      _pollJob(job.job_id, formData);
    })
    .catch(err => {
      overlay.classList.remove('active');
      setFormDisabled(false);
      showToast(err.message || 'Generation failed', 'error');
    });
}

function _pollJob(jobId, formData) {
  fetch(`/api/generate/${jobId}/status/`)
    .then(r => r.json())
    .then(data => {
      if (data.error) throw new Error(data.error);

      if (data.status === 'TEXT_SUCCESS') {
        _setProgress(40, 'Generating vocals...', '🎤');
        setFlowState('suno_polling');
        setTimeout(() => _pollJob(jobId, formData), 3000);

      } else if (data.status === 'FIRST_SUCCESS') {
        _setProgress(70, 'Finalizing...', '✨');
        setFlowState('suno_polling');
        setTimeout(() => _pollJob(jobId, formData), 3000);

      } else if (data.status === 'SUCCESS') {
        _setProgress(100, 'Done!', '✅');
        setFlowState('saving');
        setTimeout(() => _onGenerateDone(data, formData), 500);

      } else if (data.status === 'FAILED') {
        throw new Error(data.error || 'Generation failed');

      } else {

        setTimeout(() => _pollJob(jobId, formData), 3000);
      }
    })
    .catch(err => {
      document.getElementById('progress-overlay').classList.remove('active');
      setFormDisabled(false);
      showToast(err.message || 'Generation failed', 'error');
    });
}

function _onGenerateDone(jobData, formData) {
  document.getElementById('progress-overlay').classList.remove('active');
  setFormDisabled(false);

  const newSong = {
    id:      jobData.song_id,
    title:   formData.title,
    genre:   formData.genre,
    mood:    formData.mood,
    vocal:   formData.vocal,
    created: 'just now',
    audio:   jobData.audio_url || '',
  };
  library.unshift(newSong);
  renderResultCard(newSong);
  showToast('🎵 Song generated successfully!', 'success');
  setFlowState('library');
}

function _setProgress(pct, msg, icon) {
  document.getElementById('prog-stage').textContent = msg;
  document.getElementById('prog-icon').textContent  = icon;
  document.getElementById('prog-bar').style.width   = pct + '%';
  document.getElementById('prog-pct').textContent   = pct + '%';
}

function setFormDisabled(d) {
  document.getElementById('gen-form').querySelectorAll('input,textarea,select,button').forEach(el => el.disabled = d);
}

function autoTitle() {
  const adj  = ['Midnight','Golden','Electric','Dreamy','Neon','Velvet','Crystal','Hazy','Crimson'];
  const noun = ['Journey','Horizon','Echo','Dream','Storm','Memory','Pulse','Garden','Tide'];
  return adj[Math.floor(Math.random()*adj.length)] + ' ' + noun[Math.floor(Math.random()*noun.length)];
}

function renderResultCard(song) {
  const [c1,c2] = gradient(song.genre);
  const em = GENRE_EMOJI[song.genre] || '🎵';
  document.getElementById('result-card').innerHTML = `
    <div class="result-meta">
      <div class="result-art" style="background:linear-gradient(135deg,${c1},${c2})">${em}</div>
      <div style="flex:1">
        <div class="result-title">${esc(song.title)}</div>
        <div class="result-tags">
          <span class="tag tag-purple">${esc(song.genre)}</span>
          <span class="tag tag-teal">${esc(song.mood)}</span>
          <span class="tag tag-pink">${vocalLabel(song.vocal)}</span>
        </div>
      </div>
    </div>
    <audio controls style="width:100%;margin-top:14px;border-radius:8px;accent-color:var(--accent)">
      <source src="${esc(song.audio)}" type="audio/mpeg" />
    </audio>
    <div class="result-btns">
      <button type="button" class="btn btn-secondary" onclick="regenerateSong()">🔄 Regenerate</button>
      <button type="button" class="btn btn-secondary" onclick="openShareModal(${song.id})">🔗 Share</button>
      <button type="button" class="btn btn-secondary" onclick='openDownloadModal(${JSON.stringify({id:song.id,title:song.title,audio:song.audio})})'>⬇️ Download</button>
      <button type="button" class="btn btn-secondary" onclick="switchTab('library')">📚 Library</button>
    </div>
  `;
  const rs = document.getElementById('result-section');
  rs.classList.add('show');
  setTimeout(() => rs.scrollIntoView({ behavior:'smooth', block:'start' }), 80);
}

async function fetchLibrary() {
  setFlowState('library');
  const grid = document.getElementById('lib-grid');
  if (!grid) return;

  try {
    const resp = await fetch(`/api/songs/?username=${encodeURIComponent(currentUser.username)}`);
    if (!resp.ok) throw new Error();
    const songs = await resp.json();
    library = songs.map(s => ({
      id:      s.id,
      title:   s.title,
      genre:   s.genre,
      mood:    s.mood,
      vocal:   s.vocal,
      created: new Date(s.create_at).toLocaleDateString('th-TH'),
      audio:   s.audio_url || s.path || '',
    }));
  } catch (_) {

  }

  _renderLibraryGrid();
}

function _renderLibraryGrid() {
  const grid = document.getElementById('lib-grid');
  if (!grid) return;

  if (!library.length) {
    grid.innerHTML = `<div style="color:var(--text-muted);padding:40px 0;grid-column:1/-1;text-align:center;">ยังไม่มีเพลง — ไปสร้างเพลงแรกกันเลย ✨</div>`;
    return;
  }

  grid.innerHTML = library.map(song => {
    const [c1,c2] = gradient(song.genre);
    const em = GENRE_EMOJI[song.genre] || '🎵';
    return `
      <div class="song-card">
        <div class="song-art" style="background:linear-gradient(135deg,${c1},${c2})">
          <span class="song-art-inner">${em}</span>
        </div>
        <div class="song-body">
          <div class="song-title">${esc(song.title)}</div>
          <div class="song-tags">
            <span class="tag tag-purple">${esc(song.genre)}</span>
            <span class="tag tag-teal">${esc(song.mood)}</span>
            <span class="tag tag-pink">${vocalLabel(song.vocal)}</span>
          </div>
          <div class="song-date">🕐 ${song.created}</div>
          <div class="song-player">
            <audio controls><source src="${esc(song.audio)}" type="audio/mpeg" /></audio>
          </div>
          <div class="song-actions">
            <button class="btn btn-secondary" onclick="openShareModal(${song.id})">🔗 Share</button>
            <button class="btn btn-secondary" onclick='openDownloadModal(${JSON.stringify({id:song.id,title:song.title,audio:song.audio})})'>⬇️ Download</button>
          </div>
        </div>
      </div>`;
  }).join('');
}

function openModal(id)  { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }
function closeModalOnBg(e,id) { if (e.target.id === id) closeModal(id); }

async function openShareModal(songId) {
  setFlowState('sharing_create');

  const urlEl   = document.getElementById('share-url-text');
  const copyBtn = document.querySelector('#share-modal .btn-secondary');
  urlEl.textContent = 'กำลังสร้าง link...';
  if (copyBtn) copyBtn.disabled = true;
  openModal('share-modal');

  try {
    const resp = await fetch('/api/share/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        song_id:  songId,
        username: currentUser ? currentUser.username : '',
      }),
    });
    const data = await resp.json();
    if (resp.ok) {
      urlEl.textContent = `${window.location.origin}/?token=${data.token}`;
    } else {
      urlEl.textContent = `${window.location.origin}/?token=demo${songId}`;
      showToast(data.error || 'ไม่สามารถสร้าง link ได้', 'error');
    }
  } catch (_) {
    urlEl.textContent = `${window.location.origin}/?token=demo${songId}`;
  }

  if (copyBtn) copyBtn.disabled = false;
}

function copyShareLink() {
  const url = document.getElementById('share-url-text').textContent;
  navigator.clipboard.writeText(url)
    .then(() => { showToast('🔗 Link copied!', 'success'); closeModal('share-modal'); })
    .catch(()  => { showToast('🔗 Link copied!', 'success'); closeModal('share-modal'); });
}
function openDownloadModal(song) {
  currentDownloadSong = song;
  openModal('dl-modal');
}

function openHelp() { openModal('help-modal'); }

const TOUR_STEPS = [
  {
    selector: '#f-prompt',
    title: '✍️ เริ่มจาก Prompt',
    desc: 'เขียนอธิบายเพลงที่อยากได้ที่นี่ — ยิ่งละเอียดยิ่งดี เช่น "lo-fi เบาๆ สำหรับนั่งทำงานตอนกลางคืน"',
    position: 'right',
    requireTab: 'generate',
  },
  {
    selector: '#f-genre',
    title: '🎼 เลือก Genre',
    desc: 'เลือกแนวเพลง — Lo-fi, Pop, Rock, Jazz หรืออื่นๆ',
    position: 'right',
    requireTab: 'generate',
  },
  {
    selector: '#f-mood',
    title: '😌 ตั้ง Mood',
    desc: 'เลือกอารมณ์เพลง — Calm, Happy, Energetic ฯลฯ',
    position: 'right',
    requireTab: 'generate',
  },
  {
    selector: '#btn-gen',
    title: '✨ กด Generate',
    desc: 'พร้อมแล้วกดปุ่มนี้เลย! ระบบจะสร้างเพลงให้ภายในไม่กี่วินาที',
    position: 'top',
    requireTab: 'generate',
  },
  {
    selector: '#right-panel',
    title: '🗺 Real-time Flow',
    desc: 'panel ขวานี้แสดงว่าระบบกำลังทำอะไรอยู่ — ดู step, file ที่เกี่ยวข้อง, และ design pattern แบบเรียลไทม์',
    position: 'left',
    requireTab: 'generate',
  },
  {
    selector: '#nav-library',
    title: '📚 Library',
    desc: 'เพลงที่สร้างทั้งหมดเก็บอยู่ในนี้ — ฟัง, share, download ได้',
    position: 'right',
    requireTab: 'generate',
  },
  {
    selector: '#nav-help',
    title: '❓ Help เมื่อต้องการ',
    desc: 'กดตรงนี้ได้ตลอดเวลาถ้าอยากดูคำแนะนำการใช้งานอีกครั้ง',
    position: 'right',
    requireTab: 'generate',
  },
];

let _tourIndex = 0;
let _tourResizeHandler = null;

function startTour() {
  _tourIndex = 0;
  switchTab('generate');

  setTimeout(() => {
    document.getElementById('tour-root').classList.add('active');
    _renderTourStep();
    _tourResizeHandler = () => _renderTourStep();
    window.addEventListener('resize', _tourResizeHandler);
    window.addEventListener('scroll', _tourResizeHandler, true);
  }, 250);
}

function nextTourStep() {
  _tourIndex++;
  if (_tourIndex >= TOUR_STEPS.length) {
    endTour(false);
    return;
  }
  _renderTourStep();
}

function _renderTourStep() {
  const step = TOUR_STEPS[_tourIndex];
  if (!step) return;

  if (step.requireTab && currentTab !== step.requireTab) switchTab(step.requireTab);

  const target = document.querySelector(step.selector);
  if (!target) { nextTourStep(); return; }

  const rect = target.getBoundingClientRect();
  const padding = 8;

  const spotlight = document.getElementById('tour-spotlight');
  spotlight.style.top    = (rect.top - padding) + 'px';
  spotlight.style.left   = (rect.left - padding) + 'px';
  spotlight.style.width  = (rect.width + padding * 2) + 'px';
  spotlight.style.height = (rect.height + padding * 2) + 'px';

  const tip = document.getElementById('tour-tooltip');
  document.getElementById('tour-tooltip-step').textContent  = `STEP ${_tourIndex + 1} / ${TOUR_STEPS.length}`;
  document.getElementById('tour-tooltip-title').textContent = step.title;
  document.getElementById('tour-tooltip-desc').textContent  = step.desc;
  document.getElementById('tour-next-btn').textContent =
    _tourIndex === TOUR_STEPS.length - 1 ? 'Done ✓' : 'Next →';

  tip.classList.remove('pos-right','pos-left','pos-top','pos-bottom');
  tip.classList.add('pos-' + (step.position || 'right'));

  const tipW = 320;
  const tipH = tip.offsetHeight || 180;
  const gap = 20;
  let top, left;

  switch (step.position) {
    case 'left':
      top  = rect.top + rect.height / 2 - 30;
      left = rect.left - tipW - gap;
      break;
    case 'top':
      top  = rect.top - tipH - gap;
      left = rect.left + rect.width / 2 - tipW / 2;
      break;
    case 'bottom':
      top  = rect.bottom + gap;
      left = rect.left + rect.width / 2 - tipW / 2;
      break;
    default:
      top  = rect.top + rect.height / 2 - 30;
      left = rect.right + gap;
  }

  top  = Math.max(16, Math.min(top,  window.innerHeight - tipH - 16));
  left = Math.max(16, Math.min(left, window.innerWidth  - tipW - 16));

  tip.style.top  = top + 'px';
  tip.style.left = left + 'px';
}

function endTour(skipped) {
  document.getElementById('tour-root').classList.remove('active');
  if (_tourResizeHandler) {
    window.removeEventListener('resize', _tourResizeHandler);
    window.removeEventListener('scroll', _tourResizeHandler, true);
    _tourResizeHandler = null;
  }

  fetch('/auth/tour-complete/', { method: 'POST' }).catch(() => {});
  if (!skipped) showToast('✨ ยินดีต้อนรับสู่ Cithara!', 'success');
}

function handleDownload(fmt) {
  if (!currentDownloadSong || !currentDownloadSong.id) {
    showToast('No song selected', 'error');
    return;
  }

  const url = `/api/songs/${currentDownloadSong.id}/download/?fmt=${encodeURIComponent(fmt.toLowerCase())}`;
  const a = document.createElement('a');
  a.href = url;
  a.download = `${currentDownloadSong.title || 'song'}.${fmt.toLowerCase()}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  closeModal('dl-modal');
  showToast(`⬇️ Downloading as ${fmt}...`, 'info');
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') document.querySelectorAll('.modal-overlay.open').forEach(el => el.classList.remove('open'));
});

function showToast(msg, type = 'success') {
  const icons = { success:'✅', error:'❌', info:'ℹ️', warning:'⚠️' };
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.innerHTML = `<span>${icons[type]||'💬'}</span><span>${msg}</span>`;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => { el.classList.add('out'); setTimeout(() => el.remove(), 300); }, 3000);
}

function gradient(genre) { return GENRE_GRADIENTS[genre] || GENRE_GRADIENTS._default; }
function cap(s) { return s ? s[0].toUpperCase() + s.slice(1) : s; }
function vocalLabel(v) { return { male:'Male', female:'Female', none:'Instrumental' }[v] || cap(v) || '—'; }
function esc(s) { const d = document.createElement('div'); d.appendChild(document.createTextNode(s||'')); return d.innerHTML; }

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('btn-google');
  if (btn) btn.onclick = login;
  const logoutBtn = document.querySelector('.btn-logout');
  if (logoutBtn) logoutBtn.onclick = logout;
});

(async () => {
  setFlowState('login');

  const urlToken = new URLSearchParams(window.location.search).get('token');
  if (urlToken) {
    await loadSharedFromToken(urlToken);
    return;
  }

  const user = await checkSession();
  if (user) {
    _applyUser(user);
    switchTab('generate');
    if (user.tour_seen === false) {

      setTimeout(() => startTour(), 600);
    } else {
      showToast(`Welcome back, ${user.username}! 👋`, 'success');
    }
  } else {
    showPage('login');
  }
})();
