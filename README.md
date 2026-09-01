
# 🤖 Auto-Santillana Solver (Early Beta)

> ⚠️ **DISCLAIMER: EARLY BETA STAGE**  
> This project is currently in an **experimental/early beta** state. It is actively under development, and breaking changes may occur. Features, continuous scrolling logic, and API fallback configurations are subject to rapid iteration.

An autonomous computer vision bot written in Python that leverages **Gemini 3.6 Flash** (Visual Language Model) to dynamically navigate, reason, and solve interactive educational exercises (checkboxes, drag-and-drop matching, and complex word searches) in a Linux (X11) environment.

---

## 🌟 Key Features

* **Multimodal Vision Engine:** Real-time UI inspection and spatial reasoning powered by `gemini-3.6-flash`.
* **Complex UI Interaction Handling:**
  * **Checkboxes & Buttons:** Single-click UI element targeting.
  * **Concept Matching:** Dynamic drag-and-drop line plotting.
  * **Word Search (Sopa de Letras):** Grid OCR, diagonal/vertical/horizontal pattern recognition, and precise click-and-drag coordinate extraction.
* **Low-Level Native Control:** Direct mouse and event simulation via `pynput` on Linux X11.
* **API Resilience & Recovery:** Exponential backoff mechanism for API congestion (`503 / 429` errors) with automatic fallback to `gemini-3.1-pro-preview`.

---

## 🛠️ Tech Stack & Environment

* **Language:** Python 3.12+
* **Vision Model:** Google Gemini 3.6 Flash & Gemini 3.1 Pro Preview
* **Platform:** Linux (Garuda Linux / KDE Plasma on X11)
* **Libraries:** `pynput`, `Pillow`, `OpenCV`, `google-genai`
* **AI Collaboration:** Built with Google Antigravity Agent

---

## 📦 Quick Start

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/Santillana_bot.git](https://github.com/YOUR_USERNAME/Santillana_bot.git)
cd Santillana_bot

```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

### 3. Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY="your_gemini_api_key_here"

```

### 4. Run the Solver

```bash
python main.py

```

---

## 🛣️ Roadmap

* [x] Checkbox and button detection
* [x] Drag-and-drop matching resolution
* [x] Matrix OCR & Word Search solver logic
* [x] API fallback and exponential backoff strategy
* [ ] Finite State Machine (FSM) for full autonomy
* [ ] Auto-scrolling and viewport detection
* [ ] Multi-lesson progression and navigation loop

---
