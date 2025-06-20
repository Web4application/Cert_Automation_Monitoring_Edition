docker build -t projectpilot-cert-dashboard .
docker run -p 8501:8501 projectpilot-cert-dashboard

git add .gitignore .gitattributes pyproject.toml requirements.txt requirements-dev.txt .github/workflows/lint-cert.yml
git commit -m "🚀 Harden build: git hygiene, pyproject packaging, cert CI, modern dependency setup"
git push origin main

pip install -r requirements.txt

chmod +x .git/hooks/pre-commit

cd extensions/cert_dashboard
streamlit run app.py
