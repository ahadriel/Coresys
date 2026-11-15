# Ubuntu 24.04 build

## Dependencies

```sh
sudo apt update
sudo apt install -y clang-18 lld-18 nasm mtools xorriso qemu-system-x86 ovmf python3 make
```

The build uses Clang/LLD 18. CI records installed versions. Ubuntu package revisions are supplied by the runner's package snapshot; use the same Ubuntu 24.04 snapshot locally for exact environment reproduction.

## Build

```sh
export SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
make clean
make all
```

Outputs: `build/BOOTX64.EFI`, `build/coresys-esp.img`, `build/coresys-disk.img`, `build/coresys.iso`.

## Test and launch

```sh
make test
make run
```

The test boots the GPT disk headlessly with OVMF, captures `build/serial.log`, and checks three ordered markers. KVM is used only if `/dev/kvm` is accessible; otherwise TCG is used and boot-time performance is marked unmeasured. `make run` opens a graphical QEMU window and sends serial output to the terminal.

OVMF firmware is searched under `/usr/share/OVMF` and `/usr/share/edk2/ovmf`. Install `ovmf` if no CODE/VARS pair is found.

## Reproducibility

Set `SOURCE_DATE_EPOCH` to the commit timestamp. LLD uses `/Brepro`; GPT identifiers derive from the EFI binary hash; xorriso receives a fixed volume timestamp. CI creates `build/manifest.json` containing tool versions and SHA-256 hashes.
