import subprocess
import os

class WorkflowOrchestrator:
    def __init__(self, extractor, analyzer, github_agent):
        self.extractor = extractor
        self.analyzer = analyzer
        self.github_agent = github_agent

    def run_cert_automation(self):
        script_path = os.path.join("extensions", "cert_automation", "auto_cert.ps1")
        try:
            subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path], check=True)
            print("✅ Certificate automation executed.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Cert automation failed: {e}")

    def run(self, transcript):
        tasks = self.extractor.extract(transcript)
        analysis = self.analyzer.analyze()
        self.github_agent.create_issues(tasks)
        self.run_cert_automation()
        return {"tasks": tasks, "analysis": analysis}
