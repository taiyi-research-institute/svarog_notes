---
title: "随机 VOLE"
---

# 0. 铺垫

回顾 [SoftSpokenOT](./05-softspoken.md), 其 Sender 得到 $L$ 对 OT 密钥, Receiver 得到相应的 $L$ 个单侧密钥.  对第 $j$ 实例, $j \in [0, L)$,

* Sender 持有成对密钥 $\rho^0_j, \rho^1_j$, 不知 Receiver 选哪一边.
* Receiver 持有选择位 $\beta_j\in\left\{0,1\right\}$, 所选密钥 $\rho^{\beta_j}_j$, 不知另一个密钥 $\rho_j^{1-\beta_j}$.

记号约定: $\vec\beta \in \left\{0,1\right\}^L$ 指选项串本身 (即 [SoftSpokenOT](./05-softspoken.md) 的 $\beta$); 不带箭头的 $\beta := \sum_{j\in[0,L)}\beta_j g_j \pmod n$ 专指它的 gadget 加权聚合 ([杂记：gadget 向量](./misc-gadget.md)).

拿到这些密钥后, 兑现随机 MtA 关系 $y + z := w\beta \pmod n$. 其中 Sender 输入 $w$, 输出 $y$; Receiver 输入 $\beta$, 输出 $z$.

注意: 本协议不兑现 ECDSA MtA 关系 $y + z := wx \pmod n$. DKLs23 把消除 $\beta$ 的工作交给 ECDSA 编排层, 这是一个安全手段.

安全在哪? 若直接让 Receiver 输入选定值 $x$, 选择串就是 $x$ 的编码, 恶意 Sender 对个别实例 $j$ 掺假即可发动 selective failure —— 协议 abort 与否泄露该位 $\beta_j$, 也就是泄露 $x$ 的比特. 换成随机 $\vec\beta$ 后有两重保险: 其一, $\vec\beta$ 一次一换, 泄露不跨会话累积; 其二, gadget 编码留有 $2\lambda_s$ 比特富余熵 ($L = \kappa + 2\lambda_s = 512$), 即便个别 $\beta_j$ 败露, 聚合值 $\beta$ 对 Sender 仍统计均匀 (DKLs23 援引的依据是 Impagliazzo-Naor 子集和引理).

[协议编排](./07-orchestration.md) 描述了如何将 $w\beta$ 替换成 $wx$.

兑现 MtA 关系有以下两种思路.

## 0.1. 朴素路线: 对消息进行加密

Sender 构造 OT 消息:

$$

\begin{align*}
M^0_j &:= r_j \stackrel{\$}{\leftarrow}\mathbb{Z}_n,\\
M^1_j &:= r_j + w\cdot g_j \pmod{n}.
\end{align*}

$$

把密钥直接加到消息上, 形成密文:

$$

\begin{align*}
C^0_j &:= \rho^0_j + M^0_j, \\
C^1_j &:= \rho^1_j + M^1_j.
\end{align*}

$$

Receiver 用所持的 $\rho^{\beta_j}_j$ 解开 $C^{\beta_j}_j$, 得

$$

M^{\beta_j}_j = r_j + \beta_j\cdot w\cdot g_j.

$$

Sender 和 Receiver 分别聚合出自己的加法秘密份额. 聚合采用 gadget 方式, 详见 [杂记：gadget 向量](./misc-gadget.md).

$$

\begin{align*}
y &:= -\sum_j  r_j \pmod{n}, \\
z &:= \sum_j M^{\beta_j}_j \pmod{n}.
\end{align*}

$$

协议至此结束. 通信量: 对每个 OT 槽位, Sender 发 2 个密文 $C^0_j, C^1_j$.

## 0.2. 另类路线: 把密钥直接解读为随机数

既然消息和密钥都是随机的, 我们不如把 $\rho_j^0, \rho_j^1$  直接当成 $\mathbb{Z}_n$ 标量用. 定义

$$

\alpha_j^0,\alpha_j^1 := \rho_j^0, \rho_j^1 \pmod n.

$$

Sender 拥有 $\alpha_j^0,\alpha_j^1$, 以及秘密因子 $w$. Receiver 拥有 $\alpha_j^{\beta_j}$, 以及秘密因子 $\beta$.

对每个 OT 实例 $j$, 也就是 gadget 分解后的第 $j$ 分量,

Sender 发送修正量:

$$

