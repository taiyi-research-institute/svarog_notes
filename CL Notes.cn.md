## 第一部分. 二次域的整环

一个整数 $d$ 是 <mark>无平方因子的</mark>，当且仅当其素因数分解中每个素数恰好出现一次。形式上，$d=p_1p_2\cdots p_k$，其中 $p_i$ 是不同的素数。

一个 <mark>代数数</mark> 是具有整数（或等价地，有理数）系数的非零单变量有限次多项式的（复）根。

* 根可以是实数或复数。
* 系数是有理数。
* 系数乘以分母的最小公倍数后成为整数。通分。

一个 <mark>代数整数</mark> 是具有整数系数且首项系数为 1 的多项式的（复）根。

代数数 $a$ 的 <mark>极小多项式</mark> 是唯一的、首一的、不可约的（在有理数上）最小次数多项式 $p(x)$，具有有理系数使得 $p(a)=0$。

* $p(x)\in\mathbb{Q}(x)$，首项系数为 1。

通过构造，$a+b\sqrt{d}$ 的 <mark>极小多项式</mark> 是
$$
\begin{align}
p(x)&=(x-(a+b\sqrt{d}))(x-(a-b\sqrt{d})) \\
&=x^2-2ax+a^2-b^2d
\end{align}
$$
一个 <mark>二次**域**</mark> $F$ 是 $\mathbb{Q}$ 的域扩张，作为 $\mathbb{Q}$ 上的向量空间维数/秩为 2。即，
$$
F = \mathbb{Q}(\sqrt{d})=\left\{a+b\sqrt{d}: \forall a,b\in\mathbb{Q}\right\} ~~.
$$
为了构造"有意义的"（非平凡的、且在最简平方根意义下唯一的）$\mathbb{Q}$ 的扩张，我们 <mark>通常要求 $d$ 是无平方因子的</mark>。反例：

* 平凡：$\mathbb{Q}(\sqrt 4)=\mathbb{Q}$
* 重复：$\mathbb{Q}(\sqrt{108})=\mathbb{Q}(\sqrt{3})$

$F= \mathbb{Q}(\sqrt{d})$ 的 <mark>代数整数</mark> 是形式为 $a+b\sqrt{d}$ 的所有元素的总体，使得 $p(x)$ 具有整数系数。

设 $\mathcal{O}_F$ 是 $F$ 的所有代数整数的集合，则
$$
\mathcal{O}_F = \begin{cases}
\mathbb{Z}\left[\dfrac{1+\sqrt{d}}{2}\right] & d\equiv 1~(\mathrm{mod}~4) \\
\mathbb{Z}\left[\sqrt{d}\right] & d\equiv 2,3~(\mathrm{mod}~4) ~~.
\end{cases}
$$
注意 $d\equiv 0~(\mathrm{mod}~4)$ 的情况是不可能的，因为 $d$ 是无平方因子的。

**问题：** 为什么对于任何 $d$，$\mathbb{Z}\left[\sqrt{d}\right]$ 都不能穷尽 $\mathcal{O}_F$？

**解释：**

为了使 $a+b\sqrt{d}~~(a,b\in \mathbb{Q})$ 成为代数整数，我们需要使 $2a$ 和 $a^2-db^2$ 都是整数。注意 $a, b$ 是有理数。因此我们需要讨论 $a, b$ 的可能模式。设 $h,j,m,n,p,q$ 为整数。

(情况 1) 如果 $a=h$，则 $b=p/q$ 或 $b=p$。

(情况 1.1) 如果 $b=p/q$，则 $db^2=d\frac{p^2}{q^2}$，其中 $\gcd(p,q)=1$。由于 $db^2$ 是整数，我们有 $q^2\mid d$，这与 $d$ 无平方因子矛盾。

(情况 1.2) 如果 $b=p$，则对任何 $d$，$a^2-db^2$ 都是整数。

(情况 2) 如果 $a=h+\frac{1}{2}$。设 $b=p/q$，其中 $\gcd(p,q)=1$，则 $a^2-db^2=h^2+h+\frac{1}{4}-\frac{dr^2}{s^2}$。

(情况 2.1) 如果 $s=1$，则与 $\frac{1}{4}-\frac{dr^2}{s^2}$ 是整数矛盾。

(情况 2.2) 如果 $s=2$。设 $r=2j+1$，则 $\frac{1}{4}-\frac{dr^2}{s^2}=\frac{1}{4}-\frac{d(4j^2+4j+1)}{4}$。唯一可能的 $d$ 是 $d\equiv 1~(\mathrm{mod}~4)$。

(情况 2.3) 对于任何其他 $s$，假设 $s=p_1^{r_1}p_2^{r_2}\cdots p_S^{r_S}$ 且 $d=q_1q_2\cdots q_D$。如果存在某些 $q$ 与某些 $p$ 相同，则在简化后的 $\frac{d}{s^2}$ 的分母中，这些相同的素因子被提升到奇数幂。因此分母不能是 4，这与 $\frac{1}{4}-\frac{dr^2}{s^2}$ 是整数矛盾。

从上述讨论，我们有

* 如果 $d\equiv 1~(\mathrm{mod}~4)$，则 $(a, b)$ 可以是 <mark>整数对或半整数对</mark>。这样的 $a+b\sqrt{d}$ 可以用基 $\left\{1, \frac{1+\sqrt{d}}{2} \right\}$ 的 $\mathbb{Z}$-模表示。
* 否则，$a, b$ 可以是整数。这样的 $a+b\sqrt{d}$ 可以用基 $\left\{1, \sqrt{d} \right\}$ 的 $\mathbb{Z}$-模表示。

$\mathcal{O}_F$ 是 $F$ 的子环，称为 $F$ 的 <mark>极大整环</mark>。$\mathcal{O}_F$ 的任何包含 1 且是秩为 2 的自由 $\mathbb{Z}$-模的子环 $\mathcal{O}$ 称为 $F$ 的 <mark>整环</mark>。

## 第二部分. 二次域的类群

一个 <mark>理想</mark> 是环 $\mathcal{R}$ 的加法子群 $\mathfrak{I}$（Fraktur 字体的"I"），满足"乘法陷阱"性质，即
$$
xy\in \mathfrak{I}~\mathrm{和}~yx\in \mathfrak{I}~~\forall x\in\mathcal{R},y\in\mathfrak{I}~.
$$

> 关键词：加法子群，乘法陷阱。

两个理想 $\mathfrak{a},\mathfrak{b}$ 的加法定义为
$$
\mathfrak{a}+\mathfrak{b} = 
\left\{
a+b
~|~
a\in\mathfrak{a},b\in \mathfrak{b}
\right\} ~.
$$
两个理想的乘法定义为
$$
\mathfrak{a}\mathfrak{b} = 
\left\{
\sum_{i=1}^n a_i b_i
~|~
a_i\in\mathfrak{a},b_i\in \mathfrak{b},n\ge 1
\right\} ~.
$$
