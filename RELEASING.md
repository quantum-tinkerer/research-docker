# Publishing notebook images

Main and ordinary branches run patch checks and a build without publishing.
After those checks pass, tag the reviewed commit `release-YYYYMMDD` (or append
`-2`, `-3`, etc. for a new candidate that day). Never move an existing release tag.

The tag pipeline runs the same patch and native Kaniko trust checks, then builds
and publishes `combined:<tag>`. It records the registry manifest digest in the
`image-digest.txt` job artifact. It does not change `combined:main`, `latest`,
Hub configuration or running notebooks.

Pull the published digest and run `tests/run-image.py` as described in
`tests/README.md`. Review its scanner applicability and the outstanding exceptions
in `INTEGRATION-HANDOFF.md`. A successful publishing job alone is not the runtime
validation receipt. Promote through staging before updating the production image
reference; retain the prior digest for rollback and preserve user home volumes.