\tilde a_j := \alpha^0_j - \alpha^1_j + w \pmod{n}.

$$

Sender 和 Receiver 分别聚合出自己的加法秘密份额:

$$

\begin{align*}
y &:= -\sum_j g_j\cdot\alpha^0_j \pmod{n}, \\
z &:= \sum_j g_j\left(\alpha^{\beta_j}_j + \beta_j\tilde a_j\right) \pmod{n}.
\end{align*}

$$

注意到 $\alpha^{\beta_j}_j + \beta_j\tilde a_j = \alpha^0_j + \beta_j w \pmod n$, 读者凭此公式自行验算. 

协议至此结束. 通信量: 对每个 OT 槽位, Sender 发送 1 个标量 $\tilde a_j$.

另类路线的好处:
* 节省通信带宽
* Sender 消息不依赖 gadget 向量 $\big(g_j \mid j\in[0,L)\big)$.

-----

# 1. RVOLE 协议核心版

RVOLE 完全版有三个索引维度: OT 实例 $j$, 检查编号 $k$, MtA 关系编号 $i$ 或 $k$. 维度太多会干扰认知. 本章描述单个负载且无检查的 RVOLE 协议.

## 1.1. 规格

输入: Sender 持有秘密 $w$, Receiver 持有秘密 $\beta=\sum_{j\in[0,L)} \beta_j \cdot g_j$.

输出: Sender 获得 $y$, Receiver 获得 $z$, 使得

$$

y + z := w \cdot \beta \pmod{n}.

$$

## 1.2. 实施

### 1.2.(1) Sender 发送修正项, 获得加法份额

Sender 把 OT 密钥 $\rho^0_j$ 转换为随机标量 $\alpha^0_j\in\mathbb{Z}_n$. 同理, 把 $\rho^1_j$ 转换为随机标量 $\alpha^1_j\in\mathbb{Z}_n$. 然后构造修正项:

$$

\tilde{a}_{j} = \alpha^0_{j} - \alpha^1_{j} + w \pmod{n}.

$$

计算自己的加法份额:

$$

y = -\sum_j g_j \cdot \alpha^0_j \pmod n.

$$

Sender 发送 $\tilde{a}_j$, 本地保存 $y$.

### 1.2.(2) Receiver 获得加法份额

Receiver 对每个 $j$ 计算自己的份额:

$$

\begin{align*}
t_j &:= \alpha^{\beta_j}_j+\beta_j\cdot\tilde{a}_j \pmod n, \\
\textrm{a.k.a.~} t_j &= \alpha^0_j + \beta_j \cdot w \pmod n.
\end{align*}

$$

Receiver 计算 $z$ 份额:

$$

z := \sum_j g_j \cdot t_j \pmod{n}.

$$

本章协议结束.

-----

# 2. RVOLE 协议完全版

恶意 Sender 可能对不同的 OT 实例 $j$ 使用不同的 $w' \neq w$, 破坏 MtA 关系 $y + z = w \cdot \beta \pmod n$ 的正确性. 为此, 我们约定每个 OT 实例携带 $N_2$ 个负载用于校验. DKLs23 论文取 $N_2 = 1$. 

决定引入校验维度以后, 将使 RVOLE 内部运算变得向量化. 既然如此, 不妨继续引入 $(N_1-1)$ 个 MtA 关系. 对于 ECDSA 签名, 有 $N_1=2$.

综上, 完全版的协议兑现如下 $N_1$ 个 MtA 关系:

$$

y_{i}+z_{i} := w_{i}\cdot \beta \pmod n,
\quad i \in [0,\, N_1).
\tag{batch-mta}

$$

## 2.1. 规格

输入:

* Sender 持有 $N_1$ 个秘密因子 $w_i$, $i \in [0, N_1)$. 协议内部他再自采 $N_2$ 个新鲜随机校验因子 $w_k$, $k \in [N_1, N_1+N_2)$.
* Receiver 持有秘密选项串 $\vec\beta \in \left\{0,1\right\}^L$; 这意味着他持有相应的秘密因子 $\beta=\sum_{j\in[0,L)} \beta_j \cdot g_j$.

输出: Sender 获得 $N_1$ 个秘密加项 $y_i$. Receiver 获得 $N_1$ 个秘密加项 $z_i$, 使得等式 (batch-mta) 成立.

安全承诺:

