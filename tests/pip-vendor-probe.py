"""Actual pip vendor imports, serializer compatibility, and native TLS."""
import json, subprocess
from pip._vendor import msgpack, urllib3, requests
from pip._vendor.cachecontrol.serialize import Serializer
assert msgpack.__version__ == '1.2.4'
assert urllib3.__version__ == '2.8.0'
assert msgpack.Unpacker.__module__ == 'pip._vendor.msgpack.fallback'
value={'array':[1,2,3], 'text':'λ', 'binary':b'bytes'}
assert msgpack.unpackb(msgpack.packb(value,use_bin_type=True),raw=False)==value
request=requests.Request('GET','https://pypi.org/simple/pip/').prepare()
response=urllib3.HTTPResponse(body=b'package index',headers={'Content-Type':'text/plain'},status=200,preload_content=False)
serializer=Serializer();encoded=serializer.dumps(request,response,body=b'package index')
restored=serializer.loads(request,encoded)
assert restored is not None and restored.read()==b'package index'
checks={}
for host,good in [('pypi.org',True),('dv-g3b-emudhra.we-have-a-problem.com',False),('dv-g3b-aaa-emudhra.we-have-a-problem.com',False)]:
    try:
        response=requests.get('https://'+host,timeout=25)
        assert good and response.status_code==200
        checks[host]={'status':response.status_code}
    except requests.exceptions.SSLError:
        assert not good
        checks[host]={'certificate_rejected':True}
subprocess.run(['pip','index','versions','pip','--disable-pip-version-check'],check=True,stdout=subprocess.DEVNULL,timeout=60)
print(json.dumps({'msgpack':msgpack.__version__,'urllib3':urllib3.__version__,'pure_python_msgpack':True,'cachecontrol_roundtrip':True,'pip_index':True,'tls':checks}))
