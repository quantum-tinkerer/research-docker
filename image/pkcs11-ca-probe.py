#!/usr/bin/env python3
"""Enumerate only public certificate objects from one explicit PKCS#11 module."""
import ctypes as c,hashlib,json,sys
U=c.c_ulong;P=c.c_void_p
class Version(c.Structure):_fields_=[('major',c.c_ubyte),('minor',c.c_ubyte)]
class Functions(c.Structure):_fields_=[('version',Version),('pointers',P*68)]
class Attribute(c.Structure):_fields_=[('type',U),('value',P),('length',U)]
lib=c.CDLL(sys.argv[1]);table=c.POINTER(Functions)()
assert lib.C_GetFunctionList(c.byref(table))==0
F=table.contents.pointers
def fun(i,*args):return c.CFUNCTYPE(U,*args)(F[i])
def check(rc):
 if rc:raise RuntimeError('PKCS11 return '+str(rc))
check(fun(0,P)(None))
count=U();check(fun(4,c.c_ubyte,c.POINTER(U),c.POINTER(U))(1,None,c.byref(count)))
slots=(U*count.value)();check(fun(4,c.c_ubyte,c.POINTER(U),c.POINTER(U))(1,slots,c.byref(count)))
hashes=[]
for slot in slots:
 session=U();check(fun(12,U,U,P,P,c.POINTER(U))(slot,4,None,None,c.byref(session)))
 klass=U(1);template=Attribute(0,c.cast(c.pointer(klass),P),c.sizeof(klass))
 check(fun(26,U,c.POINTER(Attribute),U)(session,c.byref(template),1))
 while True:
  objects=(U*64)();found=U();check(fun(27,U,c.POINTER(U),U,c.POINTER(U))(session,objects,64,c.byref(found)))
  if not found.value:break
  for obj in objects[:found.value]:
   attr=Attribute(0x11,None,0);check(fun(24,U,U,c.POINTER(Attribute),U)(session,obj,c.byref(attr),1))
   value=c.create_string_buffer(attr.length);attr.value=c.cast(value,P);check(fun(24,U,U,c.POINTER(Attribute),U)(session,obj,c.byref(attr),1))
   hashes.append(hashlib.sha256(value.raw[:attr.length]).hexdigest().upper())
 check(fun(28,U)(session));check(fun(13,U)(session))
check(fun(1,P)(None))
bad={'45A883F349AEDFD5F3A649B5498FFB121712BA8B448F3F2A91DBC5A766FCDDBE', 'A496E23AC0CAB8155FC9B117B97EAE368EFCBB9041AEC8804D5A308D2D01C2D8', '4B2460A466F95FD40113BCDCCA2CEB29B3B093921DE45474DA7DF48874C630B1', 'E7568FE6E12331F4FD7DE61DA4C7559D0F8EB192A218D4741A3BA75184333838', 'D7A7A0FB5D7E2731D771E9484EBCDEF71D5F0C3E0A2948782BC83EE0EA699EF4', '42C4ACCD12C4F59597925E1A08A7A90102608543809308D50EC427E118BA1493', '0164D7CEAE5BB909C272AF151FF44B1177AE9B47D9424B94F1D9558C30934D19', '9E39DE2881273ACC225A149C72BA3E0F51424963669AB633EE1DC7DF5DB067B4', '579480AEA166290BD3C643589E795FC0D0E54E86505D180F1DFF99EFD3199512', 'CB6E15165AC802E9B3F993F16C25D41F4E81C21EBDE71AE1B012AC00BF9C7C3F', '86A1ECBA089C4A8D3BBE2734C612BA341D813E043CF9E8A862CD5C57A36BBE6B', 'FD9D5C2DBBD4995AB69B8D50C439D9527B00529199C2FD01B2174EB58F07021F', '7485B51C0ED192878FA1D2F948FB529AE1842CC5086C4B67F7BE5B2039DE9489', '62B7F9868263F72F6911FC78CEAF72C1979158B7368BF648683BB2AA39B02E72', 'F2EDAAFF3D9B701FB4D14C9F285F8C0BAD90FC3BCC1FA07D47F4718EDABA34A5', '7DD78D5F4F13459A83DFF9ABBBA62EDBAF6F2D102BF257FD712F4D9F2746ED8D', '5F1DED4DD590AF74631290CF073B122A2AAC6A1FA479778A0BD43579BD832699', '98B896625C0C230ADEEC3EB2CF6AAD5001ECF9156A68644E82374CE5833BC25B', '432EC25F0D28DE9006D97BF752F17BBB2CD41F669933FCB072D9A1148D0261F3', '84112972B8E59D14560AE7E7119654474AAD119990CF3722BFC1E3B91615E1FD'}
print(json.dumps({'certificates':len(hashes),'affected':sorted(set(hashes)&bad)}))
raise SystemExit(0 if len(hashes)>50 and not set(hashes)&bad else 1)