* $w_i$ 对 Receiver 保密, 零泄露.
* $\vec\beta$ 对 Sender 保密. 允许的泄露: 恶意 Sender 可按位赌个别 $\beta_j$, 代价是每位 $1/2$ 概率 abort; 无论赌多少位, 加权和 $\beta$ 对 Sender 仍统计均匀 (距离 $\le 2^{-\lambda_s}$).

逐条核对见 2.3 节.

## 2.2. 实施

索引: 协议有 $L$ 个 OT 实例, 用 $j$ 索引. 每个 OT 实例携带 $N_1+N_2$ 个负载, 用 $k$ 或 $i$ 索引.

### 2.2.(1) Sender 获得加法份额

对每个 OT 实例 $j\in [0, L)$ 和负载 $k\in[0, N_1+N_2)$, Sender 对 OT 密钥 $\rho_j^b$ 进行衍生, 得到:

$$

\alpha^b_{j,k}:=\mathtt{PRF}\left(
\mathtt{sid},j,k, \rho^b_j
\right),
\quad
b\in\left\{0,1\right\}.

$$

对同样的 $j, k$, 计算相应的修正项:

$$

\tilde{a}_{j,k} := \alpha^0_{j,k}-\alpha^1_{j,k}+w_{k}.
\tag{offset}

$$

对同样的 $j$ 和每个功能负载 $i \in [0, N_1)$, Sender 计算加法份额:

$$

y_{i}:=-\sum_j g_j\cdot \alpha^0_{j,i} ~.

$$

至此 Sender 已得到全部的输出 $y_i, i\in[0, N_1)$.

### 2.2.(2) Sender 响应挑战, 发送消息

定义矩阵 $\tilde a := \left\{ \tilde a_{j,k}~:~ j\in [0, L),\, k\in [0, N_1+N_2) \right\}.$

本节剩余内容中, $j\in[0, L)$, 也就是索引每个 OT 实例; $k\in[N_1, N_1+N_2)$, 也就是索引每个校验负载.

对每个 $k$, Sender 计算挑战向量 $\theta_k \in \mathbb{Z}_n^{N_1}$:

$$

\theta_k:=\mathrm{Hash}(\mathtt{sid},\, k,\, \tilde a).
\tag{ch}

$$

然后计算线性响应:

$$

\eta_k := w_{k}+\sum_{i\in[0,N_1)}\theta_{k,i}\cdot w_{i} \pmod n,
\tag{resp-lin}

$$

并定义向量 $\eta := \left\{ \eta_k ~:~  \forall k\right\}$.

以及计算哈希响应:

$$

\begin{align*}
\mu_{j,k} &:= \alpha^0_{j,k}
+\sum_{i\in[0,N_1)}\theta_{k,i}\cdot \alpha^0_{j,i}, \\

\mu &:= \mathrm{Hash}\left(\mathtt{sid},\, \left\{\mu_{j,k} ~:~ \forall j,k\right\}\right).
\end{align*}
\tag{resp-ha}

$$

最后, Sender 发送 $\tilde a$, $\eta$, $\mu$.

### 2.2.(3) Receiver 验证挑战, 获得加法份额

在本节, $j\in[0, L)$ 索引每个 OT 实例; $i\in[0, N_1)$ 索引每个功能负载. 注意 $t_{j,k}$ 要对**全部**负载 $k \in [0, N_1+N_2)$ 计算 —— 校验公式和输出都要用到功能负载的 $t$; 只有 $\theta_k, \eta_k, \hat\mu_{j,k}$ 的 $k$ 限于校验负载 $[N_1, N_1+N_2)$.

对每个 $j$ 和全部负载 $k \in [0, N_1+N_2)$, Receiver 对 OT 密钥 $\rho_j^{\beta_j}$ 进行衍生, 得到

$$

\alpha^{\beta_j}_{j,k}:=\mathtt{PRF}\left(
\mathtt{sid},j,k, \rho^{\beta_j}_j
\right).

$$

然后用收到的 $\tilde a_{j,k}$ 计算

$$

\begin{align*}
t_{j,k} &:= \alpha^{\beta_j}_{j,k}+\beta_j\cdot \tilde{a}_{j,k}, \\
&= \alpha^0_{j,k}+\beta_j\cdot w_{k}~,
\end{align*}
\tag{tjk}

$$

以及对每个校验负载 $k \in [N_1, N_1+N_2)$ 计算公式 (ch), 得到所有 $\theta_k$.

