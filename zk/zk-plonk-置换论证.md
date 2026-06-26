PLONK 有两类约束: 

* 门约束只管一个门, 即 $q_L a + q_R b + q_M ab + q_O c + q_C = 0$. 本文不再赘述.
* 连线约束 (copy constraint) 管 "第 1 行的输出要喂给第 2 行的输入" 这类跨格相等, 由一条独立的置换论证 (permutation argument) 保证.

读这篇笔记只需盯住两个问题:

1. 第一部分: 要刻画哪些约束? 
2. 第二部分: 约束如何变成 (秘密) 多项式?

第三部分把结果接回主协议. 全文以 PLONK 笔记里 $x^3 + x + 5 = 35$ 的轨迹表为底子.

-----
-----



# 一. 要刻画哪些约束

## 1.1 约束的来源: 电路连线

轨迹表 (行号从 0 起, 对齐 $\omega^0, \dots, \omega^3$):

| 行 $i$ | 类型 | $a$ | $b$ | $c$ |
|:-:|:-:|:-:|:-:|:-:|
| 0 | 乘 | 3 | 3 | 9 |
| 1 | 乘 | 9 | 3 | 27 |
| 2 | 加 | 27 | 3 | 30 |
| 3 | 加 | 30 | 5 | 35 |

门约束让每行成立, 但行与行之间毫无关系. 电路语义却要求数据顺线流动: 第 0 行算出的 $9$ 必须传给第 1 行的左输入, 第 1 行的 $27$ 必须传给第 2 行的左输入, 依此类推. 把所有 "同一根线的两端" 列出, 就是连线需求. (纯由电路拓扑决定, 与具体值无关):

$$
c_0 = a_1, \qquad c_1 = a_2, \qquad c_2 = a_3.
$$

## 1.2 约束的精确形式: 置换不变

把上式看作格子之间的一条边, 所有边把格子划成若干等价类. 同类的格子具有相等的值, 这意味着所有格子的值在某个置换 $\sigma$ 下不变. 设 $v_i$ 是格子 $i$ 的取值, 于是整篇笔记要刻画的约束就是:
$$
\forall i,\quad v_i=v_{\sigma_i}. \tag{perm}
$$

## 1.3 $\sigma$ 从哪来

$\sigma$ 完全由电路拓扑决定, 与 witness & 与秘密 $x$ 无关. setup 阶段算一次, 永久公开复用. 三步:

(a) 格子编号. $3n = 12$ 个格子线性编号, 按列分块:

| | 行0 | 行1 | 行2 | 行3 |
|:-:|:-:|:-:|:-:|:-:|
| $a$ | 0 | 1 | 2 | 3 |
| $b$ | 4 | 5 | 6 | 7 |
| $c$ | 8 | 9 | 10 | 11 |

三条连线需求翻成编号间的相等: $8 = 1$, $9 = 2$, $10 = 3$ (即 $c_0 = a_1$ 等).

(b) 并查集求等价类. 把相等当无向边, 连通分量即等价类. 跑完得到非平凡类

$$
\{1, 8\}, \quad \{2, 9\}, \quad \{3, 10\} ,
$$

其余格子各自成单点类 (不动点).

(c) 每类成环得 $\sigma$. 把每个类首尾相接连成一个环, $\sigma$ 是所有环的乘积. 本例都是 2 元类 (对换):

$$
\sigma = (1\ 8)\,(2\ 9)\,(3\ 10) .
$$

写成全表 $\sigma(i)$:

| $i$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| $\sigma(i)$ | 0 | 8 | 9 | 10 | 4 | 5 | 6 | 7 | 1 | 2 | 3 | 11 |



# 二. 约束如何刻画成多项式

## 2.0 总览: 哪些多项式, 谁公开谁秘密

整组连线约束最终被压进**一条新的秘密多项式 $z(X)$**. 这是本部分的终点. 先把全部涉及的多项式摊在桌上:

| 多项式 | 公开 / 秘密 | 谁生成 | 编码什么 |
|---|:-:|:-:|---|
| $a(X), b(X), c(X)$ <br> (即 $w_a, w_b, w_c$) | 秘密 | Prover | 三列 witness 取值; $w_{\text{col}}(\omega^i)$ 是格子 $(\text{col}, i)$ 的值 $v_{\text{cell}}$ (门约束部分就有) |
| $\text{id}(\text{col}, i)$ | 公开 | 双方各算 | 每格的原始位置标签 ($k_a\omega^i, k_b\omega^i, k_c\omega^i$, 无需承诺) |
| $S_{\sigma a}, S_{\sigma b}, S_{\sigma c}$ | 公开 (预处理) | Setup | $\sigma$ 把每格映到的目标位置标签 |
| $z(X)$ | 秘密 | Prover | 整组连线约束的 grand product 累加 |

读法: $a, b, c$ 装 witness, 是门约束带来的. $\text{id}$ 和 $S_\sigma$ 是描述 $\sigma$ 的公开脚手架. 真正为连线约束新引入的秘密多项式只有 $z(X)$ 一条.

