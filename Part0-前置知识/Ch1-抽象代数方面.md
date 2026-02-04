本章摘录 A First Course in Abstract Algebra, 8th Edition (Fraleigh) 中的重要定义和定理. 如果你持有该书的电子英文版, 则搜索方框内的文字就可直达定义原文. 本章只是梳理线索, 如需学习相关知识, 建议仔细阅读原书.

-----

[0.12 Definition] 函数 $f: X\rightarrow Y$ 如果满足命题逻辑 $f(x_1)=f(x_2)\Rightarrow$ $x_1=x_2$, 则称函数是单射的 (one-to-one, injective). 若函数的值域为 $Y$, 则称函数是满射的 (onto, surjective). 若两种性质都满足, 则称函数是双射的 (bijective).

[0.18 Definition] 在集合 S 的两个元素上定义一种关系 “ $\leftrightarrow$ ”. 若该关系满足如下三条性质, 则称为等价关系.

* (自反性) $x \leftrightarrow x$ 恒为真.
* (对称性) 若 $x \leftrightarrow y$ 为真, 则 $y \leftrightarrow x$ 为真.
* (传递性) 若 $x \leftrightarrow y$ 且 $y \leftrightarrow z$ 为真,
则 $x \leftrightarrow z$ 为真.

[0.20 Example] 模 $n$ 同余是极其常见的等价关系.

[2.1 Definition] 群 $G$ 是一个集合 $\left<G, \ast\right>$, 在二元运算 $\ast$ 下封闭, 满足如下公理:

* 结合律 (associativity): 对所有 $a, b, c\in G$, 有 $(a\ast b)\ast c=a\ast(b\ast c)$.
* 单位元 (identity): 存在一个元素 $e\in G$, 对所有元素 $x\in G$, 有 $e\ast x = x\ast e=x$.
* 逆元 (inverse): 对每个元素 $x\in G$, 存在一个元素 $x^\prime\in G$,
使得 $x^\prime\ast x=x\ast x^\prime=e$.

[2.3 Definition] 若群 $G$ 关联的二元运算满足交换律, 则群 $G$ 称为交换群 (commutative group) 或阿贝尔群 (abelian group).

[2.22 Definition] 设群 $\left<G_1,\ast_1\right>$, $\left<G_2, \ast_2\right>$, 映射 $f: G_1\rightarrow G_2$. 若 $f$ 满足以下两个条件, 则称 $f$ 是一个群同构 (group isomorphism).

* 函数 $f$ 是双射.
* 对 $G_1$ 中的任意元素 $a,b$, 有 $f(a\ast_1 b)=f(a)\ast_2 f(b)$

[5.20 Definition] 群 $\left\\{a^n\mid n\in\mathbb{Z}\right\\}$ 是由 $a$ 生成的循环群, 记为 $\left<a\right>$.

[5.22 Definition] 元素 $a$ 是生成元.

[6.1 Theorem] 所有循环群都是交换群.

[6.6 Theorem] 循环群的子群是循环群.

