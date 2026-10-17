    .syntax unified
    .text
    .global _start
_start:
    ldr r0, =device
    mov r1, #2
    mov r2, #0
    mov r7, #5
    svc #0
    cmp r0, #0
    blt fail_open
    mov r4, r0

    mov r0, r4
    ldr r1, =0x4004612a
    ldr r2, =unmuted
    mov r7, #54
    svc #0
    cmp r0, #0
    blt fail_ioctl

    mov r0, r4
    ldr r1, =0x4004610a
    ldr r2, =volume
    mov r7, #54
    svc #0
    cmp r0, #0
    blt fail_ioctl

    mov r0, r4
    mov r7, #6
    svc #0
    mov r0, #1
    ldr r1, =ok_message
    mov r2, #3
    mov r7, #4
    svc #0
    mov r0, #0
    b exit

fail_ioctl:
    mov r5, r0
    mov r0, r4
    mov r7, #6
    svc #0
    mov r0, #2
    ldr r1, =ioctl_message
    mov r2, #13
    mov r7, #4
    svc #0
    mov r0, #2
    b exit

fail_open:
    mov r0, #2
    ldr r1, =open_message
    mov r2, #12
    mov r7, #4
    svc #0
    mov r0, #1
exit:
    mov r7, #1
    svc #0

    .data
    .align 2
device: .asciz "/dev/msm_audio_ctl"
unmuted: .word 0
volume: .word 100
ok_message: .ascii "ok\n"
open_message: .ascii "open failed\n"
ioctl_message: .ascii "ioctl failed\n"
