---
title: 字节顺序──小端序和大端序
categories: [code]
comments: true
---

<a data-fancybox="cpu-schedulers" href="../assets/img/post/endianness-little-endian-and-big-endian/samsung-memory-mDP3qpqLIh4-unsplash.jpg"><img src="../assets/img/post/endianness-little-endian-and-big-endian/samsung-memory-mDP3qpqLIh4-unsplash.jpg">

>Photo by <a href="https://unsplash.com/@samsungmemory?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText" target="_blank">Samsung Memory</a> on <a href="https://unsplash.com/?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText" target="_blank">Unsplash</a>

# 0x00 什么是字节顺序

字节顺序，又称端序或尾序，在计算机科学领域中，指电脑内存中或在数字通信链路中，占内存多于一个字节类型的数据在内存中的存放顺序。 在几乎所有的机器上，多字节对象都被存储为连续的字节序列。例如在C语言中，在32位的环境下，一个类型为`int`的变量`x`地址为`0x79abcdef`，那么其对应地址表达式`&x`的值为`0x79abcdef`.

使用命令 `lscpu` 可以查看 cpu 的字节序。

```shell
lscpu | grep -i endian
```

输出：

```
Byte Order:                      Little Endian
```

字节序分为大端序和小端序，大端序是最高位字节`0x79` 存储在低的内存地址处，最低位字节`0xef`存储在高的内存地址处。小端序是最低位字节`0xef` 存储在低的内存地址处，最高位字节`0x79`存储在高的内存地址处。

<a data-fancybox="cpu-schedulers" href="../assets/img/post/endianness-little-endian-and-big-endian/endianess.png"><img src="../assets/img/post/endianness-little-endian-and-big-endian/endianess.png" style="text-align:center;" >

# 0x01 大小端的转换

最简单的方法是用`__builtin_bswapXX`函数

```c
#include <inttypes.h>
#include <stdio.h>

int main() {
    uint32_t le = 0x79abcdef;
    uint32_t be = __builtin_bswap32(le);

    printf("Little-endian: 0x%" PRIx32 "\n", le);
    printf("Big-endian:    0x%" PRIx32 "\n", be);

    return 0;
}

```

输出：

```
Little-endian: 0x79abcdef
Big-endian:    0xefcdab79
```

`__builtin_bswapXX` 是 [GCC内置函数](https://gcc.gnu.org/onlinedocs/gcc/Other-Builtins.html){:target="blank"}。

> - Built-in Function: *uint16_t* **__builtin_bswap16** *(uint16_t x)*
>
>   Returns x with the order of the bytes reversed; for example, `0xaabb` becomes `0xbbaa`.  Byte here always means exactly 8 bits.
>
> - Built-in Function: *uint32_t* **__builtin_bswap32** *(uint32_t x)*
>
>   Similar to `__builtin_bswap16`, except the argument and return types are 32-bit.
>
> - Built-in Function: *uint64_t* **__builtin_bswap64** *(uint64_t x)*
>
>   Similar to `__builtin_bswap32`, except the argument and return types are 64-bit.
>
> - Built-in Function: *uint128_t* **__builtin_bswap128** *(uint128_t x)*
>
>   Similar to `__builtin_bswap64`, except the argument and return types are 128-bit.  Only supported on targets when 128-bit types are supported.

# 参考资料

- [https://stackoverflow.com/questions/19275955/convert-little-endian-to-big-endian](stackoverflow/convert-little-endian-to-big-endian){:target="blank"}