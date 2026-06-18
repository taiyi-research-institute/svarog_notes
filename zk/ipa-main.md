# IPA 取值证明: Fiat-Shamir 非交互版本

> 场景接在朴素协议的第 3 轮: prover 已承诺多项式 $f(X)$ 为 $C_f$ , 挑战点 $\zeta$ 已定, prover 宣称 $f(\zeta) = v$ , 现在要产出一条**单向发送**的取值证明. 交互版每轮需要 verifier 回一个随机挑战, 共 $\log_2 n$ 轮; Fiat-Shamir 用哈希替代 verifier 的全部随机性, 把这些轮次折叠进一条证明串.

---

## 0. 记号与信息归属

设 $n-1$ 为多项式的次数, 且 $n = 2^k$ ($k$ 是折叠总轮数, $k = \log_2 n$).

下标约定:

- $i$ : 向量内的位置, 从 $0$ 到 $n - 1$ .
- $j$ : 折叠轮次编号, 从 $1$ 到 $k$ .
- $L$ 与 $R$ : 一条向量的前半与后半.

| 对象 | 谁生成 | 谁知道 |
|---|---|---|
| 系数向量 $\mathbf{f} = ( f_0, \dots, f_{n-1} )$ | prover | 仅 prover |
| 生成元 $\mathbf{G} = ( G_0, \dots, G_{n-1} )$ 与 $U$ | 公开哈希导出 | 双方 |
| $C_f = \langle \mathbf{f}, \mathbf{G} \rangle$ | prover | 双方 |
| $\zeta$ , $v$ | 协议上层 | 双方 |
| $\mathbf{b} = ( 1, \zeta, \zeta^2, \dots, \zeta^{n-1} )$ | 双方各自从 $\zeta$ 算出 | 双方 |
| 哈希函数 $\mathrm{Hash}$ | 协议规范 | 双方 |

## 1. 声明打包

把 "承诺对" 和 "取值对" 两条声明捏成一个群元素. 双方各自计算
$$
P_0 = C_f + v \cdot U .
$$
待证声明: prover 知道 $\mathbf{f}$ , 使得

$$
P_0 = \langle \mathbf{f}, \mathbf{G} \rangle + \langle \mathbf{f}, \mathbf{b} \rangle \, U . \tag{P0}
$$
后续每一轮折的就是这条声明. 实务中 $U$ 还会先乘一个挑战标量以防跨项干涉, 此处省略以免干扰理解, 不影响结构.

## 2. Fiat-Shamir: 用哈希替代 verifier

交互版中, 第 $j$ 轮挑战 $x_j$ 必须在 prover 固定 $( L_j, R_j )$ **之后**才出现, 否则 prover 可针对挑战凑交叉项. Fiat-Shamir 把这个时序约束改由哈希实现:

$$
\begin{align*}
x_j &= \mathrm{Hash} \big( \text{transcript}_j \big), \\ \text{transcript}_j &= \big( C_f, \zeta, v, L_1, R_1, x_1, \dots, L_j, R_j \big) .
\end{align*}
$$
即 $x_j$ 是 "截至本轮交叉项为止的全部公开通信记录" 的哈希. 想先看 $x_j$ 再改 $L_j, R_j$ 是循环依赖: 改交叉项会改哈希输入, 进而改掉 $x_j$ 本身. 于是 prover 可以**独自**按顺序推进全部 $k$ 轮, 不需要任何对方消息.

## 3. Prover 算法

初始化: $\mathbf{f}^{(0)} = \mathbf{f}$ , $\mathbf{G}^{(0)} = \mathbf{G}$ , $\mathbf{b}^{(0)} = \mathbf{b}$ , 长度 $n$ .

对轮次 $j = 1, 2, \dots, k$ 依次执行:

### (1) 切半

把当前三条向量各按前半 / 后半切开: $\mathbf{f}^{(j-1)} = ( \mathbf{f}_L \,\|\, \mathbf{f}_R )$ , $\mathbf{G}^{(j-1)} = ( \mathbf{G}_L \,\|\, \mathbf{G}_R )$ , $\mathbf{b}^{(j-1)} = ( \mathbf{b}_L \,\|\, \mathbf{b}_R )$ .

### (2) 算交叉项

