/*
******************************************************************************
**
** @file        : LinkerScript.ld
**
** @author      : STM32CubeIDE
**
**  Abstract    : Linker script for STM32H7Sxx Device (with XSPI1 External Flash)
**                      64Kbytes FLASH
**                      456Kbytes RAM
**                      128Mbytes External XSPI1 Flash
**
******************************************************************************
*/

/* Entry Point */
ENTRY(Reset_Handler)

/* Highest address of the user mode stack */
_estack = ORIGIN(DTCM) + LENGTH(DTCM); /* end of Ram type memory */

_Min_Heap_Size = 0x200; /* required amount of heap */
_Min_Stack_Size = 0x400; /* required amount of stack */

__FLASH_BEGIN  = 0x08000000;
__FLASH_SIZE   = 0x00010000; /* 64 KB */

__RAM_BEGIN    = 0x24000000;
__RAM_SIZE     = 0x71C00;
__RAM_NONCACHEABLEBUFFER_SIZE = 0x400;

/* Memories definition */
MEMORY
{
  RAM                    (xrw) : ORIGIN = __RAM_BEGIN,                               LENGTH = __RAM_SIZE
  RAM_NONCACHEABLEBUFFER (xrw) : ORIGIN = __RAM_BEGIN + __RAM_SIZE,                  LENGTH = __RAM_NONCACHEABLEBUFFER_SIZE

  ITCM                   (xrw) : ORIGIN = 0x00000000,                                LENGTH = 0x00010000
  DTCM                    (rw) : ORIGIN = 0x20000000,                                LENGTH = 0x00010000
  SRAMAHB                (rw)  : ORIGIN = 0x30000000,                                LENGTH = 0x00008000
  BKPSRAM                (rw)  : ORIGIN = 0x38800000,                                LENGTH = 0x00001000

  FLASH                  (xrw) : ORIGIN = __FLASH_BEGIN,                             LENGTH = __FLASH_SIZE
  XSPI1_FLASH             (rx) : ORIGIN = 0x70000000,                                LENGTH = 128M
}

/* Sections */
SECTIONS
{
  /* Startup code into "FLASH" */
  .isr_vector :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  } >FLASH

  /* Program code into "FLASH" */
  .text :
  {
    . = ALIGN(4);
    *(.text)
    *(.text*)
    *(.glue_7)
    *(.glue_7t)
    *(.eh_frame)

    KEEP (*(.init))
    KEEP (*(.fini))

    . = ALIGN(4);
    _etext = .;
  } >FLASH

  /* Constant data into internal "FLASH" */
  .rodata :
  {
    . = ALIGN(4);
    *(.rodata)
    *(.rodata*)
    . = ALIGN(4);
  } >FLASH

  .ARM.extab (READONLY) :
  {
    . = ALIGN(4);
    *(.ARM.extab* .gnu.linkonce.armextab.*)
    . = ALIGN(4);
  } >FLASH

  .ARM (READONLY) :
  {
    . = ALIGN(4);
    __exidx_start = .;
    *(.ARM.exidx*)
    __exidx_end = .;
    . = ALIGN(4);
  } >FLASH

  .preinit_array (READONLY) :
  {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__preinit_array_start = .);
    KEEP (*(.preinit_array*))
    PROVIDE_HIDDEN (__preinit_array_end = .);
    . = ALIGN(4);
  } >FLASH

  .init_array (READONLY) :
  {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__init_array_start = .);
    KEEP (*(SORT(.init_array.*)))
    KEEP (*(.init_array*))
    PROVIDE_HIDDEN (__init_array_end = .);
    . = ALIGN(4);
  } >FLASH

  .fini_array (READONLY) :
  {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__fini_array_start = .);
    KEEP (*(SORT(.fini_array.*)))
    KEEP (*(.fini_array*))
    PROVIDE_HIDDEN (__fini_array_end = .);
    . = ALIGN(4);
  } >FLASH

  /* ======================================================================== */
  /* External Flash Section (Assets, Splashes, Raw Bitmaps)                   */
  /* ======================================================================== */
  .xspi_flash :
  {
    . = ALIGN(4);
    *(.xspi_flash)
    *(.xspi_flash*)
    . = ALIGN(4);
  } >XSPI1_FLASH

  /* Used by the startup to initialize data */
  _sidata = LOADADDR(.data);

  /* Initialized data sections into RAM */
  .data :
  {
    . = ALIGN(4);
    _sdata = .;
    *(.data)
    *(.data*)
    *(.RamFunc)
    *(.RamFunc*)

    . = ALIGN(4);
    _edata = .;
  } >RAM AT> FLASH

  /* Uninitialized data section into RAM */
  . = ALIGN(4);
  .bss :
  {
    _sbss = .;
    __bss_start__ = _sbss;
    *(.bss)
    *(.bss*)
    *(COMMON)

    . = ALIGN(4);
    _ebss = .;
    __bss_end__ = _ebss;
  } >RAM

  RW_NONCACHEABLE (NOLOAD):
  {
    __NONCACHEABLEBUFFER_BEGIN = .;
    KEEP(*(noncacheable_buffer))
    __NONCACHEABLEBUFFER_END = .;
  } > RAM_NONCACHEABLEBUFFER

  /* Heap and Stack */
  ._user_heap_stack :
  {
    . = ALIGN(8);
    PROVIDE ( end = . );
    PROVIDE ( _end = . );
    . = . + _Min_Heap_Size;
    . = . + _Min_Stack_Size;
    . = ALIGN(8);
  } >DTCM

  /* Discard unused compiler libraries */
  /DISCARD/ :
  {
    libc.a ( * )
    libm.a ( * )
    libgcc.a ( * )
  }

  .ARM.attributes 0 : { *(.ARM.attributes) }
}