## 2.1 公开脚手架: 位置标签 id 与 $S_\sigma$

要 "谈论格子的位置", 先给每格赋予一个独特 (不重复) 的名字. 它是定义在格子上的函数 $\text{id}(\text{列}, \text{行})$. 用陪集编码: 取常数 $k_a, k_b, k_c$ 使三个集合 $k_a\Omega,\ k_b\Omega,\ k_c\Omega$ 两两不相交. 如此,
$$
\begin{aligned}
\text{id}(a, i) &= k_a\omega^i,\\
\text{id}(b, i) &= k_b\omega^i, \\
\text{id}(c, i) &= k_c\omega^i .
\end{aligned}
$$
"列前缀 $k_a / k_b / k_c$" 指明哪一列, "行根 $\omega^i$" 指明哪一行, 合起来唯一定位一格, $3n$ 个标签全不同.

我们用三条预处理多项式 $S_{\sigma a}, S_{\sigma b}, S_{\sigma c}$ 编码置换 $\sigma$. 我们先把 $\sigma$ 重载为两参数版本:

```
sigma(col_src, row_src) = (col_dst, row_dst)
```

然后我们定义 $S_{\sigma a}(\omega^i)$ 为 "把 $(a, i)$ 置换过去, 取它的标签", 即:

$$
S_{\sigma a}(\omega^i) = \text{id}\big( \sigma(a, i) \big) .
$$

🧠 读者自行手算一下, 多项式 $S_{\sigma a}$ 过如下四个点 
$$
(\omega^0, 1), (\omega^1, k_c), (\omega^2, k_c\omega), (\omega^3, k_c\omega^2)
$$
找到多项式 $S_{\sigma a}$ 的样本点之后, 插值或 IFFT 就能得到 $S_{\sigma a}$ 的解析式. 用类似的办法计算 $S_{\sigma b}, S_{\sigma c}$.

## 2.2 置换不变性等价于多重集相等.

记 $v_{\text{cell}}$ 为格子里装的值, 即 §1.2 的 $v_i$, 这里改按 (列, 行) 索引同一个量. "$\sigma$ 是带值格子的重排" 等价于两个多重集相等:

$$
\Big\{\big(
v_{\text{cell}},\ \text{id}(\text{cell}) 
\big)\Big\} = 
\Big\{\big(
v_{\text{cell}},\ \text{id}(\sigma(\text{cell})) 
\big)\Big\} .
$$

回顾多重集合相等: 元素种类及重复数相等.

左边给每个值配它的原始标签, 右边配它被 $\sigma$ 挪到的标签. 因标签单射, 两集相等当且仅当 $v_{\text{cell}} = v_{\sigma(\text{cell})}$, 正是问题 1 的约束.

## 2.3 多重集相等几乎等价于连乘约束.

利用 Schiwartz-Zippel 定理, 把多重集相等压缩为一个连乘约束.

首先需要引入挑战 $\beta$. 把元组 $(v, \text{id})$ 投影到域元素 $v+\beta\cdot\text{id}$. 对于随机 $\beta$, 这种投影几乎不可能产生碰撞. 于是, 以元组为元素的多重集合相等, 就简化为标量的多重集合相等. 这一步依赖 §2.1 几个陪集两两不相交.

然后需要引入挑战 $\gamma$. 根据定理, 给定随机 $\gamma$, 两个多重集相等 $\{p_i\} = \{q_i\}$, 几乎等价于 $\prod_i (p_i + \gamma) = \prod_i (q_i + \gamma)$.

两个随机挑战把 "多重集相等" 压成 "一个连乘等于 1":

* $\beta$: 把对 $(v, \text{id})$ 压成域元素 $v + \beta \cdot \text{id}$. 随机 $\beta$ 下不同对几乎不碰撞, 于是 "对的多重集相等" $\Leftrightarrow$ "压扁后标量的多重集相等". (这一步全靠 2.1 的标签单射, 否则压扁就丢位置.)
* $\gamma$: 两个多重集 $\{p_i\} = \{q_i\}$ 几乎等价于 $\prod_i (p_i + \gamma) = \prod_i (q_i + \gamma)$ (随机 $\gamma$, Schwartz–Zippel).

接下来, 给每一列构造两个多项式, 分别代表置换前和置换后的多重集合. 下式是多项式的采样点, 其中 $w_a = a$, 列 b, c 以此类推.
$$
\begin{aligned}
f_{\text{col}}(\omega^i) 
&= w_{\text{col}}(\omega^i) + \beta\, \text{id}(\text{col}, i) + \gamma , \\
g_{\text{col}}(\omega^i) 
&= w_{\text{col}}(\omega^i) + \beta\, \text{id}(\sigma(\text{col}, i)) + \gamma.
\end{aligned}
$$

最后得到连乘约束
$$
\prod_{i=0}^{n-1} \frac{f_a(\omega^i)\, f_b(\omega^i)\, f_c(\omega^i)}{g_a(\omega^i)\, g_b(\omega^i)\, g_c(\omega^i)} = 1 . \tag{GP}
$$

## 2.4 把连乘约束转化为秘密多项式