$$
\begin{align*}
L_j &= \langle \mathbf{f}_L, \mathbf{G}_R \rangle 
+ \langle \mathbf{f}_L, \mathbf{b}_R \rangle \, U, \\
R_j &= \langle \mathbf{f}_R, \mathbf{G}_L \rangle
+ \langle \mathbf{f}_R, \mathbf{b}_L \rangle \, U .
\end{align*}
$$

### (3) 导出挑战

把 $( L_j, R_j )$ 吸收进 transcript, 然后计算
$$
x_j = \mathrm{Hash} ( \text{transcript}_j ).
$$

### (4) 对折

$$
\begin{align*}
\mathbf{f}^{(j)} &= \mathbf{f}_L + x_j \, \mathbf{f}_R, \\ \mathbf{G}^{(j)} &= \mathbf{G}_L + x_j^{-1} \, \mathbf{G}_R, \tag{fold-G} \\ 
\mathbf{b}^{(j)} &= \mathbf{b}_L + x_j^{-1} \, \mathbf{b}_R 
\tag{fold-b}.
\end{align*}
$$

$k$ 轮后 $\mathbf{f}^{(k)}$ 塌缩成单个标量, 记为 $a$. 最终证明为
$$
\pi=
\big( L_1, R_1, \, L_2, R_2, \, 
\dots, \, L_k, R_k, \; a \big).
$$
通信: $\pi$ 里共 $2 k$ 个群元素加 $1$ 个域元素, 发给 verifier.

## 4. Verifier 算法

> 🤔 我要验 $\pi$ (法国赌神口音)

verifier 收到 $\pi$ 后做四件事.

### (1) 重放挑战

用同一条 transcript 规则依次算出 $x_1, \dots, x_k$ . 由于哈希输入全是公开量, 双方算出的挑战必然一致. 若 prover 在证明里伪造过任何 $L_j, R_j$, 后续挑战会全部错位.

### (2) 重放折叠后的声明 $P_j$

verifier 没有 $\mathbf{f}$, 它折的是声明本身:
$$
P_j = x_j^{-1} L_j + P_{j-1} + x_j \, R_j , \qquad j = 1, \dots, k . \tag{Pj}
$$
上述公式怎么来的? 详见 [这篇文档](./ipa-eq(Pj).md).

### (3) 自行折叠公开向量

Verifier 大不了跟 Prover 一样采用公式 (fold-b) 和公式 (fold-G). 但是有效率更高的办法.

对于 $\mathbf{b}$ , 因为它是结构化的幂次向量, 折到底有如下闭合形式, 只需$O ( \log n )$ 次标量运算.
$$
b^{*} = \prod_{j=1}^{k} \big( 1 + x_j^{-1} \, \zeta^{\, 2^{\, k - j}} \big). \tag{b-final}
$$
$\mathbf{G}$ 没有这种结构, 折到底有如下形式.
$$
G^{*} = \sum_{i=0}^{n-1} s_i \, G_i , \qquad s_i = \prod_{j=1}^{k} x_j^{- m_j ( i )}.
$$
其中 $m_j ( i ) \in \{ 0, 1 \}$ 是位置编号 $i$ 的二进制表示中第 $j$ 位 ( $j = 1$ 对应最高位, 因为第一轮按前半 / 后半切, 切的正是最高位 ) . 这一步是 $O ( n )$ , 是 IPA 验证线性的全部来源.

### (4) 做出判断

$$
P_k \ \overset{?}{=}\ a \, G^{*} + a \, b^{*} \, U .
$$

若等式成立, 则相信 Prover 确实持有 $f$ 使 $f ( \zeta ) = v$ .

注: $a$ 是 Prover 提交的 $\pi$ 的其中一项. 详见 3.4 节



## 5. 成本汇总 ( $G$ 为群元素, $F$ 为域元素 )

| | 交互轮数 | 证明大小 | verifier 工作量 |
|---|---|---|---|
| KZG | 1 <br />(单条消息) | $1 \, G$ | $O ( 1 )$ : 两次配对 |
| IPA + Fiat-Shamir | 1<br />(单条消息, 内嵌 $k$ 轮被哈希替代的对话) | $2 k \, G + 1 \, F$ | $k$ 次哈希 + $O ( \log n )$ 标量+ $O ( n )$ 多标量乘 |

交互轮数没有消失, 而是被折叠进了证明长度与哈希重放. IPA 换来的唯一东西是无可信设置; 第三列那个 $O ( n )$ 多标量乘, 正是 Halo 用 accumulation 摊销的对象 —— 把它从每次验证中延迟, 累加, 只在递归链末端结一次账.



