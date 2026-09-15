# Contributing to Chain Guard AI 🛡️

Thank you for contributing to Chain Guard AI!

## Branching & Integration Workflow
1. Feature work should be conducted on dedicated feature branches (e.g. `feature/ai-optimization`).
2. Do not commit or push directly to `main` without thorough peer review and test verification.
3. Ensure all tests pass before submitting a pull request:
   ```powershell
   python -m src.ai.run_demo
   python -m pytest tests -v
   python -m pytest src/ai/tests -v
   npm --prefix src/frontend run build
   ```

## Code Standards
- **Python:** Adhere to PEP 8 style guidelines. Use typing annotations where possible.
- **Frontend:** Follow React 18 / TypeScript strict typing conventions.
- **Security:** NEVER commit `.env` files, API keys, passwords, or personal credentials.