连乘约束没法直接抽查. 我们引入待求多项式 $z(X)$, 设多项式 $F = f_a f_b f_c$, $G = g_a g_b g_c$. 定义:

$$
\begin{aligned}
z(\omega^0) &= 1, \\
z(\omega^{i+1}) &= z(\omega^i) \cdot \frac{F(\omega^i)}{G(\omega^i)} .
\end{aligned}
$$

这既是 $z(X)$ 的递推定义, 又是 $z(X)$ 在 $\Omega$ 上的取值样本. Prover 仍然需要用 Lagrange / IFFT 求出 $z(X)$ 的解析式.

Verifier 关心以下两条约束在 $\Omega$ 上成立.
$$
\begin{align}
L_0(X)\, \big( z(X) - 1 \big) &= 0 , \tag{con1}\\
z(X)\, F(X) - z(\omega X)\, G(X) &= 0. \tag{con2}
\end{align}
$$

其中 $L_0$ 是在 $\omega^0$ 取 1、其余根取 0 的 Lagrange 基. 这两行虽都写成 "在 $\Omega$ 上恒零", 但逐点读才看得清各自在说什么.

第一条约束是为了钉住起点. 当 $X=\omega^0$ 时, $L_0=1$, 因子 $z(\omega^0) - 1$ 起效, 约束 $z(\omega^0)=1$. 当 $X=\omega^j$ ($j\ne 0$) 时, $L_0=0$, 因子 $z(\omega^i) - 1$ 爱咋咋地.

第二条约束是为了钉住递推步. 这里的妙笔是 $z(\omega X)$, 这意味着它在 $X=\omega^i$ 取下一个样本 $z(\omega^{i+1})$. 第二条约束的核心意图就在于
$$
z(\omega^i)\, F(\omega^i) - z(\omega^{i+1})\, G(\omega^i) = 0 .
$$
两条恒等式 (cond1, cond2) 左边都在 $\Omega$ 上全零, 这意味着它们都能被 $Z_\Omega(X) = X^n - 1$ 整除. 这与 PLONK 笔记中的公式 (gx-pri) 机制相同.



# 三. 合并进主协议

门约束 $G_{\text{gate}}$ 与两条置换恒等式用随机 $\alpha$ 加权合并成单条 ($\alpha$ 的不同幂次分配互不干扰的通道):

$$
\begin{aligned}
&\phantom{{}={}}G_{\text{gate}}(X) + \alpha \big( z F - z(\omega X) G \big) + \alpha^2 L_0 (z - 1) \\
&= Z_\Omega(X)\, t(X) .
\end{aligned}
$$

协议就是 PLONK 笔记 Step 5 那套四阶段, 只多承诺一条 $z$、多开一个旋转点:

1. 承诺 $a, b, c$ $\to$ 导出 $\beta, \gamma$ (Fiat–Shamir).
2. 承诺 $z$ (此时 $\beta, \gamma$ 已定, $z$ 才算得出) $\to$ 导出 $\alpha$.
3. 承诺 $t$ (含 $zF$, 次数约 $3n$, 实务切段承诺) $\to$ 导出抽查点 $\zeta$.
4. 打开 $a(\zeta), b(\zeta), c(\zeta), S_{\sigma a}(\zeta), S_{\sigma b}(\zeta), z(\zeta), z(\omega\zeta)$, 附 KZG / IPA 取值证明.
5. 验证: 确认取值真来自承诺, 代入合并恒等式, 检查左边 $= t(\zeta) \cdot (\zeta^n - 1)$.

💡 唯一新意是 $z(\omega\zeta)$: 递推式引用 "下一行", 故 $z$ 在 $\zeta$ 和 $\omega\zeta$ 两点被打开.

-----
-----

# 附录

## 附 A: 三个挑战的分工与时序

| 挑战 | 作用 |
|:-:|---|
| $\beta$ | 把 (值, 位置) 绑成一个域元素, 锁定 "值 $\leftrightarrow$ 标签" 配对 |
| $\gamma$ | 把多重集相等随机化成连乘 |
| $\alpha$ | 把门约束与两条置换约束批成一条恒等式 |

Fiat–Shamir 次序即可靠性来源: $\beta, \gamma$ 必须在 $a, b, c$ 承诺**之后**才出现, 否则 Prover 能照挑战定制 witness 去凑; $z$ 在 $\beta, \gamma$ 后; $\zeta$ 在 $z$ 后. 每个随机量都晚于它要约束的承诺 —— 和 IPA 笔记里 "$x_j$ 必须在固定 $L_j, R_j$ 之后" 同一种时序论证.

## 附 B: 预处理产物清单

setup 一次性算出, 只依赖电路拓扑, 与 witness 和秘密输入无关, 同一电路永久复用:

* 置换 $\sigma$ (union-find + 成环).
* $S_{\sigma a}, S_{\sigma b}, S_{\sigma c}$ (对目标标签向量做 IFFT).
* 它们的承诺 $\text{Com}(S_{\sigma\_})$, 连同门参数承诺进 verifying key 公开.