之后, 对每个 $j$ 和每个校验负载 $k$, 计算 $\hat\mu_{j,k}$ 和 $\hat{\mu}$ 如下式, 检验 $\hat\mu\stackrel{?}{=}\mu$.

$$

\begin{align*}
\hat\mu_{j,k} &:= t_{j,k} 
+ \sum_{i\in[0,N_1)} \theta_{k,i}\cdot t_{j,i}
- \beta_j\cdot\eta_k, \\

\hat\mu &:= \mathrm{Hash}\left(\mathtt{sid},\, \left\{\hat\mu_{j,k} ~:~ \forall j,k\right\}\right).
\end{align*}

$$

如果检验通过, 那么 Receiver 对每个功能负载 $i$ 计算本地份额

$$

z_{i} := \sum_{j}g_j\cdot t_{j,i} ~.

$$

最后, Receiver 本地保存 $z_{i}$.

## 2.3. 核对安全承诺

### 2.3.1 $w_i$ 对 Receiver 零泄露

Receiver 的视图为: 单侧 OT 密钥 + Sender 的唯一消息 $(\tilde a, \eta, \mu)$. 逐项检查是否含有 $w$ 的信息.

根据公式 (offset), $\tilde\alpha_{j,i}$ 含有 $w_i$, 但 Receiver 总是缺少 $\alpha_{j,i}^{1-\beta_j}$, 并且 $\alpha_{j,i}^?$ 是会话新鲜的, 因而 $w_i$ 被 $(\alpha_{j,i}^0-\alpha_{j,i}^1)$ 遮蔽.

根据公式 (resp-eta), $\eta_k$ 含有关于 $w_i$ 的线性组合, 但被新鲜随机的 $w_k$ 遮蔽.

$\mu$ 不含 $w_k$.

### 2.3.2 $\vec\beta$ 对 Sender 保密, 泄露有上限

Receiver 的 $\vec\beta$ 进入 Sender 视图的唯一方式是 "abort 与否" 这一个比特.

诚实 Sender 恒通过. 而对于作弊 Sender, 每个受攻击的实例 $j$ 至多泄露一个 $\beta_j$, 其只有一比特; 代价是 1/2 概率当场 abort. 即便若干 $\beta_j$ 败露, [杂记：gadget 向量](./misc-gadget.md) 的 $2\lambda_s$ 富余熵保证聚合值 $\beta$ 仍统计均匀. 况且 $\vec\beta$ 一次一换, 泄露不跨会话累积.

-----

# 附录 A. 这种挑战是怎么想到的?

本附录复盘 2.2 节 "挑战-响应" 的设计过程, 展示它不是天降神来之笔, 而是由若干 "思维脚手架" 搭建出来的.

## A.1. 给出作恶/诚实的形式化描述

Sender 在本协议只发一条消息 $(\tilde a, \eta, \mu)$. 其中 $\eta, \mu$ 恰是被检查的对象, 所以真正的作弊自由度全在 $\tilde a$ 里. 观察 (offset): Sender 知道全部 $\alpha^0_{j,k}, \alpha^1_{j,k}$, 所以他发出的**任意** $\tilde a_{j,k}$ 都可以反解出一个 "等效输入"

$$

w_{j,k} := \tilde a_{j,k} - \alpha^0_{j,k} + \alpha^1_{j,k} \pmod n.

$$

诚实当且仅当对每个 $k$, 都有 $\forall (j_1, j_2), w_{j_1,k}=w_{j_2,k}$ .

## A.2. 用 "公共基准" 回答 "两两相等"

Receiver 能直接比较两行吗? 他手里只有 $t_{j,k} = \alpha^0_{j,k} + \beta_j \cdot w_{j,k}$. 两行相减:

$$

t_{j_1,k} - t_{j_2,k} = \left(\alpha^0_{j_1,k} - \alpha^0_{j_2,k}\right) + \left(\beta_{j_1} w_{j_1,k} - \beta_{j_2} w_{j_2,k}\right),

$$

两行的 pad 是各自独立的随机数, 消不掉. 直接对比的思路行不通. 问题化归: 一列内部两两相等 iff 全列等于同一个公共值.

化归以后, 需要把举证责任推给 Sender, 让他申报这个公共值 $c_k$. 若第 $j$ 行确实用了申报值 $c_k$, 则根据公式 (tjk) 有

