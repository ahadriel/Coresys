#!/usr/bin/env python3
import argparse,datetime,hashlib,os,shutil,struct,subprocess,uuid,zlib
from pathlib import Path
SECTOR=512
ESP_BYTES=128*1024*1024
ESP_START=2048
EFI_TYPE=uuid.UUID("c12a7328-f81f-11d2-ba4b-00a0c93ec93b")
def run(args): subprocess.run(args,check=True)
def header(cur,bak,entries_lba,crc,total,dg):
    b=bytearray(SECTOR)
    struct.pack_into("<8sIIIIQQQQ16sQIII",b,0,b"EFI PART",0x10000,92,0,0,
        cur,bak,ESP_START,total-34,dg.bytes_le,entries_lba,128,128,crc)
    struct.pack_into("<I",b,16,zlib.crc32(b[:92])&0xffffffff)
    return b
def make_disk(esp,disk,seed):
    data=esp.read_bytes(); n=len(data)//SECTOR; total=ESP_START+n+34
    dg=uuid.UUID(bytes=hashlib.sha256(seed+b"disk").digest()[:16])
    pg=uuid.UUID(bytes=hashlib.sha256(seed+b"esp").digest()[:16])
    e=bytearray(128); e[:16]=EFI_TYPE.bytes_le; e[16:32]=pg.bytes_le
    struct.pack_into("<QQQ",e,32,ESP_START,ESP_START+n-1,0)
    entries=bytes(e)+bytes(128*127); crc=zlib.crc32(entries)&0xffffffff
    with disk.open("wb") as f:
        f.truncate(total*SECTOR); m=bytearray(SECTOR); m[450]=0xEE
        struct.pack_into("<II",m,454,1,min(total-1,0xffffffff)); m[510:]=b"\x55\xaa"
        f.write(m); f.seek(SECTOR); f.write(header(1,total-1,2,crc,total,dg))
        f.seek(2*SECTOR); f.write(entries); f.seek((total-33)*SECTOR); f.write(entries)
        f.seek((total-1)*SECTOR); f.write(header(total-1,1,total-33,crc,total,dg))
        f.seek(ESP_START*SECTOR); f.write(data)
def main():
    p=argparse.ArgumentParser(); p.add_argument("--efi",required=True); p.add_argument("--out-dir",default="build")
    a=p.parse_args(); out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    efi=Path(a.efi); esp=out/"coresys-esp.img"; disk=out/"coresys-disk.img"; iso=out/"coresys.iso"
    with esp.open("wb") as f: f.truncate(ESP_BYTES)
    img=f"{esp}@@0"
    run(["mformat","-F","-v","CORESYS","-i",img,"::"])
    run(["mmd","-i",img,"::/EFI"]); run(["mmd","-i",img,"::/EFI/BOOT"])
    run(["mcopy","-i",img,str(efi),"::/EFI/BOOT/BOOTX64.EFI"])
    make_disk(esp,disk,hashlib.sha256(efi.read_bytes()).digest())
    root=out/"iso-root"; root.mkdir(exist_ok=True); shutil.copyfile(esp,root/esp.name)
    stamp=datetime.datetime.fromtimestamp(int(os.getenv("SOURCE_DATE_EPOCH","0")),datetime.timezone.utc).strftime("%Y%m%d%H%M%S00")
    run(["xorriso","-as","mkisofs","-r","-J","-V","CORESYS","-uid","0","-gid","0",
      "-volume_date",f"all_file_dates={stamp}","-o",str(iso),"-e",esp.name,"-no-emul-boot",str(root)])
    print(f"Created {esp}, {disk}, {iso}")
if __name__=="__main__": main()