## 附录 

### Appx.1 解释公式 (Pj)

公式 (Pj) 并不显然. 这里以输入 $n=4$, 输出 $n=2$ 为例解释一下.

设 $f = ( f_0, \dots, f_3 )$ , $G = ( G_0, \dots, G_3 )$ , $b = ( \zeta^0, \dots, \zeta^3 )$. 

切半后:

$$
\begin{align*}
f_L &= ( f_0, f_1 ) , & f_R &= ( f_2, f_3 ) ,\\
G_L &= ( G_0, G_1 ) , & G_R &= ( G_2, G_3 ) , \\
b_L &= ( \zeta^0, \zeta^1 ) , & b_R &= ( \zeta^2, \zeta^3 ) .
\end{align*}
$$
旧声明:

$$
\begin{align*}
P_0 &= ( f_0 G_0 + \dots + f_3 G_3 ) \\
&\phantom{{}={}}
+ ( f_0 \zeta^0 + \dots + f_3 \zeta^3 ) \cdot U .
\end{align*}
$$
交叉项:

$$
\begin{aligned}
L &= ( f_0 G_2 + f_1 G_3 ) + ( f_0 \zeta^2 + f_1 \zeta^3 ) \cdot U , \\
R &= ( f_2 G_0 + f_3 G_1 ) + ( f_2 \zeta^0 + f_3 \zeta^1 ) \cdot U .
\end{aligned}
$$

---

对折后的新向量 (长度从 4 变成 2) :

$$
\begin{aligned}
f' &= ( f_0 + x f_2 , \; f_1 + x f_3 ) , \\
G' &= ( G_0 + x^{-1} G_2 , \; G_1 + x^{-1} G_3 ) , \\
b' &= ( \zeta^0 + x^{-1} \zeta^2 , \; \zeta^1 + x^{-1} \zeta^3 ) .
\end{aligned}
$$

新声明的右边如下. 我们即将彻底展开它.

$$
P' = \langle f', G' \rangle + \langle f', b' \rangle \cdot U
$$
第一步, 把两个内积按定义写开:

$$
\begin{aligned}
&\phantom{{}={}} P' \\
&= ( f_0 + x f_2 )( G_0 + x^{-1} G_2 ) + ( f_1 + x f_3 )( G_1 + x^{-1} G_3 ) \\
& \cdots\cdots \ \langle f', G' \rangle \\
&+ \big( ( f_0 + x f_2 )( \zeta^0 + x^{-1} \zeta^2 ) + ( f_1 + x f_3 )( \zeta^1 + x^{-1} \zeta^3 ) \big) \\
& \cdots\cdots \ \langle f', b'\rangle \\
&\phantom{.}\bullet\phantom{.} U.
\end{aligned}
$$

第二步, 按 $x$ 的幂次分桶整理:

$$
\begin{aligned}
&\phantom{{}={}} P' \\
&= (f_0 G_0 + \dots + f_3 G_3) \\
&+ x \, ( f_2 G_0 + f_3 G_1 ) \\
&+ x^{-1} ( f_0 G_2 + f_1 G_3 ) \\
&+ \big( ( f_0 \zeta^0 + \dots + f_3 \zeta^3 ) \\
&\phantom{+}+ x \, ( f_2 \zeta^0 + f_3 \zeta^1 ) \\
&\phantom{+}+ x^{-1} ( f_0 \zeta^2 + f_1 \zeta^3 ) \big) \cdot U.
\end{aligned}
$$

三个桶各自的归属:

- $x^0$ (不带 $x$) 桶 $= ( f_0 G_0 + \dots + f_3 G_3 ) + ( f_0 \zeta^0 + \dots + f_3 \zeta^3 ) U$ , 恰好是 $P_0$ .
- $x^{-1}$ 桶 $= ( f_0 G_2 + f_1 G_3 ) + ( f_0 \zeta^2 + f_1 \zeta^3 ) U$ , 恰好是 $L$ .
- $x^{1}$ 桶 $= ( f_2 G_0 + f_3 G_1 ) + ( f_2 \zeta^0 + f_3 \zeta^1 ) U$ , 恰好是 $R$ .

于是

$$
P' = P_0 + x^{-1} L + x R.
$$
