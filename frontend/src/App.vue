<template>
  <div class="app-shell" :class="{ dark: darkMode }">
    <header class="site-header">
      <div class="brand" @click="go('home')" title="回首頁">
        <div class="brand-mark">⚡</div>
        <div>
          <h1>全源配服</h1>
          <p>SDG 7 能源遊戲化學習平台</p>
        </div>
      </div>

      <button class="mobile-menu" @click="menuOpen = !menuOpen" aria-label="切換選單">
        ☰
      </button>

      <div class="header-main" :class="{ open: menuOpen }">
        <nav class="nav-pills" aria-label="主要導覽">
          <button v-for="item in navItems" :key="item.key" :class="{ active: page === item.key }" @click="go(item.key)">
            {{ item.label }}
          </button>
        </nav>

        <div class="mode-tools" aria-label="顯示與展示設定">
          <label class="switch-line">
            <span class="switch">
              <input type="checkbox" v-model="demoMode" />
              <span class="slider"></span>
            </span>
            <span>DEMO 模式</span>
          </label>
          <label class="switch-line">
            <span class="switch">
              <input type="checkbox" v-model="darkMode" />
              <span class="slider"></span>
            </span>
            <span>深色模式</span>
          </label>
        </div>
      </div>
    </header>

    <div v-if="demoMode" class="demo-ribbon" role="status" aria-live="polite">
      <div>
        <b>DEMO 展示模式已啟用</b>
        <span>{{ demoStatusText }}</span>
      </div>
      <div class="demo-ribbon-actions">
        <button class="outline small" @click="go('memory')">展示翻牌</button>
        <button class="outline small" @click="go('quiz')">展示問答</button>
        <button class="primary small" @click="seedDemo">產生展示資料</button>
      </div>
    </div>

    <main class="page-wrap">
      <section v-if="page === 'home'" class="page-section home-layout">
        <div class="hero-card glass-card">
          <span class="eyebrow">Affordable and Clean Energy</span>
          <h2>用翻牌與問答，學會不同能源的特色與限制</h2>
          <p>
            本平台結合 Flask 後端 API、能源題庫、遊戲紀錄與排行榜，讓使用者在互動中理解 SDG 7 與能源轉型議題。
          </p>
          <div class="player-row">
            <input v-model="playerName" maxlength="20" placeholder="輸入玩家暱稱" @keyup.enter="startTask" />
            <button class="primary" @click="startTask">開始任務</button>
          </div>
          <div class="connection" :class="apiOk ? 'ok' : 'bad'">
            <span></span>{{ apiOk ? '後端連線正常' : '後端尚未連線' }}
          </div>
        </div>

        <div class="stat-grid home-stats">
          <div class="stat-card"><strong>{{ energies.length }}</strong><span>能源圖鑑</span></div>
          <div class="stat-card"><strong>{{ questions.length }}</strong><span>後端題庫</span></div>
          <div class="stat-card"><strong>{{ playerSummary.totalPoints || 0 }}</strong><span>知識點數</span></div>
          <div class="stat-card"><strong>{{ leaderboard.length }}</strong><span>排行榜玩家</span></div>
        </div>

        <div class="task-panel glass-card full-span">
          <div class="section-title compact">
            <h3>今日學習任務</h3>
            <p>適合 DEMO 時快速展示完整資料流。</p>
          </div>
          <div class="task-grid">
            <button class="task-card" @click="go('atlas')"><b>01</b><span>查看能源圖鑑</span><small>理解六種能源特性</small></button>
            <button class="task-card" @click="startTask"><b>02</b><span>完成翻牌配對</span><small>重新開啟任務並記錄目前玩家</small></button>
            <button class="task-card" @click="go('quiz')"><b>03</b><span>完成問答闖關</span><small>答題結果寫入 API</small></button>
            <button class="task-card" @click="go('leaderboard')"><b>04</b><span>查看排行榜</span><small>用後端結果即時計算</small></button>
          </div>
        </div>
      </section>

      <section v-if="page === 'atlas'" class="page-section">
        <div class="section-title">
          <h2>能源圖鑑</h2>
          <p>資料由 Flask 後端 API 提供，前端負責視覺化呈現。</p>
        </div>
        <div class="energy-grid">
          <article v-for="e in energies" :key="e.id" class="energy-card">
            <div class="energy-top">
              <div class="energy-icon">{{ e.icon }}</div>
              <div><h3>{{ e.name }}</h3><span>{{ e.type }}</span></div>
            </div>
            <p class="principle">{{ e.principle }}</p>
            <div class="chips"><span v-for="k in e.keywords" :key="k">{{ k }}</span></div>
            <div class="energy-lists">
              <div><b>優點</b><ul><li v-for="p in e.pros" :key="p">{{ p }}</li></ul></div>
              <div><b>限制</b><ul><li v-for="c in e.cons" :key="c">{{ c }}</li></ul></div>
            </div>
            <div class="case-box">台灣案例：{{ e.taiwanExample }}</div>
          </article>
        </div>
      </section>

      <section v-if="page === 'memory'" class="page-section">
        <div class="section-title with-action">
          <div>
            <h2>翻牌配對挑戰</h2>
            <p>圖示卡與關鍵字卡配對成功後，系統會顯示學習知識卡並送出學習紀錄。</p>
          </div>
          <button class="outline" @click="resetMemory">重新開始</button>
        </div>

        <div class="game-meta">
          <span>步數：{{ memoryMoves }}</span>
          <span>配對：{{ matchedPairs }} / {{ energies.length }}</span>
          <span>{{ memoryMessage || '請翻開兩張卡片配對' }}</span>
        </div>

        <div v-if="demoMode" class="demo-actions glass-card">
          <div>
            <b>翻牌 DEMO 快捷</b>
            <p>現場展示可直接提示下一組或一鍵完成，避免因找不到配對而拖延。</p>
          </div>
          <button class="outline" @click="demoRevealNextPair">提示下一組配對</button>
          <button class="primary" @click="demoCompleteMemory">一鍵完成翻牌</button>
        </div>

        <div class="memory-grid">
          <button v-for="card in memoryCards" :key="card.uid" class="memory-card" :class="{ flipped: card.flipped || card.matched, matched: card.matched }" @click="flipCard(card)">
            <div class="memory-inner">
              <div class="memory-front">?</div>
              <div class="memory-back">
                <div class="mini-type">{{ card.cardType === 'visual' ? '圖示卡' : '關鍵字卡' }}</div>
                <div class="big-icon">{{ card.cardType === 'visual' ? card.icon : '🔎' }}</div>
                <strong>{{ card.cardType === 'visual' ? card.title : card.text }}</strong>
              </div>
            </div>
          </button>
        </div>
      </section>

      <section v-if="page === 'quiz'" class="page-section">
        <div class="section-title with-action">
          <div>
            <h2>問答闖關</h2>
            <p>題目由後端題庫提供，結果會回傳後端儲存。</p>
          </div>
          <button class="outline" @click="resetQuiz">重新開始</button>
        </div>

        <div class="quiz-card" v-if="currentQuestion">
          <div class="progress-bar"><span :style="{ width: quizProgress + '%' }"></span></div>
          <div class="quiz-meta">第 {{ quizIndex + 1 }} / {{ questions.length }} 題｜{{ currentQuestion.level }}</div>
          <h3>{{ currentQuestion.question }}</h3>
          <div class="options">
            <button v-for="(op, idx) in currentQuestion.options" :key="op" :class="answerClass(idx)" @click="chooseAnswer(idx)">{{ op }}</button>
          </div>
          <div v-if="answerState.locked" class="explain-box" :class="answerState.correct ? 'right' : 'wrong'">
            <b>{{ answerState.correct ? '答對了' : '答錯了' }}</b>
            <p>{{ currentQuestion.explanation }}</p>
          </div>
          <div v-if="demoMode" class="demo-actions inline">
            <div>
              <b>問答 DEMO 快捷</b>
              <p>可快速選正解或完成整套題目，確保 3 分鐘展示時間內看得到成果頁與排行榜。</p>
            </div>
            <button class="outline" @click="demoAnswerCurrent">選擇本題正解</button>
            <button class="primary" @click="demoCompleteQuiz">一鍵完成問答</button>
          </div>
          <div class="quiz-actions">
            <button class="outline" @click="prevQuestion" :disabled="quizIndex === 0">上一題</button>
            <button class="outline" @click="skipQuestion" :disabled="answerState.locked">跳過</button>
            <button class="primary" @click="submitAnswer" :disabled="answerState.choice === null || answerState.locked">送出</button>
            <button class="outline" @click="nextQuestion" :disabled="quizIndex >= questions.length - 1">下一題</button>
            <button class="primary" @click="finishQuiz">完成並儲存</button>
          </div>
        </div>
      </section>

      <section v-if="page === 'result'" class="page-section">
        <div class="section-title">
          <h2>學習成果</h2>
          <p>後端依玩家名稱彙整歷史紀錄與徽章。</p>
        </div>
        <div class="stat-grid result-stats">
          <div class="stat-card"><strong>{{ playerSummary.playCount || 0 }}</strong><span>遊玩次數</span></div>
          <div class="stat-card"><strong>{{ playerSummary.totalPoints || 0 }}</strong><span>累積點數</span></div>
          <div class="stat-card"><strong>{{ playerSummary.avgAccuracy || 0 }}%</strong><span>平均正確率</span></div>
          <div class="stat-card"><strong>{{ playerSummary.weakCategory || '待觀察' }}</strong><span>建議複習</span></div>
        </div>
        <div class="glass-card">
          <h3>已獲得徽章</h3>
          <div class="badge-row" v-if="playerSummary.badges?.length">
            <span v-for="b in playerSummary.badges" :key="b.id" :title="b.reason">🏅 {{ b.name }}</span>
          </div>
          <p v-else>尚未取得徽章，完成一次翻牌或問答即可累積。</p>
        </div>
      </section>

      <section v-if="page === 'leaderboard'" class="page-section">
        <div class="section-title">
          <h2>排行榜</h2>
          <p>由後端根據遊戲結果即時計算。</p>
        </div>

        <div class="leaderboard-tools glass-card">
          <div>
            <b>我的紀錄管理</b>
            <p>目前玩家：{{ displayPlayerName }}。此功能只會刪除自己的遊玩紀錄，不會清空全站資料。</p>
          </div>
          <button class="danger" @click="deleteMyResults">刪除我的紀錄</button>
        </div>

        <div class="table-wrap">
          <table>
            <thead><tr><th>排名</th><th>玩家</th><th>總點數</th><th>最高分</th><th>最佳正確率</th><th>次數</th></tr></thead>
            <tbody>
              <tr v-for="(row, idx) in leaderboard" :key="row.playerName">
                <td>#{{ idx + 1 }}</td><td>{{ row.playerName }}</td><td>{{ row.totalPoints }}</td><td>{{ row.bestScore }}</td><td>{{ row.accuracy }}%</td><td>{{ row.playCount }}</td>
              </tr>
              <tr v-if="!leaderboard.length"><td colspan="6">目前尚無資料，請先完成遊戲或產生 DEMO 資料。</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="page === 'admin'" class="page-section">
        <div class="section-title">
          <h2>後端測試面板</h2>
          <p>展示 API 連線、資料統計與 DEMO 資料建立，方便現場說明後端價值。資料刪除請至排行榜頁面刪除自己的紀錄。</p>
        </div>
        <div class="admin-actions glass-card">
          <button class="outline" @click="loadAll">重新讀取 API</button>

          <button class="primary" @click="seedDemo">產生 DEMO 資料</button>
        </div>
        <div class="stat-grid result-stats">
          <div class="stat-card"><strong>{{ systemStats.energyCount ?? '-' }}</strong><span>能源資料</span></div>
          <div class="stat-card"><strong>{{ systemStats.questionCount ?? '-' }}</strong><span>題庫數量</span></div>
          <div class="stat-card"><strong>{{ systemStats.resultCount ?? '-' }}</strong><span>結果筆數</span></div>
          
          <div class="stat-card"><strong>{{ storageLabel }}</strong><span>儲存模式</span></div>
        </div>
        <pre class="api-box">{{ JSON.stringify(apiDebug, null, 2) }}</pre>
      </section>
    </main>

    <div v-if="knowledgeModal" class="modal-mask" @click.self="knowledgeModal = null">
      <article class="knowledge-modal">
        <button class="close" @click="knowledgeModal = null">×</button>
        <span class="eyebrow">配對成功 +20 點</span>
        <h3>{{ knowledgeModal.icon }} {{ knowledgeModal.name }}</h3>
        <p>{{ knowledgeModal.principle }}</p>
        <div class="modal-grid">
          <div><b>重點優點</b><ul><li v-for="p in knowledgeModal.pros" :key="p">{{ p }}</li></ul></div>
          <div><b>主要限制</b><ul><li v-for="c in knowledgeModal.cons" :key="c">{{ c }}</li></ul></div>
        </div>
        <div class="case-box">{{ knowledgeModal.learnTip }}</div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';

