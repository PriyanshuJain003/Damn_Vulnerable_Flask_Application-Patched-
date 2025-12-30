# Damn Vulnerable Flask App (Patched Edition)

A partially secured version of the Damn Vulnerable Flask Shop App built with **Python (Flask)** and **SQLite** for educational and CTF purposes.

This edition demonstrates how common web vulnerabilities are mitigated using secure coding practices, while intentionally retaining specific flaws (XSS and Insecure Deserialization) for focused learning.

---

## Table of Contents

- Features
- Vulnerabilities Demonstrated
- Security Improvements
- Prerequisites
- Installation
- Usage
- Remaining Intentional Vulnerabilities
- Project Structure
- Educational Goals
- Important Security Notes
- License

---

## Features

- Parameterized SQL queries
- Session hardening and expiration
- Role-based access control
- IDOR mitigation
- Retained XSS and deserialization flaws for labs
- Secure-by-default routing

---

## Vulnerabilities Demonstrated

### Intentionally Retained

- Insecure Deserialization (pickle-based RCE)

### Mitigated

- SQL Injection
- Broken Authentication
- Broken Access Control
- Insecure Direct Object References (IDOR)

---

## Security Improvements

- Prepared statements for all SQL queries
- Session clearing and regeneration on login
- Explicit admin role checks
- Ownership enforcement for profiles and orders
- Limited session lifetime (30 minutes)

---

## Prerequisites

- Python 3.9+
- pip
- Local or lab environment only

---

## Installation

```bash
git clone https://github.com/yourusername/damn-vulnerable-flask-shop.git
cd damn-vulnerable-flask-shop
pip install flask
```

---

## Usage

```bash
cd patched exp
python app.py
```

Access:
- http://127.0.0.1:5000/login
- http://127.0.0.1:5000/admin

---

## Remaining Intentional Vulnerabilities

### Reflected XSS

User input from the search parameter is reflected into the customers template without output encoding.

### Insecure Deserialization

The /hackme endpoint deserializes user-supplied pickle data, allowing arbitrary code execution.

---

## Project Structure

```
.
├── app.py
├── database.py
├── exploit.py
├── templates/
├── static/
└── shop.db
```

---

## Educational Goals

- Demonstrate real-world vulnerability mitigation
- Teach secure session and access control design
- Enable focused exploitation labs for XSS and RCE
- Compare insecure vs patched implementations

---

## Important Security Notes

⚠️ WARNING

This application is still intentionally vulnerable.
Do NOT deploy to production.
Use only in controlled environments.

---

## License

Educational use only.
