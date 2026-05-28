// ============================================
// MINIQ FRONTEND - FIXED AST & RULES - Urvashi Kashyap
// ============================================

console.log('🔄 Initializing app.js...');

const miniqEditor = document.getElementById('miniqEditor');
const exampleSelect = document.getElementById('exampleSelect');
const runBtn = document.getElementById('runBtn');
const clearBtn = document.getElementById('clearBtn');
const rulesBtn = document.getElementById('rulesBtn');

const lexerOutput = document.getElementById('lexerOutput');
const parserOutput = document.getElementById('parserOutput');
const symbolTableOutput = document.getElementById('symbolTableOutput');
const sqlOutput = document.getElementById('sqlOutput');
const rulesPanel = document.getElementById('rulesPanel');

const BACKEND_URL = 'http://localhost:5000';

// ========== RULES TOGGLE ========== -- Urvashi Kashyap
function toggleRules() {
    rulesPanel.classList.toggle('show');
}

rulesBtn.addEventListener('click', toggleRules);

// Close rules when clicking outside
rulesPanel.addEventListener('click', (e) => {
    if (e.target === rulesPanel) {
        toggleRules();
    }
});

// ========== EXAMPLE SELECTION ========== -- Urvashi Kashyap
exampleSelect.addEventListener('change', function(e) {
    if (e.target.value && examples[e.target.value]) {
        miniqEditor.value = examples[e.target.value].code;
        setTimeout(() => compileCode(), 500);
    }
});

runBtn.addEventListener('click', compileCode);

clearBtn.addEventListener('click', () => {
    miniqEditor.value = '';
    exampleSelect.value = '';
    resetOutputs();
});

// ========== MAIN COMPILE ========== -- Urvashi Kashyap
async function compileCode() {
    const code = miniqEditor.value.trim();
    
    if (!code) {
        sqlOutput.innerHTML = '<pre style="color: #ffb300;">⚠️ Write code or select example</pre>';
        return;
    }
    
    setLoading(true);
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/compile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const result = await response.json();
        displayResults(result);
        
    } catch (error) {
        const msg = error.message.includes('Failed to fetch')
            ? '❌ BACKEND NOT RUNNING\n\nRun: python backend.py'
            : `❌ Error: ${error.message}`;
        
        sqlOutput.innerHTML = `<pre style="color: #ff5252;">${msg}</pre>`;
        resetOutputs();
    } finally {
        setLoading(false);
    }
}
