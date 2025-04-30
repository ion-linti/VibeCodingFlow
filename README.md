[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

# VibeCodingFlow — AI IDE  
**Say your idea. Get the code. Feel the flow.**

> Turn natural language into full project code — instantly.

---

## 📋 Table of Contents

1. [Status](#status)  
2. [Philosophy](#philosophy)  
3. [Features](#features)  
4. [Installation](#installation)  
5. [Usage](#usage)  
6. [Configuration](#configuration)  
7. [Architecture](#architecture)  
8. [Roadmap](#roadmap)  
9. [Known Issues](#known-issues)  
10. [Contributing](#contributing)  
11. [Support](#support)  
12. [License](#license)  

---

## ⚠️ Status

**Early MVP (alpha)** — still buggy, but already usable.  
Expect rough edges; feedback is welcome.  

---

## 💡 Philosophy

**Dopamine-Driven Development**  
Modern tools sacrifice creativity for complexity.  
**VibeCodingFlow** reimagines programming as a dialogue between human intention and machine execution:

- Not just autocomplete — it’s **flow**.  
- Not about typing faster — about **thinking clearer**.  

> *Programming should feel like creation, not configuration.*  
> *Bring dopamine back to development.*  

---

## 🚀 Features

### 🔨 Create a new project  
```bash
vibe new <project_name> "<description>"
```
Generates a complete directory with structure and boilerplate.

### 📂 Navigate to a project  
```bash
vibe go <project_name>
# → cd ~/path/to/<project_name>
```

### 🛠 Incremental updates  
```bash
vibe do "<change request>"
```
Applies targeted modifications; only changed files are regenerated. History saved in SQLite.

---

## 📦 Installation

```bash
git clone https://github.com/ion-linti/VibeCodingFlow.git
cd VibeCodingFlow
pip install -r requirements.txt
pip install -e . 
```

---

## 🔧 Configuration

### OpenAI API Key  
```bash
export OPENAI_API_KEY=your_api_key      # macOS/Linux
set OPENAI_API_KEY=your_api_key         # Windows
```

### Windows line endings  
```bash
git config --global core.autocrlf true
```
Or add a `.gitattributes`:
```
* text=auto
```

---

## 📦 Usage Examples

```bash
# 1. Create a business landing page
vibe new business_site "beautiful landing page for a company"

# 2. Jump into it
vibe go business_site

# 3. Add an About page
vibe do "add About page with team photos and bios"

# 4. Add a contact form
vibe do "add contact form with email validation"

```

👉 [Watch a quick demo GIF](SOON)

---

## 🧠 Architecture

```
Prompt ─▶ GPT-4o ─▶ Spec JSON ─▶ GPT-4o (Code Gen) ─▶ File Writer
                           │
                           └─▶ SQLite Memory (project history & state)
```

---

## 🛣️ Roadmap

- **RAG integration** (retrieve doc snippets for specs)  
- **Plugin system** (custom generators & verifiers)  
- **GUI** (Electron/Tauri + Monaco editor)  
- **Formal verification** (symbolic checks via Prolog/Z3)  
- **`vibe server`** (local dev server)  
- **Test runner** (`vibe test` with pytest/vitest)  
- **Voice request** (in GUI)

---

## ❗ Known Issues

- Prompt parsing may fail on complex JSON specs  
- Large projects can be slow to regenerate  
- Windows support is untested beyond CRLF handling  

Please open an issue if you hit bugs or performance bottlenecks!

---

## 🤝 Contributing

Contributions welcome!  
If you want to help with testing, plugins, or reasoning modules — fork and PR.  
Start a `tests/` folder with `pytest` if you'd like.

---

## 💬 Support

- **Issues**: https://github.com/ion-linti/VibeCodingFlow/issues  

---

## 📄 License

MIT © 2025 [Ion Linti](https://github.com/ion-linti)