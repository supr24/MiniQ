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
