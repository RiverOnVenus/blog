---
title: 字符串的暴力匹配和 KMP 算法
categories: [code]
comments: true
---

<a data-fancybox="gallery" href="../assets/img/post/brute-force-string-match-and-KMP-algorithm/piotr-laskawski-gL7oJLJOb_I-unsplash.jpg"><img src="../assets/img/post/brute-force-string-match-and-KMP-algorithm/piotr-laskawski-gL7oJLJOb_I-unsplash.jpg">

> Photo by <a href="https://unsplash.com/@tot87?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText" target="_blank">Piotr Łaskawski</a> on <a href="https://unsplash.com/?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText" target="_blank">Unsplash</a>

# 什么是暴力匹配？

从源串的第一个字符起，与模式串的第一个字符比较，若相等，则继续逐个比较后续字符；否则从源串的下一个字符起，重新和模式串比较；以此类推，直至模式串的每一个字符依次和源串中一个连续的字符序列相等，则匹配成功。

```c
//暴力匹配
void brute_force_match(char *S, char *T) {
    int i = 1;
    int j = 1; //第0个位置存的字符串长度
    while (i <= S[0] && j <= T[0]) {
        if (S[i] == T[j]) {
            i++;
            j++; //比较下一个字符
        } else { //回退，重新比较
            i = i - j + 2;
            j = 1;
        }
    }
    if (j > T[0])  //匹配成功
        printf("匹配成功，匹配成功的起始位置是第%d个字符\n", i - T[0]);
    else
        printf("匹配失败\n");

}
```

# 什么是KMP算法？

这里直接引用阮一峰老师的文章--[字符串匹配的KMP算法](https://www.ruanyifeng.com/blog/2013/05/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm.html){:target="blank"}

```c
//算出KMP的next数组
void get_next(char *T, int *next) {
    int i = 1;
    next[1] = 0; //恒为零
    int j = 0;
    while (i < T[0]) { // T[0]中存储的是字符串的长度
        if (j == 0 || T[i] == T[j]) { // j==0，说明再次回到了开头
            i++;
            j++;
            next[i] = j; //记录出现重复的位置
        } else {
            j = next[j]; //不相同，找个位置重新比较
        }
    }
}

//KMP匹配算法
void kmp(char *S, char *T, int *next, int pos) {
    int i = pos; //开始查找的起始位置
    int j = 1;
    while (i <= S[0] && j <= T[0]) {
        if (j == 0 || S[i] == T[j]) { //相等各自加加，往后走
            i++;
            j++;
        } else { //不相等，回退next[j]位置
            j = next[j];
        }
    }
    if (j > T[0]) //匹配成功
        printf("匹配成功，匹配成功的起始位置是第%d个字符\n", i - T[0]);
    else
        printf("匹配失败\n");

}
```

 完整代码

```c
/**
 * @file string_match.c
 * @author zhui (RiverOnVenus)
 * @brief 字符串的暴力匹配和KMP算法
 * @version 0.1
 * @date 2022-07-26
 *
 * @copyright Copyright (c) 2022
 *
 */

#include <stdio.h>
#include <string.h>

//暴力匹配
void brute_force_match(char *S, char *T) {
    int i = 1;
    int j = 1; //第0个位置存的字符串长度
    while (i <= S[0] && j <= T[0]) {
        if (S[i] == T[j]) {
            i++;
            j++; //比较下一个字符
        } else { //回退，重新比较
            i = i - j + 2;
            j = 1;
        }
    }
    if (j > T[0])  //匹配成功
        printf("匹配成功，匹配成功的起始位置是源串的第%d个字符\n", i - T[0]);
    else
        printf("匹配失败\n");

}

//算出KMP的next数组
void get_next(char *T, int *next) {
    int i = 1;
    next[1] = 0; //恒为零
    int j = 0;
    while (i < T[0]) { // T[0]中存储的是字符串的长度
        if (j == 0 || T[i] == T[j]) { // j==0，说明再次回到了开头
            i++;
            j++;
            next[i] = j; //记录出现重复的位置
        } else {
            j = next[j]; //不相同，找个位置重新比较
        }
    }
}

//KMP匹配算法
void kmp(char *S, char *T, int *next, int pos) {
    int i = pos; //开始查找的起始位置
    int j = 1;
    while (i <= S[0] && j <= T[0]) {
        if (j == 0 || S[i] == T[j]) { //相等各自加加，往后走
            i++;
            j++;
        } else { //不相等，回退next[j]位置
            j = next[j];
        }
    }
    if (j > T[0]) //匹配成功
        printf("匹配成功，匹配成功的起始位置是源串的第%d个字符\n", i - T[0]);
    else
        printf("匹配失败\n");

}

int main() {
    char S[100];
    char T[20];
    int next[20];

    S[0] = strlen("BBC ABCDAB ABCDABCDABDE"); //S[0] 存放源串长度
    strcpy(S + 1, "BBC ABCDAB ABCDABCDABDE");
    T[0] = strlen("ABCDABD"); //T[0] 存放模式串长度
    strcpy(T + 1, "ABCDABD");

    printf("源串：");
    for (int i = 1; i <= S[0]; ++i) {
        putchar(S[i]);
    }
    printf("\n");

    printf("模式串：");
    for (int i = 1; i <= T[0]; ++i) {
        putchar(T[i]);
    }
    printf("\n");

    printf("暴力匹配：");
    brute_force_match(S, T); //暴力匹配

    get_next(T, next); //计算next数组
    printf("next数组为：");
    for (int i = 1; i <= T[0]; i++) {
        printf("%d ", next[i]);
    }
    printf("\n");

    printf("KMP: ");
    kmp(S, T, next, 1); //KMP算法

    return 0;
}

```

运行结果

```
源串：BBC ABCDAB ABCDABCDABDE
模式串：ABCDABD
暴力匹配：匹配成功，匹配成功的起始位置是源串的第16个字符
next数组为：0 1 1 1 1 2 3 
KMP: 匹配成功，匹配成功的起始位置是源串的第16个字符
```

