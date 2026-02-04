$$
\begin{align}
a_1 &= g_p^{s_r} \\
a_2 &= h^{s_r}f^{s_m} \\
z_r &= s_r+er \\
z_r' &= s_r+e'r \\
\tilde{z}_r &= (e-e')r \\
\tilde{z}_m &= (e-e')x_1 \\
c_1^\tilde{e} &= g_p^{(e-e')r} \\
c_2^\tilde{e} &= (h^r f^{x_1})^\tilde{e}
               =h^{(e-e')^r}\cdot f^{(e-e'){x_1}} \\
c_1' &= g_p^{\tilde{e}r} \\
c_2' &= h^{\tilde{e}r}f^{\tilde{e}m} \\
\frac{c_2'}{(c_1')^d} &= f^{\tilde{e}m}
\end{align}
$$

💡 $c_1', c_2'$ 都可以表示成 $g$ 的幂；前文有说 $g$ 是 $G$ 的生成元。因此，表达式 $c_2'/c_1'$ 看起来是除法，实际上是幂的减法。

## 1.2. 技术概述

(1) 从密码学角度回顾类域的"接口"。

* $G$ 是 $\mathrm{CL}(\Delta_p)$ 中最大奇数阶的子群。$G$ 有 >97% 的概率是循环群。
* $F$ 是 $G$ 中唯一的 $p$ 阶循环子群。这里，$p$ 等于 secp256k1 曲线的阶。$F$ 的元素记为 $(p^2, xp)$。这个记号实际上是二次型，省略了第三个参数。
* $G/F$ 同构于 $G_p=\left\{x\in G \mid x=g^p\right\}$。该群的阶未知，理论上界为 $U$。

(2) 传统的 sigma 协议无法证明 $(r, m)$ 的见证。

当应用传统的 sigma 协议时，会得到一个记录：

* 证明者说：$a_1=g^{s_r}, a_2=h^{s_r}f^{s_m}$ 和 $c_1=g^r, c_2=h^rf^m$。
* 验证者说：随机 $e$。
* 证明者说：$z_r=s_r+er, z_m=s_m+em\bmod p$。
* 验证者检查：$g^{z_r}=a_1c_1^e, h^{z_r}f^{z_m}=a_2c_2^e$。

然而，<mark>如果恶意证明者持有阶整除 $e$ 的低阶元素 $g'$</mark>，并提供 $c_1'=g'c_1, c_2'=g'c_2$；那么对于任何 $r, m$，验证总是为真。

我的计算：
$$
\begin{align}
g^{z_r}&=g^{s_r+er},\\
a_1c_1'^e&=g^{s_r}g'^e g^{re}=g^{s_r+er}g'^e=g^{s_r+er}.
\end{align}
$$
问题在于 $c_1' = g'g^r$ 和 $c_2' = g'h^rf^m$ **并不**对应于随机数 $r$ 下消息 $m$ 的 ElGamal 加密。相反：
- $c_1'$ 需要等于某个 $r'$ 的 $g^{r'}$，
- $c_2'$ 需要等于某个 $m'$ 的 $h^{r'}f^{m'}$。

但如果 $g'$ 不在 $g$ 生成的子群中，那么这样的 $r', m'$ 就不存在。

总而言之，当证明者提供 $c_1', c_2'$ 时，他们实际上是在为一个格式错误的密文证明知识，该密文根本不是正确的 ElGamal 加密。

## 3. Promise $\Sigma$-协议

定义 6 涉及一些零知识概念。辨析如下：

* **模拟器**：用于展示**零知识性质**，确保验证者除了语句的有效性之外什么都学不到。
* **提取器**：用于展示**可靠性性质**，确保证明者无法说服验证者接受虚假语句。




密码学中的"验证"大多利用了**同构性**。

验证 $z_m$ 的原理。
$$
\begin{align}
z_mG &= (s_m+em)G \\
&=s_mG+emG \\
&=A+eQ
\end{align}
$$
验证 $z_r$ 的原理。
$$
\begin{align}
g_p^{z_r}&=\mathrm{pow}(g_p,s_r+er) \\
&=\mathrm{pow}(g_p,s_r)\cdot\mathrm{pow}(g_p,er) \\
&=a_1\cdot (g_p^r)^e \\
&=a_1\cdot c_1^e
\end{align}
$$

$$
\begin{align}
h^{z_r}f^{z_m}
&=\mathrm{pow}(h,s_r+er)\cdot \mathrm{pow}(f,s_m+em) \\
&=h^{s_r}h^{er}f^{s_m}f^{em} \\
&=h^{s_r}f^{s_m}h^{er}f^{em} \\
&=h^{s_r}f^{s_m}(h^rf^m)^e \\
&=a_2\cdot c_2^e
\end{align}
$$

使用 Typora 编辑

## SigmaProm2协议 注解

首先明确一个问题，什么叫"明文相等"？这个问题来自于逻辑而不是内容：明文只有一个，也就是 $m$，它何来相等一说？通过询问 GPT 和 Google，我相信作者想说的是"不同算法的密文来自相同的明文"。这实际上是明文的等价性或一致性。

明确作者的确切意图之后，就得到一个技术问题。<mark>给定两个不同算法的密文，如果没有密钥，如何判断它们对应相同的明文？</mark>

### 知识铺垫

$C_2$ 是 $m$ 的 EC ElGamal 加密，$c_2$ 是 $m$ 的 CL ElGamal 加密。

文章并没有说 ElGamal 加密的一般形式。我在维基上查了一下，整理出一般形式如下：
$$
\begin{align}
\mathtt{Alice::~~}& x:=\mathrm{Rand}(G);~~ y=g^x \\
\mathtt{Bob::~~}& r:=\mathrm{Uni}(\mathrm{ord}(G));~~ c_1=g^r;~~ c_2=m\cdot y^r \\
\mathtt{Alice::~~}& m=c_2\cdot(c_1^x)^{-1}
\end{align}
$$
对于 EC ElGamal 来说，通常表示成数乘形式，并假设加密的不是 $m$，而是 $m$ 的可逆编码 $F(m)$。虽然我很好奇如何把数 $m$ <mark>可逆地</mark> 映射到点 $F(m)$，但是暂且放一放，假设存在这样的方法。如此，EC ElGamal 具有如下一般形式：
$$
\begin{align}
\mathtt{Alice::~~}& x:=\mathrm{Uni}(n);~~ H=xG \\
\mathtt{Bob::~~}& r:=\mathrm{Uni}(n);~~ C_1=rG;~~ C_2=F(m)+rH \\
\mathtt{Alice::~~}& F(m)=C_2-xC_1 \\
\mathtt{Alice::~~}& m=F^{-1}(F(m))
\end{align}
$$
💡 注意 ElGamal 中的 $\cdot(c_1^x)^{-1}$ 在 EC ElGamal 中变成了 $-xC_1$。一定要保持清醒：一般循环群中的"乘法"和求逆，在加法循环群中是加法和减法。

### 正式开始讲协议

第一步：在证明者一侧，执行
$$
\begin{align}
s_1 &:= \mathrm{Uni}(\mathbb{Z}_p) \\
s_2 &:= \mathrm{Uni}[0,U) \\
s_m &:= \mathrm{Uni}(\mathbb{Z}_p) \\
A_1,~A_2 &:= s_1G,~s_1P+s_mG \\
a_1,~a_2 &:= g_p^{s_2},~h^{s_2}f^{s_m} \\
&\mathtt{send}(\mathcal{V},A_1,A_2,a_1,a_2).
\end{align}
$$
第二步：在验证者一侧，执行
$$
\begin{align}
e &:= \mathrm{Uni}(\mathbb{Z}_p)\\
&\mathtt{send}(\mathcal{P},e).
\end{align}
$$
第三步：在证明者一侧，执行
$$
\begin{align}
z_1 &:=(s_1+er_1)~\mathrm{mod}~p \\
z_m &:=(s_m+em)~\mathrm{mod}~p \\
z_2 &:=s_2+er_2 \\
&\mathtt{send}(\mathcal{V}, z_1,z_m,z_2).
\end{align}
$$
第四步：在验证者一侧，验证
$$
\begin{align}
& 0 \le z_2 < U+(p-1)S \\
& z_1G=A_1+eC_1 \\
& z_1P+z_mG=A_2+eC_2 \\
& g_p^{z_2}=a_1c_1^e \\
& h^{z_2}f^{z_m}=a_2c_2^e ~.
\end{align}
$$
若这些条件都满足，则验证者宣布接受证明。

至此，我又产生了一个疑问：<mark>如果证明者故意用两个 $m$，比如用 $m_1$ 算 $C_2$，用 $m_2$ 算 $c_2$，那么验证者仍然能验算通过，以上协议不就失效了吗？</mark>

动笔演算之后想通了：验证者只收到了一个 $z_m$。所以如果 $C_2, c_2$ 来自不同的明文 $m_1,m_2$，那么验证者不论收到哪一个 $m_i$ 所对应的 $z_m$，因为总是少一个 $m_i$，所以必然验不过。

## 顺便辨析概念

明文与密文相对。明文不一定公开，甚至往往是私密的。一定要保持清醒，不要受"明"字的误导。

换个角度想，如果明文公开，那么何必加密？

# SigmaProtocol 3

前文对 $\mathcal{L}_\mathrm{affine}$ 的描述非常高冷。实际上，里面带"撇"的密文，等价于对明文 $m^\prime=am+b$ 进行加密。

如此，协议 3 的公共输入所提到的密文 $C'$，其对应的明文是 $m^\prime=am+b$。

## 第一步：在证明者一侧，计算承诺并发送给验证者

$$
\begin{align}
s_a &:=\mathrm{Uni}(pS) \\
(s_b,s_r) &:= \mathrm{Uni}(\mathbb{Z}_p) \\
A_1 &:= s_aC_1+s_rG \\
A_2 &:= s_aC_2+s_bG+s_rP \\
a_1 &:= c_1^{s_a} \\
a_2 &:= c_2^{s_a}f^{s_b} \\
&\mathtt{send}(\mathcal{V}, A_1, A_2, c_1, c_2)
\end{align}
$$

上述公式里，$(A_1, A_2)$ 是对 $(s_am+s_b)$ 的同态加密。实际上，
$$
\begin{align}
A_1 &= s_ar_1G+s_rG \\
    &= (s_ar_1+s_r)G, \\
A_2 &= s_a(r_1P+mG)+s_bG+s_rP \\
    &= (s_am+s_b)G+(s_ar_1+s_r)P.
\end{align}
$$
类似地，$(a_1, a_2)$ 也是对 $(s_am+s_b)$ 的同态加密。实际上，
$$
\begin{align}
a_1 &= g_p^{s_ar_2},\\
a_2 &= h^{s_ar_2}f^{s_am}f^{s_b}\\
    &= h^{s_ar_2}f^{s_am+s_b}.
\end{align}
$$

## 第二步：在验证者一侧，摇出随机挑战并发送给证明者

$$
\begin{align}
e &:= \mathrm{Uni}(\mathbb{Z}_p)\\
&\mathtt{send}(\mathcal{P},e).
\end{align}
$$

## 第三步：在证明者一侧，响应挑战

$$
\begin{align}
z_a &:= s_a+ea \\
z_b &:= s_b+eb \\
z_r &:= s_r+er \\
&\mathtt{send}(\mathcal{V},z_a,z_b,z_r)
\end{align}
$$

## 第四步：在验证者一侧，验证响应

这一步检查四个等式是否成立。每个表达式的左右两边在以不同的结合性计算 $(s_a+ea)m+(s_b+eb)$ 的 ElGamal 加密。

我们分析前两个等式
$$
\begin{align}
z_aC_1+z_rG &= (s_a+ea)r_1G+(s_r+er)G \\
&= ((s_a+ea)r_1+s_r+er)G ~~, \\
A_1+eC_1' &= (s_ar_1+s_r)G+e(aC_1+rG) \\
&= (s_ar_1+s_r)G+e(ar_1+r)G \\
&= ((s_a+ea)r_1+s_r+er)G ~~.
\end{align}
$$

$$
\begin{align}
z_aC_2+z_bG+z_rP
&= (s_a+ea)(r_1P+mG)+(s_b+eb)G+(s_r+er)P \\
&= \Big[(s_a+ea)m+(s_b+eb)\Big]G  \\
&\hspace{1em}+ \Big[(s_a+ea)r_1+(s_r+er)\Big]P ~~,\\

A_2+eC_2' &=
(s_am+s_b)G+(s_ar_1+s_r)P \\
&\hspace{1em}+ e(a(r_1P+mG)+bG+rP) \\
&=\Big[(s_a+ea)m+(s_b+eb)\Big]G  \\
&\hspace{1em}+ \Big[(s_a+ea)r_1+(s_r+er)\Big]P ~~.
\end{align}
$$

## 阶段 1

​	参与方 $\mathcal{P}_i$ 生成 $k_i, \gamma_i$，与其他各参与方用 $\Sigma_\mathrm{prom}^2$ 协议证明确实生成了 $k_i$。

## 阶段 2

​	参与方 $\mathcal{P}_i$ 在 CL ElGamal 信道与其他各方交换如下两个表达式。这里下标 $j,i$ 代表"从 $i$ 到 $j$"。
$$
\begin{align}
F_\alpha &= k_j(\gamma_i+\hat{t}_{j,i})-\beta_{j,i} \\
F_\mu &= k_j(w_i+t_{j,i})-v_{j,i}
\end{align}
$$
​	然后，其他各参与方 $\mathcal{P}_j$ 计算如下两个表达式。这里，符号"$\equiv$"表示事实等价，不代表 $\mathcal{P}_j$ 能知道任何下标为 $i$ 或 $j,i$ 的变量。强调一下：$\mathcal{P}_j$（理论上）到底知道什么，只取决于 $\mathcal{P}_i$ 给他发了什么，也就是长箭头上面的东西。
$$
\begin{align}
\alpha_{j,i} &= F_\alpha-k_j\hat{t}_{j,i} \equiv k_j\gamma_i-\beta_{j,i} \\
\mu_{j,i} &= F_\mu - k_jt_{j,i} \equiv k_jw_i-v_{j,i}
\end{align}
$$
​	最后，$\mathcal{P}_i$ 计算如下两个表达式。回忆：公式 $\eqref 2$ 中的 $w_i=\lambda_ix_i$，也就是插值后的私钥分片。可以合理推断，$W_i=w_iG$。
$$
\begin{align}
\delta_i&=k_i\gamma_i+\sum_j^{j\neq i}(\alpha_{i,j}+\beta_{j,i}) \\
&\equiv k_i\sum_j\gamma_j ~-~ \sum_j^{j\neq i}\beta_{i,j} ~+~ \sum_j^{j\neq i}\beta_{j,i} \\
&\equiv k_i\gamma ~-~ \sum_j^{j\neq i}\beta_{i,j} ~+~ \sum_j^{j\neq i}\beta_{j,i}
\end{align}\tag{1}\label{1}
$$

$$
\begin{align}
\sigma_i&=k_iw_i+\sum_j^{j\neq i}(\mu_{i,j}+v_{j,i}) \\
&\equiv k_i\sum_jw_j ~-~ \sum_j^{j\neq i}v_{i,j} ~+~ \sum_j^{j\neq i}v_{j,i} \\
&\equiv k_ix ~-~ \sum_j^{j\neq i}v_{i,j} ~+~ \sum_j^{j\neq i}v_{j,i}
\end{align} \tag{2}\label{2}
$$

## 阶段 3

​	计算 $\delta=\sum_i\delta_i=k\gamma$。这里 $k=\sum_i k_i, \gamma=\sum_i \gamma_i$。

​	提示：在求和过程中，公式 $\eqref 1$ 中的正负 $\beta_{i,j}$ 被消掉了。

## 阶段 4

​	利用 $R=\delta^{-1}(\sum_i \Gamma_i)$ 得到签名字段 $r$。这里 $\Gamma_i\equiv \gamma_iG$。

## 阶段 5

​	聚合签名：$s_i=mk_i+r\sigma_i, s=\sum_i s_i$。

​	公式推导
$$
\begin{align}
&\hspace{1em}\sum_j U_j \\
&= \sum_j\rho_j\sum_i\big((mk_i+r\sigma_i)R+l_iG\big) \\
&\equiv \sum_j\rho_j\sum_i\big( (mk_i+r\sigma_i)k^{-1}+l_i\big)G \\
\mathrm{by~\eqref{2}}& \equiv \sum_j\rho_j\Big(mG+rQ+\sum_i V_i\Big) \\
&=\sum_j\rho_j\sum_il_iG ~~=\sum_il_iA
\end{align}
$$

