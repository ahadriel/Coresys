#!/usr/bin/env python3
import argparse,os,shutil,subprocess,tempfile,time
from pathlib import Path
MARKERS=["CORESYS_M0_UEFI_START","CORESYS_M0_GOP_READY","CORESYS_M0_BOOT_OK"]
def firmware():
    pairs=[("/usr/share/OVMF/OVMF_CODE_4M.fd","/usr/share/OVMF/OVMF_VARS_4M.fd"),
      ("/usr/share/OVMF/OVMF_CODE.fd","/usr/share/OVMF/OVMF_VARS.fd"),
      ("/usr/share/edk2/ovmf/OVMF_CODE.fd","/usr/share/edk2/ovmf/OVMF_VARS.fd")]
    for c,v in pairs:
        if Path(c).is_file() and Path(v).is_file(): return c,v
    raise SystemExit("OVMF firmware pair not found; install ovmf")
def main():
    p=argparse.ArgumentParser(); p.add_argument("--disk",default="build/coresys-disk.img")
    p.add_argument("--log",default="build/serial.log"); p.add_argument("--timeout",type=int,default=20)
    a=p.parse_args(); log=Path(a.log).resolve(); log.parent.mkdir(parents=True,exist_ok=True)
    code,template=firmware(); kvm=Path("/dev/kvm").exists() and os.access("/dev/kvm",os.R_OK|os.W_OK)
    accel="kvm" if kvm else "tcg"
    with tempfile.TemporaryDirectory() as tmp:
        vars_copy=Path(tmp)/"vars.fd"; shutil.copyfile(template,vars_copy)
        cmd=["qemu-system-x86_64","-machine",f"q35,accel={accel}","-cpu","max","-m","256M",
          "-drive",f"if=pflash,format=raw,readonly=on,file={code}",
          "-drive",f"if=pflash,format=raw,file={vars_copy}",
          "-drive",f"if=ide,format=raw,file={Path(a.disk).resolve()}",
          "-boot","order=c","-display","none","-monitor","none",
          "-serial",f"file:{log}","-no-reboot","-no-shutdown"]
        start=time.monotonic(); proc=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
        try:
            while time.monotonic()-start<a.timeout:
                if proc.poll() is not None: raise SystemExit(f"QEMU exited early: {proc.returncode}")
                data=log.read_text(errors="replace") if log.exists() else ""
                if all(m in data for m in MARKERS):
                    pos=[data.index(m) for m in MARKERS]
                    if pos!=sorted(pos): raise SystemExit("Boot markers out of order")
                    print("PASS: "+" -> ".join(MARKERS))
                    print(f"QEMU accelerator: {accel}; marker time: {time.monotonic()-start:.3f}s")
                    print("Boot-time target measured: "+("yes" if kvm else "no (TCG fallback)"))
                    return
                time.sleep(.1)
            raise SystemExit(f"Timed out after {a.timeout}s waiting for markers")
        finally:
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=3)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait()
if __name__=="__main__": main()
