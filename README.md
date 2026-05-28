# MiniQ SQL Compiler - Complete Documentation

---

## TABLE OF CONTENTS
1. Project Overview
2. Phase 3 Progress Report
3. Compiler Theory
4. Quick Start Guide
5. Project Structure
6. Features & Architecture

---

# PART 1: PROJECT OVERVIEW

## 1.1 Project Title
**MiniQ: Multi-Phase SQL Compiler with Semantic Analysis**

## 1.2 GitHub URL
https://github.com/supr24/MiniQ/tree/main

## 1.3 Project Description
MiniQ is a complete SQL compiler that converts simple English-like queries into standard SQL code. It implements all 5 compiler phases with real-time visualization: Lexer, Parser, AST, Semantic Analysis, and Code Generation. Users can write simple commands instead of complex SQL syntax. The project includes 20 example queries and works with 6 different data tables. Each compilation step is displayed in real-time, making it perfect for learning how compilers work.

---

# PART 2: PHASE 3 PROGRESS REPORT

## 2.1 Project Status
**Overall Status: 95% Complete - Ready for Deployment**

## 2.2 Project Abstract (200 words)

MiniQ is a SQL compiler that converts simple English-like queries into SQL code. Instead of learning complex SQL syntax, users write easy commands like "load students, filter age > 18, select name" and get SQL automatically.

The compiler implements all 5 real compiler phases visually: Lexer tokenizes code, Parser builds syntax tree, Semantic Analysis validates fields, and Code Generator creates SQL. Each phase displays in real-time.

Includes 20 examples and works with 6 data tables (students, sales, products, employees, orders, customers). Has Python backend and JavaScript frontend showing tokens, syntax tree, symbol table, and SQL side-by-side.

Perfect for learning SQL and understanding how compilers work in real industry applications.

## 2.3 Approach & Architecture

**Frontend:** HTML5, CSS3, JavaScript (dark theme UI)
**Backend:** Python Flask with REST API
**Communication:** Frontend sends code → Backend compiles → Returns JSON with all phases
**Databases:** 6 tables (students, sales, products, employees, orders, customers)
**Features:** Real-time phase display, symbol table validation, error handling