const API_BASE = window.location.port === '5173' ? 'http://127.0.0.1:5000' : '';
const navItems = [
  { key: 'home', label: '首頁' },
  { key: 'atlas', label: '能源圖鑑' },
  { key: 'memory', label: '翻牌配對' },
  { key: 'quiz', label: '問答闖關' },
  { key: 'result', label: '學習成果' },
  { key: 'leaderboard', label: '排行榜' },
  { key: 'admin', label: '後端面板' }
];

const page = ref('home');
const menuOpen = ref(false);
const darkMode = ref(localStorage.getItem('qy_dark') === '1');
const demoMode = ref(false);
const playerName = ref(localStorage.getItem('qy_player') || 'Demo玩家');
const apiOk = ref(false);
const energies = ref([]);
const questions = ref([]);
const leaderboard = ref([]);
const playerSummary = ref({});
const systemStats = ref({});
const apiDebug = ref({});

const memoryCards = ref([]);
const memoryLock = ref(false);
const memoryMoves = ref(0);
const memoryMessage = ref('');
const knowledgeModal = ref(null);
const memoryStartedAt = ref(Date.now());
const memorySaved = ref(false);

const quizIndex = ref(0);
const answers = ref({});
const quizStartedAt = ref(Date.now());

watch(darkMode, v => localStorage.setItem('qy_dark', v ? '1' : '0'));
watch(playerName, v => localStorage.setItem('qy_player', v || 'Demo玩家'));

