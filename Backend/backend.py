# ============================================
# MINIQ SQL COMPILER - BACKEND - Urvashi Kashyap
# ============================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# ============================================
# PHASE 1: LEXER - Urvashi Kashyap
# ============================================
class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.keywords = ['load', 'filter', 'select', 'sort', 'by', 'group', 
                        'aggregate', 'limit', 'asc', 'desc', 'as', 'and', 'or',
                        'sum', 'count', 'avg', 'min', 'max']
    
    def tokenize(self):
        lines = self.code.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            i = 0
            while i < len(line):
                if line[i].isspace():
                    i += 1
                elif line[i] in '(),':
                    self.tokens.append({
                        'type': 'SYMBOL',
                        'value': line[i],
                        'lineNum': line_num
                    })
                    i += 1
                elif i + 1 < len(line) and line[i:i+2] in ['>=', '<=', '!=']:
                    self.tokens.append({
                        'type': 'OPERATOR',
                        'value': line[i:i+2],
                        'lineNum': line_num
                    })
                    i += 2
                elif line[i] in '<>=':
                    self.tokens.append({
                        'type': 'OPERATOR',
                        'value': line[i],
                        'lineNum': line_num
                    })
                    i += 1
                elif line[i].isdigit():
                    j = i
                    while j < len(line) and line[j].isdigit():
                        j += 1
                    self.tokens.append({
                        'type': 'NUMBER',
                        'value': int(line[i:j]),
                        'lineNum': line_num
                    })
                    i = j
                elif line[i] == '"':
                    j = i + 1
                    while j < len(line) and line[j] != '"':
                        j += 1
                    self.tokens.append({
                        'type': 'STRING',
                        'value': line[i+1:j],
                        'lineNum': line_num
                    })
                    i = j + 1
                elif line[i].isalpha() or line[i] == '_':
                    j = i
                    while j < len(line) and (line[j].isalnum() or line[j] == '_'):
                        j += 1
                    word = line[i:j]
                    if word.lower() in self.keywords:
                        self.tokens.append({
                            'type': 'KEYWORD',
                            'value': word.lower(),
                            'lineNum': line_num
                        })
                    else:
                        self.tokens.append({
                            'type': 'IDENTIFIER',
                            'value': word,
                            'lineNum': line_num
                        })
                    i = j
                elif line[i] == '*':
                    self.tokens.append({
                        'type': 'WILDCARD',
                        'value': '*',
                        'lineNum': line_num
                    })
                    i += 1
                else:
                    i += 1
        
        return self.tokens

