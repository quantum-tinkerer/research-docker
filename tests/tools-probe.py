import subprocess,tempfile,pathlib,ctypes,json
r={'ripgrep_version':subprocess.check_output(['rg','--version'],text=True).splitlines()[0]}
assert '15.2.0' in r['ripgrep_version']
with tempfile.TemporaryDirectory() as t:
 p=pathlib.Path(t)/'synthetic.txt';p.write_text('first\nneedle\nlast\n');r['ripgrep_search']=subprocess.check_output(['rg','-n','needle',str(p)],text=True).strip();assert r['ripgrep_search']=='2:needle'
header=pathlib.Path('/opt/conda/include/zlib.h');assert header.is_file();lib=ctypes.CDLL('/opt/conda/lib/libz.so');lib.zlibVersion.restype=ctypes.c_char_p;r['zlib_native_version']=lib.zlibVersion().decode();assert r['zlib_native_version']=='1.3.2';r['zlib_header_present']=True
print(json.dumps(r))
