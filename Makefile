SHELL := /bin/bash
CLANG ?= clang-18
LLD_LINK ?= lld-link-18
PYTHON ?= python3
BUILD := build
EFI := $(BUILD)/BOOTX64.EFI
.PHONY: all clean image test run
all: image
$(BUILD):
	mkdir -p $(BUILD)
$(BUILD)/main.obj: boot/main.c boot/include/uefi.h | $(BUILD)
	$(CLANG) --target=x86_64-pc-win32-coff -std=c11 -O2 -Wall -Wextra -Werror \
		-ffreestanding -fno-stack-protector -fno-builtin -fshort-wchar -mno-red-zone \
		-Iboot/include -c $< -o $@
$(EFI): $(BUILD)/main.obj
	$(LLD_LINK) /nologo /subsystem:efi_application /entry:efi_main /nodefaultlib \
		/machine:x64 /Brepro /out:$@ $<
image: $(EFI)
	$(PYTHON) scripts/build-image.py --efi $(EFI) --out-dir $(BUILD)
test: image
	$(PYTHON) scripts/test-boot.py --disk $(BUILD)/coresys-disk.img --log $(BUILD)/serial.log
	$(PYTHON) scripts/write-manifest.py
run: image
	@code=$$(find /usr/share/OVMF -name 'OVMF_CODE_4M.fd' -o -name 'OVMF_CODE.fd' | head -n1); \
	vars=$$(find /usr/share/OVMF -name 'OVMF_VARS_4M.fd' -o -name 'OVMF_VARS.fd' | head -n1); \
	test -n "$$code" -a -n "$$vars" || { echo "OVMF not found"; exit 1; }; \
	cp "$$vars" $(BUILD)/OVMF_VARS.run.fd; \
	qemu-system-x86_64 -machine q35 -m 256M \
		-drive if=pflash,format=raw,readonly=on,file="$$code" \
		-drive if=pflash,format=raw,file=$(BUILD)/OVMF_VARS.run.fd \
		-drive if=ide,format=raw,file=$(BUILD)/coresys-disk.img -serial stdio
clean:
	rm -rf $(BUILD)