$$

t_{j,k} - \beta_j \cdot c_k = \alpha^0_{j,k}.

$$

若 Sender 实际用的是 $c_k + e$ ($e \neq 0$), 则 Receiver 的实算值 = 预测值 $+ \beta_j e$. 此时 Sender 要想蒙混过关, 就必须猜 $\beta_j$. 这就是整个检查的骨架: 诚实时两侧恒等且与 $\vec\beta$ 无关, 作弊时差一个 $\beta_j$ 相关项, Sender 猜不中 (类似于 [KOS15 恶意安全](./02-kos15.md) 抓恶意 Receiver 的思路).

到此, "申报 + 逐行对照" 已经能检查一列. 剩两个问题: 功能列的公共值就是秘密 $w_i$, 不能明着申报 (A.3, A.4 解决); 申报必须先于挑战固定 (A.5 解决).

## A.3. 随机线性组合

功能列不能逐列照搬 A.2 —— 申报公共值就泄露了 $w_i$. 经典技巧: 不逐列检查, 而是检查它们的随机线性组合列, 第 $j$ 行的组合值为

$$

w_{j,k} + \sum_{i\in[0,N_1)} \theta_{k,i}\, w_{j,i}.

$$

关键性质: 对随机 $\theta$, 组合列是常数列 $\iff$ (以压倒性概率) 每个参与列都是常数列.

于是对组合列套用 A.2 的 "申报 + 逐行对照", 2.2 节的三条公式有了直观意义:

* 申报组合列的公共值: $\eta_k = w_k + \sum_i \theta_{k,i} w_i$, 即 (resp-lin);
* 承诺各行预测值: $\mu_{j,k} = \alpha^0_{j,k} + \sum_i \theta_{k,i}\alpha^0_{j,i}$, 即 (resp-ha);
* Receiver 逐行实算 $t_{j,k} + \sum_i \theta_{k,i} t_{j,i} - \beta_j \eta_k$ 与承诺比对, 即 $\hat\mu_{j,k}$.

## A.4. 牺牲负载

A.3 的组合列为什么要混入校验列 $w_{j,k}$ 本身? 若组合只取功能列, 申报值就是 $\eta_k = \sum_i \theta_{k,i} w_i$ —— 泄露了功能秘密 $w_i$ 的一个线性方程 ($\theta$ 公开). 标准补丁是牺牲 (sacrifice): 加一个新鲜随机的 $w_k$ 进组合, 充当一次一密掩码.

妙处在于掩码的投放渠道: $w_k$ 作为第 $k$ 个负载**搭乘同一批 OT** 传输, 于是 Receiver 手里自动有 $t_{j,k} = \alpha^0_{j,k} + \beta_j w_k$, 能在自己那侧把掩码对应的项一并消掉, 完全不需要额外机制. 这就是"校验负载"与"功能负载"共用 (offset) 同一公式的原因 —— 校验负载不是另一种东西, 就是一个被烧掉的 MtA 关系.

## A.5. 第三件工具: Fiat-Shamir 定序

$\theta$ 必须在 Sender 固定 $\tilde a$ (等价于固定全部 $w_{j,k}$) **之后**才可知, 否则 Sender 可解方程挑出恰好过检的作弊. 交互版由 Receiver 摇 $\theta$; DKLs23 用 RO 压掉这轮交互: $\theta_k := \mathrm{Hash}(\mathtt{sid}, k, \tilde a)$, 消息定挑战, 与 [SoftSpokenOT](./05-softspoken.md)、[杂记：Fiat-Shamir](./misc-fiat-shamir.md) 同一处理.

可靠性核算. 作弊 Sender 想过检只有两条路:

