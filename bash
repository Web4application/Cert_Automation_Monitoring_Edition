docker build -t projectpilot-cert-dashboard .
docker run -p 8501:8501 projectpilot-cert-dashboard

git add .gitignore .gitattributes pyproject.toml requirements.txt requirements-dev.txt .github/workflows/lint-cert.yml
git commit -m "🚀 Harden build: git hygiene, pyproject packaging, cert CI, modern dependency setup"
git push origin main

pip install -r requirements.txt

chmod +x .git/hooks/pre-commit

cd extensions/cert_dashboard
streamlit run app.py

docker build -t web4-cert-generator .
docker run --rm \
  -e WEB4_CA_NAME="WEB4 Root CA" \
  -e WEB4_CODE_NAME="CI Builder" \
  -e WEB4_SERVER_NAME="ci.web4.com" \
  -e WEB4_SERVER_SANS="ci.web4.com,api.web4.com" \
  -v $(pwd)/web4_certs:/app/web4_certs \
  web4-cert-generator
