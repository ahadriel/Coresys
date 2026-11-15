#ifndef CORESYS_UEFI_H
#define CORESYS_UEFI_H
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long long u64;
typedef u64 usize;
typedef u64 EFI_STATUS;
typedef void *EFI_HANDLE;
typedef u16 CHAR16;
#define EFI_SUCCESS 0
#define EFI_ERROR_BIT (1ULL << 63)
#define EFI_ERROR(s) (((s) & EFI_ERROR_BIT) != 0)
#define EFIAPI
typedef struct { u64 Signature; u32 Revision, HeaderSize, CRC32, Reserved; } EFI_TABLE_HEADER;
typedef struct { u32 Data1; u16 Data2, Data3; u8 Data4[8]; } EFI_GUID;
typedef struct EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL;
struct EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL {
    EFI_STATUS (*Reset)(EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *, u8);
    EFI_STATUS (*OutputString)(EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *, CHAR16 *);
    void *TestString, *QueryMode, *SetMode, *SetAttribute, *ClearScreen;
    void *SetCursorPosition, *EnableCursor, *Mode;
};
typedef struct {
    u32 Version, HorizontalResolution, VerticalResolution, PixelFormat;
    u32 PixelInformation[4];
    u32 PixelsPerScanLine;
} EFI_GRAPHICS_OUTPUT_MODE_INFORMATION;
typedef struct {
    u32 MaxMode, Mode;
    EFI_GRAPHICS_OUTPUT_MODE_INFORMATION *Info;
    usize SizeOfInfo;
    u64 FrameBufferBase;
    usize FrameBufferSize;
} EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE;
typedef struct {
    void *QueryMode, *SetMode, *Blt;
    EFI_GRAPHICS_OUTPUT_PROTOCOL_MODE *Mode;
} EFI_GRAPHICS_OUTPUT_PROTOCOL;
typedef EFI_STATUS (*EFI_LOCATE_PROTOCOL)(EFI_GUID *, void *, void **);
typedef struct {
    EFI_TABLE_HEADER Header;
    void *Services[37];
    EFI_LOCATE_PROTOCOL LocateProtocol;
} EFI_BOOT_SERVICES;
typedef struct {
    EFI_TABLE_HEADER Header;
    CHAR16 *FirmwareVendor;
    u32 FirmwareRevision, Padding;
    EFI_HANDLE ConsoleInHandle;
    void *ConIn;
    EFI_HANDLE ConsoleOutHandle;
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *ConOut;
    EFI_HANDLE StandardErrorHandle;
    EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL *StdErr;
    void *RuntimeServices;
    EFI_BOOT_SERVICES *BootServices;
    usize NumberOfTableEntries;
    void *ConfigurationTable;
} EFI_SYSTEM_TABLE;
#endif