function go(target) {
  page.value = target;
  menuOpen.value = false;
  if (target === 'memory' && !memoryCards.value.length) resetMemory();
  if (target === 'quiz' && !questions.value.length) loadQuestions();
  if (target === 'result') refreshPlayer();
  if (target === 'leaderboard') loadLeaderboard();
  if (target === 'admin') loadStats();
}

async function startTask() {
  playerName.value = displayPlayerName.value;
  menuOpen.value = false;
  await Promise.all([resetMemory(), resetQuiz(), refreshPlayer()]);
  memoryMessage.value = `已為「${displayPlayerName.value}」重新開始翻牌與問答任務。`;
  page.value = 'memory';
}

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  const json = await res.json();
  if (!json.ok) throw new Error(json.message || 'API error');
  return json.data;
}

async function loadAll() {
  try {
    const health = await api('/api/health');
    apiOk.value = true;
    apiDebug.value = health;
    await Promise.all([loadEnergies(), loadQuestions(), loadLeaderboard(), refreshPlayer(), loadStats()]);
  } catch (err) {
    apiOk.value = false;
    apiDebug.value = { error: String(err) };
  }
}
async function loadEnergies() { energies.value = await api('/api/energies'); }
async function loadQuestions() { questions.value = await api('/api/questions'); if (demoMode.value) questions.value = [...questions.value].sort((a,b)=>a.id.localeCompare(b.id)); }
async function loadLeaderboard() { leaderboard.value = await api('/api/leaderboard'); }
async function refreshPlayer() { playerSummary.value = await api(`/api/player/${encodeURIComponent(playerName.value || 'Demo玩家')}`); }
async function loadStats() { systemStats.value = await api('/api/system-stats'); }

