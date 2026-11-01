"""Export the hash-verified public certifi release for CI's native builder.

The pinned Jupyter bootstrap and Kaniko images predate the CA update. Never copy
an unchecked host/bootstrap store. This is a build input, not runtime fetching.
"""
import hashlib
import io
import json
from pathlib import Path
import re
import ssl
import urllib.request
import zipfile

url = 'https://files.pythonhosted.org/packages/32/d1/a3652fe2c19134d0d15922177821d863cbd7e842d53a21bbe7e8e3a1b5ac/certifi-2026.10.23-py3-none-any.whl'
expected = 'e9b54de76e530bb6cf0ccd036787103acb58fd42ba930ea8bf948ddbaa2f61d1'
raw = urllib.request.urlopen(url, timeout=60).read()
assert hashlib.sha256(raw).hexdigest() == expected
bundle = zipfile.ZipFile(io.BytesIO(raw)).read('certifi/cacert.pem')
certs = re.findall(b'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----', bundle, re.S)
blocked = set(json.loads((Path(__file__).resolve().parents[1]/'blocked-fingerprints.json').read_text()))
assert certs and not blocked.intersection(hashlib.sha256(ssl.PEM_cert_to_DER_cert(c.decode())).hexdigest().upper() for c in certs)
Path('.ci-trust').mkdir(exist_ok=True)
Path('.ci-trust/ca-certificates.crt').write_bytes(bundle)
print('Verified public certifi 2026.10.23:', len(certs), 'roots, zero blocked fingerprints')
