设 secp256k1 的坐标模参数为 $p$, 群阶参数为 $n$. 已知 $p, n$ 都是质数且 $p, n\equiv 1 \pmod 3$.

(1) 证明: 存在 $\alpha^3 \equiv 1 \pmod p$ 且 $\alpha\ne 1$, 使得对曲线上的任意点 $P=(x,y)$, 点 $Q=(\alpha x, y)$ 也在曲线上.

(2) 证明: 存在 $\lambda^3 \equiv 1 \pmod n$ 且 $\lambda\ne 1$, 使得对曲线上的任意点 $P=(x,y)$, 有 $Q=\lambda P$.

(3) $\alpha$ 和 $\lambda$ 怎么算?

(4) 以上发现有何应用价值?

-----

### 子命题: $\mathbb{F}_p^*$ 是 $p-1$ 阶循环群

证明：令 $x$ 为 $\mathbb{F}_p^*$ 中任意非零元素, $m$ 为各元素的阶的最小公倍数, 即
$$
m=\mathrm{lcm}\left(\left\{
\mathrm{ord}(x) \mid x\in\mathbb{F}_p^*,x\ne 0
\right\}\right).
$$
如此, 对任意 $x$ 有 $x^m\equiv 1 \pmod p$, 关于 $X$ 的方程 $X^m-1\equiv 0\pmod p$ 有 $p-1$ 个根. 而 $m$ 次多项式在域上至多有 $m$ 个零点 ==(Fraleigh Abs 8e, 推论 28.6)==, 这蕴含 $p-1 \le m$.

拉格朗日定理 ==(Fraleigh Abs 8e, 定理 10.7, 10.9)== 给出, 对任意 $x$ 有 $\mathrm{ord}(x) \mid p-1$. 也就是说, $p-1$ 是 $\left\{\mathrm{ord}(x)\right\}$ 的一个公倍数. 这蕴含 $m\mid p-1$. 至此 $m=p-1$.

子命题的叙述隐含 $\mathbb{F}_p^*$ 是有限交换群, 证明省略. 有限交换群一定存在阶为 $m$ 的元素 ==(Fraleigh Abs 8e, 习题 6.67(b), 反复应用)==. 子命题证毕.

用类似的方式可以证明 $\mathbb{F}_n^*$ 是 $n-1$ 阶循环群.

### 子命题: 存在模 $p$ 非平凡三次单位根

检验 $p$ 的数值得 $3 \mid (p-1)$. 取 $\mathbb{F}_p^*$ 的生成元 $g$, 构造 $\alpha=g^{(p-1)/3}$, 则有 $\alpha^3\equiv 1\pmod p$. 此外, $\mathrm{ord}(\alpha)=\frac{p-1}{\gcd{}(p-1, (p-1/3))}=3$, 因此 $\alpha \ne 1$. 子命题证毕.

模仿上述过程, 可以证明存在模 $n$ 三次单位根.

### 命题 (1)

已经证明存在量词是成立的. 现在只需将 $(\alpha x, y)$ 代入曲线方程 $y^2\equiv x^3+7\pmod p$, 确认等式成立. 命题证毕.

### 命题 (2)

设函数 $\phi(x, y) = (\alpha x, y)$, $\phi(O)=O$. 我们先证明如下几个子命题, 再回来证命题 (2).

### $\phi$ 具有加法同态性: $\phi(P+Q)=\phi(P)+\phi(Q)$

设 $P+Q=-R$. 根据点的加法的定义, 有 $P, Q, R$ 三点共线. $\phi$ 对坐标进行线性变换, 因此 $\phi(P)$, $\phi(Q)$, $\phi(R)$ 仍然共线, 从而有 $\phi(P)+\phi(Q) = -\phi(R)$. 取负作用于纵坐标, 而 $\phi$ 仅作用于横坐标, 因此 $-\phi(R)=\phi(-R)$.

若 $P=Q$, 则直线为 $P$ 点处的切线, 重复上一段论证. 子命题证毕.

### 引理: $\phi(kP)=k\cdot\phi(P)$

递归应用同态性, 即证得本引理.

### $\phi$ 是三阶的: $\phi^3(P)=P$

这里上标 3 意味着复合 3 次, 即 $\phi (\phi (\phi(P)))$, 也写作 $\phi\circ \phi\circ \phi(P)$.

由 $\alpha^3 x \equiv x \pmod p$ 得出 $\mathrm{ord}(\phi) \mid 3$. 标准基点 $G$ 横坐标非零, 前文已证 $\alpha \ne 1$, 所以 $\phi(G)\ne G$. 因此 $\phi \ne \mathrm{id}$. 子命题证毕. 

### 回到命题 (2)

我们设曲线点的生成元为 $G$. 设 $\phi(G)=\lambda G$. 系数 $\lambda$ 必然存在, 因为 $G$ 能够生成任何点.

再设任意点 $P=dG$. 则有 $\phi(P)$ $=\phi(dG)$ $=d\phi(G)$ $=d\lambda G$ $=\lambda P$. 此时证出系数 $\lambda$ 对任意 $P$ 是常量.

$\phi^3(G)=G$ 得出 $\lambda^3\equiv 1 \pmod n$. $\phi(G)\ne G$ 得出 $\lambda \ne 1$. 命题证毕.

### 问题 (3)

求解 $\alpha$ 的方法为: 均匀随机取 $u\in\mathbb{F}_p^*$, 计算 $\alpha = u^{(p-1)/3} \bmod p$. 若 $\alpha=1$ 则换一个 $u$ 重试. 成功概率 2/3.

求解 $\lambda$ 的方法类似, 保留使 $\phi(P)=\lambda P$ 的 $\lambda$.

### 问题 (4)

典型应用: GLV 加速标量乘法.

计算 $kP$ 需处理 256-bit 标量. GLV 把 $k$ 分解为
$$
k\equiv k_1+k_2 \lambda \pmod n,
$$
使得 $\left| k_1 \right|, \left| k_2 \right| < 2^{128}$. 本文为了简化讨论, 不考虑 $k_1, k_2$ 为负数的情况. 具体的分解算法详见

```
libsecp256k1::secp256k1_scalar_split_lambda(...)

https://github.com/bitcoin-core/secp256k1/blob/master/src/scalar_impl.h
```

分解之后, $kP=k_1P+k_2\phi(P)$. 收益为: 倍点算法的迭代数从至多 256 降到至多 128. 每轮迭代的逻辑从
$$
R_{t+1}\leftarrow 2R_t + (k.b_t)\,P,
$$


变成:
$$
R_{t+1}\leftarrow
2R_t + (k_1.b_t)\,P + (k_2.b_t)\,\phi(P).
$$