function shuffle(arr) {
  const a = [...arr];
  if (demoMode.value) return a;
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

async function resetMemory() {
  const cards = await api('/api/cards');
  memoryCards.value = shuffle(cards).map(c => ({ ...c, flipped: false, matched: false }));
  memoryMoves.value = 0;
  memoryMessage.value = '';
  memoryStartedAt.value = Date.now();
  memorySaved.value = false;
  memoryLock.value = false;
}

const flippedCards = computed(() => memoryCards.value.filter(c => c.flipped && !c.matched));
const matchedPairs = computed(() => new Set(memoryCards.value.filter(c => c.matched).map(c => c.pairId)).size);

async function flipCard(card) {
  if (memoryLock.value || card.flipped || card.matched) return;
  card.flipped = true;
  if (flippedCards.value.length === 2) {
    memoryMoves.value += 1;
    memoryLock.value = true;
    const [a, b] = flippedCards.value;
    if (a.pairId === b.pairId && a.cardType !== b.cardType) {
      setTimeout(async () => {
        a.matched = b.matched = true;
        knowledgeModal.value = a.energy;
        memoryMessage.value = `配對成功：${a.energy.name}`;
        memoryLock.value = false;
        if (matchedPairs.value === energies.value.length) await saveMemoryResult();
      }, 450);
    } else {
      setTimeout(() => {
        a.flipped = b.flipped = false;
        memoryMessage.value = '配對失敗，請再試一次。';
        memoryLock.value = false;
      }, 750);
    }
  }
}

async function saveMemoryResult() {
  if (memorySaved.value) {
    memoryMessage.value = '結果已經儲存到後端。';
    return;
  }
  const timeSpent = Math.round((Date.now() - memoryStartedAt.value) / 1000);
  const score = Math.max(60, 160 - memoryMoves.value * 5);
  try {
    await api('/api/results', {
      method: 'POST',
      body: JSON.stringify({ playerName: playerName.value, mode: 'memory', score, moves: memoryMoves.value, timeSpent, knowledgePoints: score, weakCategory: '待觀察' })
    });
    memorySaved.value = true;
    await loadLeaderboard();
    await refreshPlayer();
    await loadStats();
    memoryMessage.value = '全部配對完成，結果已儲存到後端。';
  } catch (err) {
    memorySaved.value = false;
    memoryMessage.value = `儲存失敗：${err.message}`;
  }
}

async function demoRevealNextPair() {
  if (!demoMode.value || memoryLock.value) return;
  if (!memoryCards.value.length) await resetMemory();
  memoryCards.value.forEach(c => { if (!c.matched) c.flipped = false; });
  const pairId = memoryCards.value.find(c => !c.matched)?.pairId;
  if (!pairId) {
    memoryMessage.value = '所有配對已完成。';
    return;
  }
  const pair = memoryCards.value.filter(c => c.pairId === pairId && !c.matched);
  if (pair.length < 2) return;
  pair.forEach(c => { c.flipped = true; c.matched = true; });
  memoryMoves.value += 1;
  knowledgeModal.value = pair[0].energy;
  memoryMessage.value = `DEMO 已配對：${pair[0].energy.name}`;
  if (matchedPairs.value === energies.value.length) await saveMemoryResult();
}

async function demoCompleteMemory() {
  if (!demoMode.value) return;
  if (!memoryCards.value.length) await resetMemory();
  memoryCards.value.forEach(c => { c.flipped = true; c.matched = true; });
  memoryMoves.value = Math.max(memoryMoves.value, energies.value.length);
  knowledgeModal.value = energies.value[0] || null;
  memoryMessage.value = 'DEMO 已一鍵完成全部翻牌配對。';
  await saveMemoryResult();
}

const currentQuestion = computed(() => questions.value[quizIndex.value]);
const answerState = computed(() => {
  const q = currentQuestion.value;
  return q ? (answers.value[q.id] || { choice: null, locked: false, correct: false, skipped: false }) : { choice: null };
});
const quizProgress = computed(() => questions.value.length ? Math.round(((quizIndex.value + 1) / questions.value.length) * 100) : 0);
const displayPlayerName = computed(() => (playerName.value || 'Demo玩家').trim() || 'Demo玩家');
const storageLabel = computed(() => systemStats.value.storage === 'local-json' ? '本機 JSON' : (systemStats.value.storage || '本機 JSON'));
const demoStatusText = computed(() => {
  if (page.value === 'memory') return '翻牌順序固定，並提供提示配對與一鍵完成。';
  if (page.value === 'quiz') return '題目順序固定，可快速選正解或完成闖關。';
  if (page.value === 'admin') return '可產生 DEMO 資料並展示後端 API、資料筆數與儲存模式。';
  return '可用快捷功能快速展示完整學習流程與後端資料流。';
});

async function resetQuiz() {
  answers.value = {};
  quizIndex.value = 0;
  quizStartedAt.value = Date.now();
  await loadQuestions();
}
function chooseAnswer(idx) { const q = currentQuestion.value; if (!q || answerState.value.locked) return; answers.value[q.id] = { choice: idx, locked: false, correct: false, skipped: false }; }
function answerClass(idx) { const s = answerState.value; if (s.choice !== idx) return ''; if (!s.locked) return 'selected'; return s.correct ? 'correct' : 'incorrect'; }
function submitAnswer() {
  const q = currentQuestion.value; if (!q) return;
  const s = answerState.value; if (s.choice === null || s.locked) return;
  answers.value[q.id] = { ...s, locked: true, correct: s.choice === q.answerIndex, skipped: false };
}
function skipQuestion() { const q = currentQuestion.value; if (!q || answerState.value.locked) return; answers.value[q.id] = { choice: null, locked: false, correct: false, skipped: true }; nextQuestion(); }
function nextQuestion() { if (quizIndex.value < questions.value.length - 1) quizIndex.value += 1; }
function prevQuestion() { if (quizIndex.value > 0) quizIndex.value -= 1; }
function demoAnswerCurrent() {
  if (!demoMode.value) return;
  const q = currentQuestion.value;
  if (!q) return;
  answers.value[q.id] = { choice: q.answerIndex, locked: true, correct: true, skipped: false };
}
async function demoCompleteQuiz() {
  if (!demoMode.value) return;
  questions.value.forEach(q => {
    answers.value[q.id] = { choice: q.answerIndex, locked: true, correct: true, skipped: false };
  });
  quizIndex.value = Math.max(0, questions.value.length - 1);
  await finishQuiz();
}

async function finishQuiz() {
  const rows = questions.value.map(q => ({ question: q, answer: answers.value[q.id] || null }));
  const correct = rows.filter(r => r.answer?.locked && r.answer.correct).length;
  const wrong = rows.filter(r => r.answer?.locked && !r.answer.correct).length;
  const skipped = rows.filter(r => r.answer?.skipped || !r.answer).length;
  const weakCounter = {};
  rows.forEach(r => { if (!r.answer?.correct) weakCounter[r.question.category] = (weakCounter[r.question.category] || 0) + 1; });
  const weakCategory = Object.keys(weakCounter).sort((a,b)=>weakCounter[b]-weakCounter[a])[0] || '待觀察';
  const score = correct * 20 + Math.max(0, 30 - wrong * 5) + (skipped ? 0 : 10);
  const timeSpent = Math.round((Date.now() - quizStartedAt.value) / 1000);
  await api('/api/results', {
    method: 'POST',
    body: JSON.stringify({ playerName: playerName.value, mode: 'quiz', score, correct, wrong, skipped, timeSpent, knowledgePoints: score, weakCategory, detail: { answers: rows.map(r => ({ id: r.question.id, answer: r.answer })) } })
  });
  await Promise.all([loadLeaderboard(), refreshPlayer(), loadStats()]);
  page.value = 'result';
}

async function seedDemo() { apiDebug.value = await api('/api/demo/seed', { method: 'POST' }); await loadAll(); }

async function deleteMyResults() {
  const name = displayPlayerName.value;
  if (!confirm(`確定要刪除「${name}」的遊玩紀錄嗎？\n此操作只會刪除目前玩家，不會清空其他人的資料。`)) return;
  apiDebug.value = await api(`/api/player/${encodeURIComponent(name)}/results`, { method: 'DELETE' });
  await loadAll();
  page.value = 'leaderboard';
}

onMounted(loadAll);
</script>
