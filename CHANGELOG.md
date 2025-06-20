# 📦 CHANGELOG.md

All notable changes to this project will be documented in this file.

---

## [v1.0.0] - 2025-06-13

🎉 **Initial public release — Cert Automation & Monitoring Edition**

### ✨ Added

- **🔐 Certificate Automation System**
  - PowerShell scripts for creating Root CA and device SSL certs
  - Automated HTTPS binding using `netsh` to port 44300
  - Scheduled auto-renewal every 90 days with cert rotation

- **🖥️ Certificate Monitoring Dashboard**
  - Built with Streamlit for live cert expiry tracking
  - Visual alerts for expiring or expired certs
  - Integration with Python’s `cryptography` for x509 analysis

- **📁 Project Structure Enhancements**
  - `extensions/cert_automation/` for automation scripts
  - `extensions/cert_dashboard/` for Streamlit UI
  - `logs/` directory for transcript and error outputs

- **🧰 Dev Tools**
  - `.gitignore` with security-first exclusions for `.pfx`, `.cer`, `.log`, and `.env`
  - `.gitattributes` for consistent line endings across OS and languages
  - Pre-commit hook for Python & PowerShell linting and secret detection
  - GitHub Actions workflow: `lint-cert.yml` for CI lint and expiry verification

- **🐳 Docker Support**
  - Streamlit dashboard Dockerfile for containerized deployment
  - Instructions for running dashboard via Docker CLI or locally

- **📖 Documentation**
  - Updated README with clear folder structure, quickstart guides, and command snippets
  - Usage instructions for both local and CI/CD environments
  - Integrated cert tools as extensions to `WorkflowOrchestrator`

---

## Notes

This marks the foundation of ProjectPilotAI's internal infrastructure automation. The cert lifecycle system will evolve to include:
- Multi-host bindings
- Email/Slack expiry alerts
- GitHub secret vaulting
- Cross-device CA provisioning

---

🧠 Maintained by: [@Web4application](https://github.com/Web4application)