# ============================================
# PHASE 2 & 3: PARSER & AST - Ridham Singh
# ============================================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
    
    def parse(self):
        ast = {'type': 'Program', 'statements': []}
        
        while self.pos < len(self.tokens):
            stmt = self.parse_statement()
            if stmt:
                ast['statements'].append(stmt)
        
        return ast
    
    def parse_statement(self):
        token = self.peek()
        if not token:
            return None
        
        if token['value'] == 'load':
            return self.parse_load()
        elif token['value'] == 'filter':
            return self.parse_filter()
        elif token['value'] == 'select':
            return self.parse_select()
        elif token['value'] == 'sort':
            return self.parse_sort()
        elif token['value'] == 'group':
            return self.parse_group()
        elif token['value'] == 'aggregate':
            return self.parse_aggregate()
        elif token['value'] == 'limit':
            return self.parse_limit()
        else:
            self.pos += 1
            return None
    
    def parse_load(self):
        self.consume('KEYWORD', 'load')
        table = self.consume('IDENTIFIER')
        return {'type': 'LoadStatement', 'table': table['value']} if table else None
    
    def parse_filter(self):
        self.consume('KEYWORD', 'filter')
        condition = self.parse_condition()
        return {'type': 'FilterStatement', 'condition': condition} if condition else None
    
    def parse_select(self):
        self.consume('KEYWORD', 'select')
        fields = []
        
        if self.peek() and self.peek()['type'] == 'WILDCARD':
            self.pos += 1
            fields.append('*')
        else:
            field = self.consume('IDENTIFIER')
            if field:
                fields.append(field['value'])
                while self.peek() and self.peek().get('value') == ',':
                    self.pos += 1
                    f = self.consume('IDENTIFIER')
                    if f:
                        fields.append(f['value'])
        
        return {'type': 'SelectStatement', 'fields': fields}
    
    def parse_sort(self):
        self.consume('KEYWORD', 'sort')
        self.consume('KEYWORD', 'by')
        field = self.consume('IDENTIFIER')
        
        direction = 'asc'
        if self.peek() and self.peek()['value'] in ['asc', 'desc']:
            direction = self.consume('KEYWORD')['value']
        
        return {'type': 'SortStatement', 'field': field['value'], 'direction': direction} if field else None
    
    def parse_group(self):
        self.consume('KEYWORD', 'group')
        self.consume('KEYWORD', 'by')
        field = self.consume('IDENTIFIER')
        return {'type': 'GroupStatement', 'field': field['value']} if field else None
    
    def parse_aggregate(self):
        self.consume('KEYWORD', 'aggregate')
        functions = []
        
        func = self.parse_agg_func()
        if func:
            functions.append(func)
        
        while self.peek() and self.peek().get('value') == ',':
            self.pos += 1
            f = self.parse_agg_func()
            if f:
                functions.append(f)
        
        return {'type': 'AggregateStatement', 'functions': functions}
    
    def parse_agg_func(self):
        func_name = self.consume('KEYWORD')
        if not func_name:
            func_name = self.consume('IDENTIFIER')
        if not func_name:
            return None
        
        if not (self.peek() and self.peek().get('value') == '('):
            return None
        self.pos += 1
        
        field = '*'
        if self.peek() and self.peek()['type'] == 'WILDCARD':
            self.pos += 1
        elif self.peek() and self.peek()['type'] == 'IDENTIFIER':
            field = self.consume('IDENTIFIER')['value']
        
        if self.peek() and self.peek().get('value') == ')':
            self.pos += 1
        
        alias = None
        if self.peek() and self.peek().get('value') == 'as':
            self.pos += 1
            a = self.consume('IDENTIFIER')
            if a:
                alias = a['value']
        
        return {'function': func_name['value'], 'field': field, 'alias': alias}
    
    def parse_limit(self):
        self.consume('KEYWORD', 'limit')
        count = self.consume('NUMBER')
        return {'type': 'LimitStatement', 'count': count['value']} if count else None
    
    def parse_condition(self):
        field = self.consume('IDENTIFIER')
        if not field:
            return None
        op = self.consume('OPERATOR')
        if not op:
            return None
        
        value = None
        if self.peek() and self.peek()['type'] == 'NUMBER':
            value = self.consume('NUMBER')['value']
        elif self.peek() and self.peek()['type'] == 'STRING':
            value = self.consume('STRING')['value']
        elif self.peek() and self.peek()['type'] == 'IDENTIFIER':
            value = self.consume('IDENTIFIER')['value']
        
        return {'field': field['value'], 'operator': op['value'], 'value': value}
    
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def consume(self, typ=None, val=None):
        token = self.peek()
        if not token:
            return None
        if typ and token['type'] != typ:
            return None
        if val and token['value'] != val:
            return None
        self.pos += 1
        return token

