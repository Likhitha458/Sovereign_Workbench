# SOVEREIGN AI WORKBENCH — On-Premise Agentic AI Platform

> **A self-hosted, offline, agentic AI workbench for confidential industrial, government, and PSU work.**

Sovereign AI Workbench provides a ChatGPT / Claude-style interface for on-premise industrial environments. It runs 100% locally with open-weight models via Ollama, local document RAG (ChromaDB), multimodal vision understanding, intelligent auto-routing, Docker code sandbox execution, and automated multi-step hero workflows producing official Word (.docx) approval notes with Human-in-the-Loop review.

---

## 🛡️ Sovereignty & Security Architecture

- **0 External AI APIs**: Zero connections to OpenAI, Anthropic, Gemini, or cloud LLMs.
- **100% Local Inference**: Powered by local Ollama model runtime.
- **Local RAG & Vector Store**: Local ChromaDB vector database with page-level citation mapping.
- **Local OCR**: PyMuPDF & Tesseract local optical character recognition.
- **Isolated Code Sandbox**: Docker execution container with zero network access and resource constraints.
- **Complete Audit Trail**: SQLite audit ledger recording timestamped user actions, model selections, and tool calls.

```
+-----------------------------------------------------------------------------------+
|                              BROWSER (React 18 + Vite)                            |
|             Figma Kit UI: Charcoal #142626, Teal #087F72, Inter & IBM Plex Mono   |
+-----------------------------------------------------------------------------------+
                                         │
                                   HTTP / REST
                                         ▼
+-----------------------------------------------------------------------------------+
|                              FASTAPI BACKEND (Python 3.12)                        |
|                                                                                   |
|  +--------------------+   +-------------------+   +----------------------------+  |
|  |    ModelRouter     |   |    Local RAG      |   |       Hero Agent           |  |
|  |  Auto → Qwen3      |   |  ChromaDB Store   |   | Inspection → Approval Note |  |
|  |  Auto → Qwen2.5-VL |   | SentenceEmbedder  |   |  python-docx Generator     |  |
|  |  Auto → Qwen3-Coder|   |  Source Citations |   |   Human-in-the-Loop Review |  |
|  +--------------------+   +-------------------+   +----------------------------+  |
|                                                                                   |
|  +-----------------------------------+   +-------------------------------------+  |
|  |        Docker Code Sandbox        |   |         SQLite Audit Ledger         |  |
|  | Isolated Container (--network none)|   | User Actions, Model Log, Security   |  |
|  +-----------------------------------+   +-------------------------------------+  |
+-----------------------------------------------------------------------------------+
                                         │
                                 Local API (11434)
                                         ▼
+-----------------------------------------------------------------------------------+
|                                OLLAMA MODEL RUNTIME                               |
|        Qwen3 (General)   |   Qwen2.5-VL (Vision)   |   Qwen3-Coder (Coding)     |
+-----------------------------------------------------------------------------------+
```

---

## 🚀 Quick Setup & Installation

### Prerequisites
1. **Python**: 3.11+
2. **Node.js**: v18+ & npm
3. **Ollama**: Download from [ollama.com](https://ollama.com)
4. **Docker Desktop** (Optional, for isolated code sandbox execution)

---

### Step 1: Install Ollama & Pull Open-Weight Models
Run the following commands in your terminal to download the required open-weight models:

```bash
# Pull General reasoning model
ollama pull qwen3

# Pull Multimodal vision model
ollama pull qwen2.5-vl

# Pull Coding & math model
ollama pull qwen3-coder
```

---

### Step 2: Set Up Backend Environment

```bash
# Navigate to project root
cd "Sovereign AI Workbench"

# Create virtual environment (optional)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3: Set Up Frontend Environment

```bash
# Navigate to frontend folder
cd frontend

# Install node packages
npm install
```

---

## 💻 Running the Application

### 1. Start Ollama Service
Ensure Ollama is running on your system (`http://localhost:11434`).

### 2. Start Backend Server
In terminal 1 (project root):
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
Backend API will be live at `http://localhost:8000`.

### 3. Start React Frontend
In terminal 2 (`frontend/` folder):
```bash
npm run dev
```
Open your browser to `http://localhost:5173`.

---

## 🎯 Hackathon Demonstration Flow

### DEMO 1 — General AI & Local RAG (`Auto → Qwen3`)
1. Click **Chats** in the sidebar.
2. Select starter card **"Ask your documents"** or type:
   > *"What are the mandatory inspection interval regulations for pressure valves?"*
3. Notice the model badge displays `Auto → Qwen3`.
4. Observe the response grounded in `Safety_Regulation_2025.pdf — Page 14` with exact source page citations!

---

### DEMO 2 — Multimodal Vision (`Auto → Qwen2.5-VL`)
1. Click **Upload image** in the chat input bar.
2. Attach an inspection photograph or equipment drawing (`scanned_inspection_record.jpg`).
3. Type:
   > *"Inspect this equipment image and identify visible component abnormalities."*
4. Notice the model auto-router automatically selects `Auto → Qwen2.5-VL`.
5. View component identification and surface oxidation observations.

---

### DEMO 3 — Coding Agent & Docker Sandbox (`Auto → Qwen3-Coder`)
1. Select starter card **"Build a calculation"** or type:
   > *"Write Python code to calculate pressure drop using Darcy-Weisbach equation."*
2. Notice the model selector displays `Auto → Qwen3-Coder`.
3. Click the **Run Code** button in the generated code block.
4. Watch the code execute inside the isolated Docker sandbox with stdout output displayed.

---

### DEMO 4 — HERO AGENT: Inspection Report → Approval Note (`Agent Tasks`)
1. Click **Agent Tasks** in the sidebar.
2. View the pre-loaded input documents (`Inspection_Report_Unit04.pdf`, `Safety_Regulation_2025.pdf`, `Maintenance_SOP.pdf`).
3. Click **Start Analysis →**.
4. Watch the live 10-step progress timeline:
   - `✓ Document uploaded`
   - `✓ Text extracted`
   - `✓ OCR completed`
   - `✓ Regulations searched`
   - `✓ SOP searched`
   - `✓ Findings analyzed`
   - `✓ Risks identified`
   - `✓ Recommendations generated`
   - `✓ Approval note prepared`
   - `✓ Generating approval note DOCX`
5. Review the Findings Severity breakdown (HIGH Risk: Overdue inspection window).
6. Click **Preview** to view the formatted PSU Approval Note modal.
7. Click **Download DOCX** to receive the official Microsoft Word document.
8. Perform Human-in-the-Loop review by clicking **Approve** or **Reject**.

---

## 📡 Offline Verification Test

1. Disconnect your machine from Wi-Fi / Ethernet.
2. Open `http://localhost:5173`.
3. Check **Settings** view -> observe `100% Offline / On-Premise` status badge.
4. Execute all 4 demo flows above — all models, OCR, vector retrieval, and sandbox run 100% offline on local hardware!

---

## 📄 License & Confidentiality
Designed for confidential industrial, government, and PSU deployment. No data ever leaves the host machine.
