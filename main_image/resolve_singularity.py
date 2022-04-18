import os
import sys
import requests

SERVER_URL = "https://gitlab.kwant-project.org"
PROJECT_ID = 334
JOB_NAME = "build singularity image"
IMAGE_PATH = "build/Singularity.simg"
TARGET_FILENAME = "/etc/singularity_url"

try:
    token = os.environ["GITLAB_API_TOKEN"]
    pipeline_id = os.environ["CI_PIPELINE_ID"]
except KeyError as ex:
    print(f"{ex.args[0]} is undefined, not resolving the Singularity container",
          file=sys.stderr)
    sys.exit(0)

req = requests.get(f"{SERVER_URL}/api/v4/projects/{PROJECT_ID}/pipelines/{pipeline_id}/jobs",
                  headers={"PRIVATE-TOKEN": token})

for job in reversed(req.json()):
    if job["name"] == JOB_NAME:
        with open(TARGET_FILENAME, "w") as f:
            print(f"{SERVER_URL}/api/v4/projects/{PROJECT_ID}/jobs/{job['id']}/artifacts/{IMAGE_PATH}", file=f)
        # Ensure artifacts containing singularity image are preserved
        requests.post(f"{SERVER_URL}/api/v4/projects/{PROJECT_ID}/jobs/{job['id']}/artifacts/keep",
                     headers={"PRIVATE-TOKEN": token})
        sys.exit(0)

print(f"Job \"{JOB_NAME}\" is not found in the CI job", file=sys.stderr)
sys.exit(250)
