# Coresys

Original x86_64 UEFI hobby OS, built milestone by milestone.

## M0 — UEFI Hello

Builds a project-authored PE/COFF UEFI application, FAT32 EFI System Partition, GPT disk image and UEFI El Torito ISO. CI boots the disk in QEMU/OVMF and checks ordered serial markers. No GRUB, Limine, Linux kernel or third-party OS code is used.

```sh
make all
make test
make run
```

See [docs/BUILD.md](docs/BUILD.md). M0 is a boot-stage application, not yet an OS kernel. Performance targets are reported only after measurement.

- [x] M0: UEFI hello and CI boot check
- [ ] M1: memory, interrupts, timer, preemptive scheduler
- [ ] M2: input, shell, driver module loader
- [ ] M3: storage, FAT32, ELF loader, first userspace process
- [ ] M4: window server and software compositor
- [ ] M5: core apps and theme engine
- [ ] M6: sandboxed local AI and capability grants
- [ ] M7: Broadwell/Skylake hardware compatibility
- [ ] M8: packages, app store skeleton, installer