# ============================================
# PHASE 4: SEMANTIC ANALYZER - Supriya Rawat
# ============================================
class SemanticAnalyzer:
    SCHEMAS = {
        'students': ['id', 'name', 'age', 'marks', 'department', 'email', 'gpa'],
        'sales': ['id', 'product', 'category', 'revenue', 'quantity', 'date'],
        'products': ['id', 'name', 'price', 'quantity', 'category', 'supplier'],
        'employees': ['id', 'name', 'department', 'salary', 'email', 'joining_date'],
        'orders': ['id', 'customer', 'amount', 'date', 'status', 'product'],
        'customers': ['id', 'name', 'email', 'city', 'phone', 'country']
    }
    
    def __init__(self, ast):
        self.ast = ast
        self.errors = []
        self.symbol_table = {'tables': {}, 'fields': {}, 'aggregates': []}
        self.current_table = None
    
    def analyze(self):
        # First pass: load table
        for stmt in self.ast.get('statements', []):
            if stmt['type'] == 'LoadStatement':
                self.current_table = stmt['table']
                self.symbol_table['tables'][stmt['table']] = {
                    'name': stmt['table'],
                    'fields': self.SCHEMAS.get(stmt['table'], ['id', 'name', 'value'])
                }
        
        # Second pass: validate
        for stmt in self.ast.get('statements', []):
            if stmt['type'] == 'FilterStatement':
                self.validate_filter(stmt)
            elif stmt['type'] == 'SelectStatement':
                self.validate_select(stmt)
            elif stmt['type'] == 'AggregateStatement':
                for f in stmt.get('functions', []):
                    self.symbol_table['aggregates'].append(f)
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'symbolTable': self.symbol_table
        }
    
    def validate_filter(self, stmt):
        if not self.current_table:
            self.errors.append('FILTER: No table loaded')
            return
        fields = self.SCHEMAS.get(self.current_table, [])
        field = stmt['condition']['field']
        if field not in fields:
            self.errors.append(f"Field '{field}' not found")
    
    def validate_select(self, stmt):
        if not self.current_table:
            self.errors.append('SELECT: No table loaded')
            return
        fields = self.SCHEMAS.get(self.current_table, [])
        for f in stmt['fields']:
            if f != '*' and f not in fields:
                self.errors.append(f"Field '{f}' not found")

# ============================================
# PHASE 5: CODE GENERATOR - Ridham Singh
# ============================================
class CodeGen:
    def __init__(self, ast):
        self.ast = ast
        self.select_fields = ['*']
        self.from_table = ''
        self.where = ''
        self.group_by = ''
        self.order_by = ''
        self.limit = ''
        self.aggregates = []
    
    def generate(self):
        for stmt in self.ast.get('statements', []):
            if stmt['type'] == 'LoadStatement':
                self.from_table = stmt['table']
            elif stmt['type'] == 'SelectStatement':
                self.select_fields = stmt['fields']
            elif stmt['type'] == 'FilterStatement':
                cond = stmt['condition']
                val = f"'{cond['value']}'" if isinstance(cond['value'], str) else cond['value']
                self.where = f"WHERE {cond['field']} {cond['operator']} {val}"
            elif stmt['type'] == 'SortStatement':
                self.order_by = f"ORDER BY {stmt['field']} {stmt['direction'].upper()}"
            elif stmt['type'] == 'GroupStatement':
                self.group_by = f"GROUP BY {stmt['field']}"
            elif stmt['type'] == 'LimitStatement':
                self.limit = f"LIMIT {stmt['count']}"
            elif stmt['type'] == 'AggregateStatement':
                for f in stmt['functions']:
                    alias = f" AS {f['alias']}" if f['alias'] else ""
                    self.aggregates.append(f"{f['function'].upper()}({f['field']}){alias}")
        
        select = f"SELECT {', '.join(self.aggregates) if self.aggregates else ', '.join(self.select_fields)}"
        query = '\n'.join(filter(None, [select, f"FROM {self.from_table}", self.where, self.group_by, self.order_by, self.limit]))
        return query + ';'

# ============================================
# MAIN COMPILER - Urvashi Kashyap
# ============================================
class Compiler:
    def compile(self, code):
        result = {
            'lexer': None,
            'ast': None,
            'semantic': None,
            'sql': None,
            'errors': []
        }
        
        try:
            lexer = Lexer(code)
            result['lexer'] = lexer.tokenize()
            
            parser = Parser(result['lexer'])
            result['ast'] = parser.parse()
            
            semantic = SemanticAnalyzer(result['ast'])
            result['semantic'] = semantic.analyze()
            
            if not result['semantic']['valid']:
                result['errors'] = result['semantic']['errors']
                return result
            
            gen = CodeGen(result['ast'])
            result['sql'] = gen.generate()
            
        except Exception as e:
            result['errors'] = [f"Error: {str(e)}"]
        
        return result


# ============================================
# FLASK ROUTES - Supriya Rawat
# ============================================
@app.route('/api/compile', methods=['POST'])
def compile():
    data = request.json
    code = data.get('code', '')
    
    compiler = Compiler()
    result = compiler.compile(code)
    
    return jsonify(result)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Backend running'})
