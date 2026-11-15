# Architecture contract

## M0

M0 is a freestanding x86_64 PE32+ UEFI application installed at `EFI/BOOT/BOOTX64.EFI` on a FAT32 EFI System Partition. UEFI provides the initial environment, GOP framebuffer and boot services. The application writes markers to COM1 and draws a project-authored wordmark directly to GOP. It returns to the firmware after the display test; this is not yet a kernel.

## Fixed decisions

- x86_64 UEFI; QEMU/OVMF first.
- Kernel in C; assembly only for architecture entry and interrupt stubs.
- Monolithic kernel with loadable driver modules.
- Four-level paging, per-process address spaces, ELF userspace and project-owned small libc.
- Capability-based permissions; AI tools require explicit revocable grants.
- Separate userspace window server and software compositor.
- Local AI service sandboxed as a userspace process.

## Hardware and licensing

Broadwell and Skylake are the target baseline. M0 uses no CPU-specific extensions, but QEMU does not prove physical compatibility. Project code is authored in this repository; external build tools and firmware are not copied into the OS. Any future inference runtime or model requires a separate license review and approval before adoption.
