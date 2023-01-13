from pathlib import Path
import logging
import os
import sys
import requests
from ruamel.yaml import YAML

logging.basicConfig(level=logging.INFO)
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

api_url = os.getenv("CI_API_V4_URL")
project_id = os.getenv("CI_PROJECT_ID")
pipeline_id = os.getenv("CI_PIPELINE_ID")
project_api_url = f"{api_url}/projects/{project_id}"
jobs_url = f"{project_api_url}/pipelines/{pipeline_id}/jobs"

req = requests.get(jobs_url)
try:
    req.raise_for_status()
except requests.exceptions.HTTPError:
    logging.error(msg="Could not get jobs")
    sys.exit(250)

for job in reversed(req.json()):
    if job["name"] == job_name:
        singularity_url = f"{project_api_url}/jobs/{job['id']}/artifacts/{image_path}"
        logging.info(msg=f"Singularity image URL: {singularity_url}")
        Path("singularity_url").write_text(data=singularity_url)
        sys.exit(0)

logging.info(msg=f"Job '{job_name}' is not in the pipeline")
sys.exit(0)
