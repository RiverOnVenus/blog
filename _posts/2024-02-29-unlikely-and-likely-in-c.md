---
title: C 语言中的 unlikely 和 likely
categories: [code]
comments: true
---

 今天在这个 [commit](https://github.com/firelzrd/bore-scheduler/commit/2dfae364f6d7ae26eca4ddfafb3764f2525bbaa5) 中看到这样一段代码：

```c
#ifdef CONFIG_SCHED_BORE
		if (unlikely(!sched_bore)) {
#endif // CONFIG_SCHED_BORE
```

这个 `unlikely` 让我很疑惑，`if` 里面还能这样？然后在网上查了相关资料，了解了其作用。因为这段代码是在`kernel/sched/fair.c`中，于是去翻看了 Linux 内核源码，发现很多`if`处使用了 `unlikely`.

`likely()`和`unlikely()`是一种宏，帮助编译器更好地优化代码的执行路径，以提高程序的性能，`likely()`宏用于表示条件为真的可能性较大，而`unlikely()`宏则用于表示条件为假的可能性较大。

比如一个判断素数的列子：

```c
#include <stdio.h>

#define likely(x)   __builtin_expect(!!(x), 1)
#define unlikely(x) __builtin_expect(!!(x), 0)

int is_prime(int n) {
    if (n <= 1) {
        return 0;
    }

    if (n == 2 || n == 3) {
        return 1;
    }

    if (n % 2 == 0) {
        return 0;
    }

    for (int i = 3; i * i <= n; i += 2) {
        if (unlikely(n % i == 0)) {
            return 0;
        }
    }
    return 1;
}

int main() {
    int num = 17;

    if (likely(is_prime(num))) {
        printf("%d is likely a prime number\n", num);
    } else {
        printf("%d is unlikely a prime number\n", num);
    }

    return 0;
}

```

第二十行里，`unlikely(n % i == 0)` 表示编译器应该将 `n % i == 0` 这个条件判断视为不太可能发生的情况。

如果懂汇编的话可以从汇编层查看对应变化。

既然知道了作用，可不可以通过程序验证是否有优化呢？比如通过时间复杂度高的查找算法在数据级大的样本里查找，然后比较花费的时间，不知道这样是否可以验证。

这是一段查找素数的代码：

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>

#define MAX_NUMBER 100000000

#define likely(x)   __builtin_expect(!!(x), 1)
#define unlikely(x) __builtin_expect(!!(x), 0)

void find_primes_with_unlikely() {
    bool is_prime;

    struct timespec start, end;
    double cpu_time_used;

    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 2; i <= MAX_NUMBER; i++) {
        is_prime = true;
        for (int j = 2; j * j <= i; j++) {
            if (unlikely(i % j == 0)) {
                is_prime = false;
                break;
            }
        }
        if (is_prime) {
            // printf("%d ", i);
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    cpu_time_used = (end.tv_sec - start.tv_sec) * 1e9 + (end.tv_nsec - start.tv_nsec);

    printf("Find primes with unlikely execution time: %lf ns\n", cpu_time_used);
}

void find_primes_without_unlikely() {
    bool is_prime;

    struct timespec start, end;
    double cpu_time_used;

    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 2; i <= MAX_NUMBER; i++) {
        is_prime = true;
        for (int j = 2; j * j <= i; j++) {
            if (i % j == 0) {
                is_prime = false;
                break;
            }
        }
        if (is_prime) {
            // printf("%d ", i);
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    cpu_time_used = (end.tv_sec - start.tv_sec) * 1e9 + (end.tv_nsec - start.tv_nsec);

    printf("Find primes without unlikely execution time: %lf ns\n", cpu_time_used);
}

int main() {
    printf("Starting prime search...\n");
  
    find_primes_with_unlikely();

    find_primes_without_unlikely();

    return 0;
}

```

最开始用`gettimeofday()`函数来获取时间信息，发现几乎没有什么区别，于是换成了 `clock_gettime()` 函数来获取纳秒级别的时间信息。

但是吧，这个测试结果不太对，大多数时候是用了`unlikely`的花费更多时间...是因为不应该用这样的方式比较？

我又发现了 C++ 也有 `[[likely]]` `[[unlikely]]`，并且 cppreference 有[示例代码](https://zh.cppreference.com/w/cpp/language/attributes/likely)：

```c++
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <random>
 
namespace with_attributes
{
    constexpr double pow(double x, long long n) noexcept
    {
        if (n > 0) [[likely]]
            return x * pow(x, n - 1);
        else [[unlikely]]
            return 1;
    }
    constexpr long long fact(long long n) noexcept
    {
        if (n > 1) [[likely]]
            return n * fact(n - 1);
        else [[unlikely]]
            return 1;
    }
    constexpr double cos(double x) noexcept
    {
        constexpr long long precision{16LL};
        double y{};
        for (auto n{0LL}; n < precision; n += 2LL) [[likely]]
            y += pow(x, n) / (n & 2LL ? -fact(n) : fact(n));
        return y;
    }
} // namespace with_attributes
 
namespace no_attributes
{
    constexpr double pow(double x, long long n) noexcept
    {
        if (n > 0)
            return x * pow(x, n - 1);
        else
            return 1;
    }
    constexpr long long fact(long long n) noexcept
    {
        if (n > 1)
            return n * fact(n - 1);
        else
            return 1;
    }
    constexpr double cos(double x) noexcept
    {
        constexpr long long precision{16LL};
        double y{};
        for (auto n{0LL}; n < precision; n += 2LL)
            y += pow(x, n) / (n & 2LL ? -fact(n) : fact(n));
        return y;
    }
} // namespace no_attributes
 
double gen_random() noexcept
{
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_real_distribution<double> dis(-1.0, 1.0);
    return dis(gen);
}
 
volatile double sink{}; // 确保有副作用
 
int main()
{
    for (const auto x : {0.125, 0.25, 0.5, 1. / (1 << 26)})
        std::cout
            << std::setprecision(53)
            << "x = " << x << '\n'
            << std::cos(x) << '\n'
            << with_attributes::cos(x) << '\n'
            << (std::cos(x) == with_attributes::cos(x) ? "equal" : "differ") << '\n';
 
    auto benchmark = [](auto fun, auto rem)
    {
        const auto start = std::chrono::high_resolution_clock::now();
        for (auto size{1ULL}; size != 10'000'000ULL; ++size)
            sink = fun(gen_random());
        const std::chrono::duration<double> diff =
            std::chrono::high_resolution_clock::now() - start;
        std::cout << "Time: " << std::fixed << std::setprecision(6) << diff.count()
                  << " sec " << rem << std::endl; 
    };
 
    benchmark(with_attributes::cos, "(with attributes)");
    benchmark(no_attributes::cos, "(without attributes)");
    benchmark([](double t) { return std::cos(t); }, "(std::cos)");
}
```

但是测出来大多数时候也是 `with_attributes` 更耗时。也许需要更专业的工具配合正确的场景来进行测试。

参考资料：

1. [https://www.geeksforgeeks.org/branch-prediction-macros-in-gcc/](https://www.geeksforgeeks.org/branch-prediction-macros-in-gcc/)
2. [https://stackoverflow.com/questions/109710/how-do-the-likely-unlikely-macros-in-the-linux-kernel-work-and-what-is-their-ben](https://stackoverflow.com/questions/109710/how-do-the-likely-unlikely-macros-in-the-linux-kernel-work-and-what-is-their-ben)
3. [https://zh.cppreference.com/w/cpp/language/attributes/likely](https://zh.cppreference.com/w/cpp/language/attributes/likely)
