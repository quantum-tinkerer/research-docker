from pathlib import Path
import logging
import os
import sys
import requests
from ruamel.yaml import YAML

logging.basicConfig(level=logging.INFO)
jobs_url = os.getenv("JOBS_URL")
project_url = jobs_url.split("/pipelines")[0]
yaml = YAML()

with open(Path(__file__).parent / ".gitlab-ci.yml") as f:
    ci_config = yaml.load(f)
for job_name, job in ci_config.items():
    try:
        artifact_paths = job["artifacts"]["paths"]
    except (AttributeError, KeyError, TypeError):
        continue
    if image_path := next((p for p in artifact_paths if p.endswith(".simg")), None):
        break
else:
    logging.info(msg="CI does not build a singularity image")
    sys.exit(0)


req = requests.get(os.getenv("JOBS_URL"))
try:
    req.raise_for_status()
except requests.exceptions.HTTPError:
    logging.error(msg="Could not get jobs")
    sys.exit(250)

for job in reversed(req.json()):
    if job["name"] == job_name:
        singularity_url = f"{project_url}/jobs/{job['id']}/artifacts/{image_path}"
        logging.info(msg=f"Singularity image URL: {singularity_url}")
        with open("/etc/singularity_url", "w") as f:
            print(singularity_url, file=f)
        sys.exit(0)

logging.info(msg=f"Job '{job_name}' is not in the pipeline")
sys.exit(0)
