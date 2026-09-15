# Chain Guard AI — Local Setup & Execution Guide 🚀

This guide provides exact, verified Windows PowerShell commands to set up, test, and run Chain Guard AI locally.

---

## 1. Prerequisites

Ensure you have the following installed on your system:
- **Python:** 3.10, 3.11, or 3.12 (`python --version`)
- **Node.js:** v18+ or v20+ (`node --version`)
- **npm:** v9+ or v10+ (`npm --version`)
- **Git:** (`git --version`)

---

## 2. Clone & Branch Verification

```powershell
# Clone the repository
git clone https://github.com/mahipatel1126/bob-ai-hackathon-Axiom.git

# Navigate to project root
cd bob-ai-hackathon-Axiom

# Ensure you are on the integration branch
git checkout feature/ai-optimization
```

---

## 3. Python Environment & Dependencies

From the repository root:

```powershell
# Optional: Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install required Python dependencies
pip install pydantic ortools pytest
```

---

## 4. Run AI Pipeline & Unit Tests

### A. Run Full AI 8-Scenario Pipeline Demo
```powershell
# From repository root
python -m src.ai.run_demo
```
*Expected Output:* `DEMO COMPLETED SUCCESSFULLY - ALL 8 SCENARIOS VERIFIED`

### B. Run Backend & AI Test Suites
```powershell
# Run backend integration tests (27 test cases)
python -m pytest tests -v

# Run AI unit tests (29 test cases)
python -m pytest src/ai/tests -v
```
*Expected Output:* All tests `PASSED` with 0 failures.

---

## 5. Run Backend REST API Server

```powershell
# From repository root
python -m src.backend.app --port 8000
```
- **API Endpoint:** `http://localhost:8000/api`
- **Health Check:** `http://localhost:8000/api/health`
- **Dashboard Overview:** `http://localhost:8000/api/overview`

---

## 6. Frontend Setup & Launch

Open a second PowerShell terminal:

```powershell
# Navigate to frontend directory
cd src/frontend

# Install dependencies (if not already installed)
npm install

# Build production bundle to verify compilation
npm run build

# Start local development server
npm run dev
```
- **Frontend URL:** `http://localhost:5173`
- Open your browser to `http://localhost:5173` to explore the **Chain Guard AI Command Center**.

---

## 7. Optional: IBM Bob / watsonx Configuration

Chain Guard AI functions fully offline with deterministic AI reasoning. To connect to a live IBM watsonx / Bob instance:

1. Create a `.env` file in project root (or set environment variables):
```powershell
$env:BOB_API_KEY="your_ibm_watsonx_api_key"
$env:BOB_API_ENDPOINT="https://us-south.ml.cloud.ibm.com/v1/generate"
$env:BOB_PROJECT_ID="your_ibm_project_id"
```
2. Restart the backend server. The `/api/health` endpoint will report `"bob_connected": true`.

---

## 8. Troubleshooting

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'src'` | Running script directly without module flag | Run as a module from repository root: `python -m src.ai.run_demo` |
| `tsc is not recognized` | npm dependencies not installed in frontend | Run `npm install` inside `src/frontend/` |
| `Port 8000 already in use` | Another process is using port 8000 | Run backend with custom port: `python -m src.backend.app --port 8080` |
| `Execution policy error in PowerShell` | PowerShell script activation restricted | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