* **磨 RO (grinding)**: 反复重选 $\tilde a$, 祈祷摇出的 $\theta$ 恰好使所有偏差组合为零 ($e_{j,k} := w_{j,k} + \sum_i \theta_{k,i} w_{j,i} - \eta_k = 0$ 对所有 $j$). 对固定的不一致 $\tilde a$, 随机 $\theta$ 命中该超平面的概率 $\approx 1/n = 2^{-\lambda_c}$. 这解释了 $N_2 = \lceil \kappa/\lambda_c\rceil$: 若挑战系数取自小域 (每格只有 $2^{\lambda_c'}$ 种), 就要 $\lceil \kappa/\lambda_c' \rceil$ 个校验负载凑够 $\kappa$ 位可靠性; 满域标量一格即够.
* **赌 $\beta_j$**: 接受某些 $e_{j,k} \neq 0$, 直接猜那些位上的 $\beta_j$ 来伪造 $\mu_{j,k} = \hat\mu_{j,k} - \beta_j e_{j,k}$. 每个受攻击位赌中概率 $1/2$, 赌错即 abort (μ 是全体格子的哈希, 一格错全盘错). 这是压不掉的残余 —— selective failure, 由 [杂记：gadget 向量](./misc-gadget.md) 的 $2\lambda_s$ 富余熵兜底.

## A.6. 构造配方总结

1. 把对手的全部作弊自由度参数化为对某恒等式的**加性偏差** (A.1);
2. 把 "两两相等" 化归为 "对照申报的公共基准", 逐行检验 Sender 可预测的残差 (A.2);
3. 秘密列不能明着申报, 用**随机线性组合**把它们捆进一个可申报的组合列 (A.3);
4. 组合会泄露秘密的线性方程, 加**新鲜牺牲负载**做一次一密, 且让掩码搭乘同一相关性通道 (A.4);
5. 用 **Fiat-Shamir** 从承诺消息导出挑战, 固定"先承诺后挑战"的顺序 (A.5);
6. 算清两本账: 挑战域大小 ⇒ grinding 界; 消不掉的偏差 ⇒ selective failure, 交给上游熵富余 (A.5).

同型先例: KOS15 的一致性检查 (抓 Receiver)、SPDZ 的 triple sacrificing、Freivalds 矩阵乘法验证. RVOLE 的检查只是把这套骨架搬到"OT 密钥衍生的 pad"这个具体载体上.

-----

# 附录 B. $\tilde a$ 是什么密码学原语吗?

不是新原语. $\tilde a$ 是一条**消息**, 它做的事在文献里叫 **derandomization / correction**: 把随机 OT 兑换成选定关联. 可以从三个视角看它.

**视角一: 一次一密密文.** 固定 $(j,k)$, 有 $\tilde a_{j,k} = w_k + (\alpha^0_{j,k} - \alpha^1_{j,k})$, 即 $w_k$ 在密钥 $\alpha^0_{j,k} - \alpha^1_{j,k}$ 下的一次一密加密. Receiver 无论持哪一侧, 都恰好缺另一侧, 算不出这个差值密钥, 故 $w_k$ 保密. 但他能做一件比解密更弱、恰好够用的事: 把 $\tilde a$ 加到自己的单侧 pad 上, 得 $t = \alpha^0 + \beta_j w_k$ —— 解不出明文, 却拿到了明文的一个**加法份额**. 与 0.1 节朴素路线对比: 朴素路线加密两条消息 ($C^0, C^1$), 这里只发一个差值, 带宽减半.

**视角二: 随机 OT → 相关 OT 的兑换券.** 用 [IKNP03 OT 扩展](./01-iknp03.md) 的"等差"语言: SoftSpoken 交付的 $(\alpha^0_{j,k}, \alpha^1_{j,k})$ 是一对公差随机的数; 发送 $\tilde a_{j,k}$ 相当于宣布"请把公差修正为 $w_k$", 修正后 Receiver 持有的就是 correlated OT ($\Delta$-OT) 密钥 $t_{j,k} = \alpha^0_{j,k} + \beta_j \cdot w_k$ —— 单比特上的 VOLE 关系. 全体 $j$ 按 gadget 聚合, 就升级成 $\mathbb{Z}_n$ 上的 VOLE. 这个手法最早见于 Beaver 的 OT 预处理 (先离线囤随机 OT, 在线用修正词兑现选定输入), 同一个 correction word 结构也出现在 IKNP 的 $u$ 矩阵和 GGM/FSS 树的修正字里.

**视角三: 承诺.** 在附录 A 的检查里, $\tilde a$ 还兼任 Fiat-Shamir 的**首条承诺消息**: 它经由 (ch) 决定挑战 $\theta$, 从而把 Sender 的等效输入 $w_{j,k}$ 在挑战揭晓前钉死.

一句话总结: $\tilde a$ 不是原语, 而是"随机 OT 关联性 + 一次一密"拼出的修正消息; 它的保密性继承自 pad 的伪随机性 ($\alpha$ 是 OT 密钥过 PRF 的产物), 是计算性而非信息论的.

-----
