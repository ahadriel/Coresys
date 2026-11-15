#!/usr/bin/env python3
import hashlib,json,os,platform,subprocess
from pathlib import Path
def version(cmd):
    try:
        r=subprocess.run(cmd,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        return r.stdout.strip().splitlines()[0]
    except Exception as e: return f"unavailable: {e}"
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
root=Path("build"); names=["coresys-disk.img","coresys.iso","serial.log"]
data={"commit":os.getenv("GITHUB_SHA","local"),"source_date_epoch":os.getenv("SOURCE_DATE_EPOCH","unset"),
 "platform":platform.platform(),"tools":{"clang":version(["clang-18","--version"]),
 "lld_link":version(["lld-link-18","/version"]),"qemu":version(["qemu-system-x86_64","--version"]),
 "xorriso":version(["xorriso","--version"]),"mtools":version(["mformat","--version"]),
 "python":platform.python_version()},
 "artifacts":{n:{"bytes":(root/n).stat().st_size,"sha256":digest(root/n)} for n in names}}
(root/"manifest.json").write_text(json.dumps(data,indent=2)+"\n")
print(json.dumps(data,indent=2))
