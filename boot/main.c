#include "uefi.h"
#define COM1 0x3F8
static inline void outb(u16 p,u8 v) { __asm__ volatile("outb %0, %w1"::"a"(v),"d"(p)); }
static inline u8 serial_status(void) {
    u8 v; __asm__ volatile("inb %w1, %0":"=a"(v):"d"((u16)(COM1+5))); return v;
}
static void serial_init(void) {
    outb(COM1+1,0); outb(COM1+3,0x80); outb(COM1,1);
    outb(COM1+1,0); outb(COM1+3,3); outb(COM1+2,0xC7); outb(COM1+4,0x0B);
}
static void serial_putc(char c) {
    unsigned int n=1000000;
    while(n-- && !(serial_status()&0x20)) __asm__ volatile("pause");
    outb(COM1,(u8)c);
}
static void serial_write(const char *s) {
    while(*s) { if(*s=='\n') serial_putc('\r'); serial_putc(*s++); }
}
static void text_write(EFI_SYSTEM_TABLE *s,CHAR16 *t) {
    if(s && s->ConOut && s->ConOut->OutputString) s->ConOut->OutputString(s->ConOut,t);
}
static const u8 *glyph(char c) {
    static const u8 C[7]={14,17,16,16,16,17,14}, O[7]={14,17,17,17,17,17,14};
    static const u8 R[7]={30,17,17,30,20,18,17}, E[7]={31,16,16,30,16,16,31};
    static const u8 S[7]={15,16,16,14,1,1,30}, Y[7]={17,17,10,4,4,4,4};
    switch(c) { case 'C':return C; case 'O':return O; case 'R':return R;
      case 'E':return E; case 'S':return S; case 'Y':return Y; default:return E; }
}
static void pixel(u32 *fb,u32 pitch,u32 w,u32 h,u32 x,u32 y,u32 c) {
    if(x<w && y<h) fb[(usize)y*pitch+x]=c;
}
static void draw_wordmark(EFI_GRAPHICS_OUTPUT_PROTOCOL *g) {
    if(!g || !g->Mode || !g->Mode->Info) return;
    u32 w=g->Mode->Info->HorizontalResolution,h=g->Mode->Info->VerticalResolution;
    u32 pitch=g->Mode->Info->PixelsPerScanLine;
    u32 *fb=(u32 *)(usize)g->Mode->FrameBufferBase;
    if(!fb || w<320 || h<160) return;
    const char *word="CORESYS"; const u32 scale=8;
    u32 sx=(w-7*6*scale)/2,sy=h/2-28;
    for(u32 i=0;i<7;i++) {
        const u8 *rows=glyph(word[i]);
        for(u32 y=0;y<7;y++) for(u32 x=0;x<5;x++) if(rows[y]&(1u<<(4-x)))
            for(u32 dy=0;dy<scale;dy++) for(u32 dx=0;dx<scale;dx++)
                pixel(fb,pitch,w,h,sx+i*6*scale+x*scale+dx,sy+y*scale+dy,0x00E8F0FF);
    }
    for(u32 y=0;y<3;y++) for(u32 x=0;x<w;x++)
        pixel(fb,pitch,w,h,x,sy+7*scale+20+y,0x003B82F6);
}
EFI_STATUS EFIAPI efi_main(EFI_HANDLE image,EFI_SYSTEM_TABLE *st) {
    (void)image; serial_init(); serial_write("CORESYS_M0_UEFI_START\n");
    text_write(st,L"CORESYS: UEFI application started\r\n");
    EFI_GUID guid={0x9042A9DE,0x23DC,0x4A38,{0x96,0xFB,0x7A,0xDE,0xD0,0x80,0x51,0x6A}};
    EFI_GRAPHICS_OUTPUT_PROTOCOL *gop=0;
    EFI_STATUS status=st->BootServices->LocateProtocol(&guid,0,(void **)&gop);
    if(EFI_ERROR(status)||!gop||!gop->Mode||!gop->Mode->Info) {
        serial_write("CORESYS_M0_GOP_FAIL\n"); text_write(st,L"CORESYS: GOP unavailable\r\n"); return status;
    }
    draw_wordmark(gop); serial_write("CORESYS_M0_GOP_READY\n");
    serial_write("CORESYS_M0_BOOT_OK\n");
    text_write(st,L"CORESYS: framebuffer ready. M0 boot complete.\r\n");
    return EFI_SUCCESS;
}
