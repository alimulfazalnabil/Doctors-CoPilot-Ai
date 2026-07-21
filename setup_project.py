import os

# Define the complete file structure and content for Doctors Copilot
project_structure = {
    "README.md": """# 🩺 Doctors Copilot
An Enterprise-Grade, Ambient AI Clinical Documentation & Coding Assistant
""",
    ".gitignore": """node_modules/
.next/
dist/
build/
.venv/
venv/
env/
__pycache__/
*.py[cod]
.env
.env.local
.terraform/
*.tfstate
*.tfstate.*
.DS_Store
""",
    ".dockerignore": """__pycache__/
*.py[cod]
.env
.venv/
.git/
README.md
""",
    "backend/requirements.txt": """fastapi>=0.110.0
uvicorn[standard]>=0.28.0
azure-cognitiveservices-speech>=1.37.0
azure-ai-textanalytics>=5.3.0
openai>=1.14.0
pydantic>=2.6.0
python-multipart>=0.0.9
""",
    "backend/Dockerfile": """FROM python:3.12-slim-bookworm AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

FROM mwader/static-ffmpeg:7.1 AS ffmpeg-source

FROM python:3.12-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH" PORT=8000
WORKDIR /app
RUN groupadd -g 10001 appgroup && useradd -u 10001 -g appgroup -s /bin/false -m appuser
RUN apt-get update && apt-get install -y --no-install-recommends libssl-dev ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /opt/venv /opt/venv
COPY --from=ffmpeg-source /ffmpeg /usr/local/bin/ffmpeg
COPY --from=ffmpeg-source /ffprobe /usr/local/bin/ffprobe
COPY --chown=appuser:appgroup ./app ./app
USER appuser
EXPOSE 8000
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
""",
    "backend/app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Doctors Copilot Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health/live")
async def liveness():
    return {"status": "ALIVE"}

@app.get("/health/ready")
async def readiness():
    return {"status": "READY"}
""",
    "infra/variables.tf": """variable "resource_group_name" { type = string, default = "rg-doctors-copilot-prod" }
variable "location" { type = string, default = "eastus2" }
variable "environment" { type = string, default = "prod" }
""",
    ".github/workflows/terraform.yml": """name: "IaC: Terraform Provisioning"
on:
  push:
    branches: [ "main" ]
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
""",
    ".github/workflows/deploy-app.yml": """name: "DevSecOps: Deploy App"
on:
  push:
    branches: [ "main" ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
"""
}

def create_project():
    print("🚀 Initializing Doctors Copilot project structure...")
    for filepath, content in project_structure.items():
        # Ensure directory exists
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        # Write file content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"Created: {filepath}")
    
    print("\n✅ Project setup complete! All directories and files have been generated.")

if __name__ == "__main__":
    create_project()