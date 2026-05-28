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

// ========== DISPLAY RESULTS ========== -- Ridham Singh
function displayResults(result) {
    // Phase 1: Lexer
    if (result.lexer && result.lexer.length > 0) {
        const tokens = result.lexer.map(t => `[${t.type}] ${t.value}`).join('\n');
        lexerOutput.innerHTML = `<pre>${tokens}</pre>`;
    } else {
        lexerOutput.innerHTML = '<div class="empty-placeholder">No tokens</div>';
    }
    
    // Phase 2: Parser & AST (PROPER TREE)
    if (result.ast && result.ast.statements) {
        parserOutput.innerHTML = buildASTTree(result.ast);
    } else {
        parserOutput.innerHTML = '<div class="empty-placeholder">No AST</div>';
    }
    
    // Phase 3: Symbol Table
    if (result.semantic && result.semantic.symbolTable) {
        symbolTableOutput.innerHTML = `<pre>${formatSymbolTable(result.semantic.symbolTable)}</pre>`;
    } else {
        symbolTableOutput.innerHTML = '<div class="empty-placeholder">No symbol table</div>';
    }
    
    // Phase 4: SQL
    if (result.errors && result.errors.length > 0) {
        sqlOutput.innerHTML = `<pre style="color: #ff5252;">❌ ERRORS:\n${result.errors.join('\n')}</pre>`;
    } else if (result.sql) {
        sqlOutput.innerHTML = `<pre>${result.sql}</pre>`;
    } else {
        sqlOutput.innerHTML = '<div class="empty-placeholder">No SQL</div>';
    }
}

// ========== BUILD AST TREE (PROPER TREE STRUCTURE) ========== -- Ridham Singh
function buildASTTree(ast) {
    let html = '<pre>';
    html += '📦 <span class="ast-keyword">Program</span>\n';
    
    if (ast.statements && ast.statements.length > 0) {
        ast.statements.forEach((stmt, idx) => {
            const isLast = idx === ast.statements.length - 1;
            const prefix = isLast ? '└─ ' : '├─ ';
            const childPrefix = isLast ? '   ' : '│  ';
            
            html += prefix;
            
            if (stmt.type === 'LoadStatement') {
                html += `<span class="ast-keyword">LOAD</span> `;
                html += `<span class="ast-value">${stmt.table}</span>\n`;
            }
            else if (stmt.type === 'FilterStatement') {
                html += `<span class="ast-keyword">FILTER</span>\n`;
                html += childPrefix + `├─ field: <span class="ast-value">${stmt.condition.field}</span>\n`;
                html += childPrefix + `├─ operator: <span class="ast-value">${stmt.condition.operator}</span>\n`;
                html += childPrefix + `└─ value: <span class="ast-value">${stmt.condition.value}</span>\n`;
            }
            else if (stmt.type === 'SelectStatement') {
                html += `<span class="ast-keyword">SELECT</span> `;
                html += `<span class="ast-value">[${stmt.fields.join(', ')}]</span>\n`;
            }
            else if (stmt.type === 'SortStatement') {
                html += `<span class="ast-keyword">SORT BY</span> `;
                html += `<span class="ast-value">${stmt.field}</span> `;
                html += `<span class="ast-value">${stmt.direction.toUpperCase()}</span>\n`;
            }
            else if (stmt.type === 'GroupStatement') {
                html += `<span class="ast-keyword">GROUP BY</span> `;
                html += `<span class="ast-value">${stmt.field}</span>\n`;
            }
            else if (stmt.type === 'AggregateStatement') {
                html += `<span class="ast-keyword">AGGREGATE</span>\n`;
                stmt.functions.forEach((func, fIdx) => {
                    const fIsLast = fIdx === stmt.functions.length - 1;
                    const fPrefix = fIsLast ? '└─ ' : '├─ ';
                    html += childPrefix + fPrefix;
                    html += `<span class="ast-value">${func.function}(${func.field})</span>`;
                    if (func.alias) {
                        html += ` <span class="ast-keyword">AS</span> <span class="ast-value">${func.alias}</span>`;
                    }
                    html += '\n';
                });
            }
             else if (stmt.type === 'LimitStatement') {
                html += `<span class="ast-keyword">LIMIT</span> `;
                html += `<span class="ast-value">${stmt.count}</span>\n`;
            }
        });
    }
    
    html += '</pre>';
    return html;
}

// ========== SYMBOL TABLE FORMATTING ========== -- Supriya Rawat
function formatSymbolTable(st) {
    let table = '═══════════════════════════════════\n';
    table += '       SYMBOL TABLE\n';
    table += '═══════════════════════════════════\n\n';
    
    if (st.tables && Object.keys(st.tables).length > 0) {
        table += '📦 TABLES LOADED:\n';
        table += '───────────────────────────────────\n';
        Object.keys(st.tables).forEach(name => {
            table += `  ${name}\n`;
            table += `    Fields: [${st.tables[name].fields.join(', ')}]\n`;
        });
        table += '\n';
    }
    
    if (st.fields && Object.keys(st.fields).length > 0) {
        table += '📋 FIELDS REFERENCED:\n';
        table += '───────────────────────────────────\n';
        Object.keys(st.fields).forEach(name => {
            table += `  ${name}\n`;
        });
        table += '\n';
    }
    
    if (st.aggregates && st.aggregates.length > 0) {
        table += '∑ AGGREGATE FUNCTIONS:\n';
        table += '───────────────────────────────────\n';
        st.aggregates.forEach(agg => {
            table += `  ${agg.function.toUpperCase()}(${agg.field})`;
            if (agg.alias) table += ` AS ${agg.alias}`;
            table += '\n';
        });
    }
    
    table += '═══════════════════════════════════';
    return table;
}

// ========== HELPERS ========== --Supriya Rawat
function setLoading(isLoading) {
    if (isLoading) {
        lexerOutput.innerHTML = '<div class="empty-placeholder">⏳ Compiling...</div>';
        parserOutput.innerHTML = '<div class="empty-placeholder">⏳ Compiling...</div>';
        symbolTableOutput.innerHTML = '<div class="empty-placeholder">⏳ Compiling...</div>';
        sqlOutput.innerHTML = '<div class="empty-placeholder">⏳ Compiling...</div>';
    }
}

function resetOutputs() {
    lexerOutput.innerHTML = '<div class="empty-placeholder">Tokens here</div>';
    parserOutput.innerHTML = '<div class="empty-placeholder">AST here</div>';
    symbolTableOutput.innerHTML = '<div class="empty-placeholder">Symbol table here</div>';
    sqlOutput.innerHTML = '<div class="empty-placeholder">SQL here</div>';
}

window.addEventListener('load', () => {
    if (!examples || Object.keys(examples).length === 0) {
        sqlOutput.innerHTML = '<pre style="color: #ff5252;">ERROR: examples.js not loaded</pre>';
    }
});

console.log('✓ App loaded successfully');
