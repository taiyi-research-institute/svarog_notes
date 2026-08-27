---
title: "SoftSpokenOT"
---

[PPRF 与 GGM 树](./04-pprf.md) 把 $k$ 个二选一 Base OT 合成一棵 $q=2^k$ 叶的打孔树. 本篇是 [IKNP03 OT 扩展](./01-iknp03.md) 末节 "半诚实的边界" 第 (3) 条路线的正主: SoftSpokenOT 用 $\kappa/k$ 棵打孔树顶替 IKNP 的 $\kappa$ 行种子, 把半密钥 $u$ 的行数从 $\kappa$ 压到 $\kappa/k$, 拿计算量换带宽. 一致性检查沿用 [KOS15 恶意安全](./02-kos15.md) 的骨架: 承诺-挑战-响应, 再用 Fiat-Shamir 变换压成单条消息. 产出的随机 OT 密钥由 [随机 VOLE](./06-rvole.md) 兑换成 MtA.

参考: Roy, "SoftSpokenOT", CRYPTO 2022, https://eprint.iacr.org/2022/192. 本篇参数取 DKLs23 中的设置.

# 1. 接口规格串讲

SoftSpokenOT 协议是由 Base Endemic OT, PPRF, Extended OT 三个子协议依次串联而成的. 本章梳理三个子协议的输入、输出和参数. 同时标明子协议属于 ECDSA 的 Keygen 还是 Sign, 这意味着输出是否持久存储.

## 1.1. Base OT 的接口规格

ECDSA Keygen 阶段跑 $\kappa = 256$ 个 Base Endemic OT 实例 ([Endemic OT](./03-endemic-ot.md)). 对每个实例 $i\in [0, \kappa)$:

* Sender 得到两侧串 $\left(\rho_i^0, \rho_i^1\right)$, 其中 $\rho_i^b \in \left\{0,1\right\}^\lambda$.
* Receiver 得到选择位 $\beta_i$ 与单侧串 $\rho_i^{\beta_i}$.

⚠️ 正文将把 $\rho$ 重载为 Extended OT 的输出密钥 (与下游 [随机 VOLE](./06-rvole.md) 对齐). 类似地, 正文将把 $\beta$ 重载为 Extended OT 的选项.

## 1.2. PPRF 的接口规格

发生于 ECDSA Keygen 阶段, 紧跟 Base OT: 建好的树随 keyshare 持久落库, 供日后每次 Sign 反复取用.

每 $k = 4$ 个 Base (Endemic) OT 实例喂给 [PPRF 与 GGM 树](./04-pprf.md) 合成一棵 GGM 树, 共 $\kappa/k = 64$ 棵. 对于树编号 $i \in [0, \kappa/k)$:

* 叶子共 $q = 2^k = 16$ 片, 记为 $\mathcal{T}_{i,x} \in \left\{0,1\right\}^\lambda$, $x \in [0, q)$. 本篇笔记只需要叶子层, 故略去 [PPRF 与 GGM 树](./04-pprf.md) 的层上标, 把树编号挪进下标.
* PPRF Sender 持全部 $q$ 片叶子.
* PPRF Receiver 持 $q-1$ 片叶子, 缺打孔叶子 $\mathcal{T}_{i,\delta_i}$. 打孔下标 $\delta_i \in [0, q)$ 即 [PPRF 与 GGM 树](./04-pprf.md) 的 $\hat y$, 由他的 Base OT 选择位决定, 只有他知道.

(id-1-3-extended-ot)=
## 1.3. Extended OT 的接口规格

发生于 ECDSA Sign 阶段.

输入:

* SoftSpoken Receiver 持有 $\kappa/k$ 棵完整树 $\left\{\mathcal{T}_{i,x}\right\}$, $i\in [0, \kappa/k)$. 以及随机选项串 $\beta \in \left\{0,1\right\}^L$.
* SoftSpoken Sender 持有 $\kappa/k$ 棵打孔树. 具体来说, 持有非打孔节点值以及打孔下标.

输出:

* Sender 得到 $L$ (真实 OT 实例数) 对密钥 $\left(\rho^0_j,\, \rho^1_j\right)$, $j \in [0, L)$.
* Receiver 得到所选一侧 $\rho^{\beta_j}_j$.

Extended OT 是随机 OT: 两侧协商出随机密钥串, 真正的 payload 传输推迟到 [随机 VOLE](./06-rvole.md) 完成.

## 1.4. 参数表

|      参数      | 意义                                   | DKLs23 取值 |
| :----------: | ------------------------------------ | :-------: |
|   $\kappa$   | Base OT 实例数 = $v/w$ 矩阵行数             |    256    |
|  $\lambda$   | 叶子内容长度 (数值同 $\kappa$, 见 [PPRF 与 GGM 树](./04-pprf.md)) |    256    |
|     $k$      | 树深 = 每棵树吃掉的 Base OT 数                |     4     |
|  $q = 2^k$   | 每棵树的叶子数                              |    16     |
|     $L$      | 真实 OT 实例数                            |    512    |
|     $S$      | 陪跑段长度, 也是域 $\mathbb{GF}(2^S)$ 的位宽    |    128    |
| $L' = L + S$ | 扩展列数                                 |    640    |
|  $M = L/S$   | 挑战向量长度                               |     4     |

# 2. SoftSpoken 扩展 OT 协议

## 2.1. 规格

输入输出: 详见 [1.3. Extended OT 的接口规格](#id-1-3-extended-ot).

安全承诺:

* Sender 不知道 $\beta$.
* Receiver 不知道另一侧密钥 $\rho^{1-\beta_j}_j$.
* 一致性: Receiver 必须在所有行 (row) 使用同一个选项串, 掺假会被 1.2.(5) 抓住.

安全假设:

* 双方恶意. Receiver 掺假由挑战-响应防御. Fiat-Shamir 使得 Sender 无法指定挑战. Sender 的另一类作恶 (selective failure) 是另一条线, 见 [随机 VOLE](./06-rvole.md).
* PPRF 来历合规: [PPRF 与 GGM 树](./04-pprf.md) 的安全承诺未被破坏, 即: 打孔叶内容对本篇 Sender 均匀随机, 打孔位置对本篇 Receiver 保密.
* $\mathtt{PRG}$, $\mathtt{XOF}$, $\mathtt{Hash}$ 视作随机谕言机.

通信形态: 全程只有一条 Receiver $\to$ Sender 的消息. 原论文是三轮 Sigma 形 (Receiver 承诺, Sender 挑战, Receiver 响应), Fiat-Shamir 后压成一条, 同 [3.2. 实施](./02-kos15.md#id-3-2).

## 2.2. 实施

### 2.2.(1) Receiver 产生半密钥, 以及全密钥原像

Receiver 对第 $i, i \in [0, \kappa/k)$ 棵 PPRF 树:

延长和刷新叶子 $\mathcal{T}_{i, x}$, 得到 $r_{i,x}$.

$$

r_{i,x} := \mathtt{PRG}\left(\mathtt{sid},\, i,\, \mathtt{tag4},\, \mathcal{T}_{i,x}\right) \in \left\{0,1\right\}^{L'}.
\tag{leaf}

$$

💡 域分离参数: $\mathtt{tag4}$ 续接 [PPRF 与 GGM 树](./04-pprf.md) 的 $\mathtt{tag1}$~$\mathtt{tag3}$, 把叶子扩张与其他事由隔离开; 树编号 $i$ 顶替那篇的 $\mathtt{tid}$.

摇 $S$ 比特陪跑选项 $\beta^\mathrm{ext}$, 与真实选项 $\beta$ 拼接得到 $\hat\beta$.

$$

\hat\beta := \beta \,\|\, \beta^\mathrm{ext} \in \left\{0,1\right\}^{L'}.

$$

陪跑的作用详见 [3.2.(0) Receiver 延长选择向量](./02-kos15.md#id-3-2-0-receiver).

生成半密钥兼选项承诺 $u$.

$$

u_{i,*} := \hat\beta \oplus \sum_{x \in [0, q)} r_{i,x}.
\tag{umat}

$$

单侧全密钥原像: 矩阵 $v$ 的形状为 $\kappa\times L'$. 行号 $i' := ik + b$, 其中 $b \in [0, k)$ 用于索引叶子编号的比特位. 

$$

v_{i',*} := \sum_{x \in [0, q)} \mathrm{bit}_b(x)\cdot r_{i,x}. \tag{vmat}

$$

### 2.2.(2) 双方各自算 Fiat-Shamir 挑战

$$

\chi := \mathtt{XOF}(\mathtt{sid}, u) \in \mathbb{GF}(2^S)^M. \tag{chi}

$$

Receiver 此刻就能算, Sender 收到 $u$ 后也能算. 取 $S = 128$ 是为了让 $\mathbb{GF}(2^{128})$ 的乘法享受 AES 相关的硬件指令. 域运算详见 [杂记：F_2^k](./misc-f2k.md).

Fiat-Shamir 的收益不只是省一轮通信, 更在于: $\chi$ 被随机谕言机固定住, 双方都无法指定挑战. 详见 [3. 进阶版 KOS15](./02-kos15.md#id-3-kos15).

### 2.2.(3) Receiver 响应挑战, 进行唯一一轮通信.

把每行 $v_{i',*}$ 切成 $M+1$ 段, 每段 $S$ 比特: 前 $M$ 段记为 $\hat v_{i',j}$, $j \in [0, M)$, 末段记为 $v^\mathrm{ext}_{i'}$. 把 $\hat\beta$ 照同样 "刀法" 切段: 前 $M$ 段记为 $\hat\beta_j$, 末段恰好是陪跑选项 $\beta^\mathrm{ext}$. 各段视为 $\mathbb{GF}(2^S)$ 元素.

$$

\tau_{i'} := \left\{
    \sum_{j\in[0,M)} \chi_j \cdot\hat v_{i',j}
\right\}
\oplus v^\mathrm{ext}_{i'}. \tag{tau-mat}

$$

$$

\tilde\beta := \left\{
    \sum_{j\in[0,M)} \chi_j \cdot \hat\beta_j
\right\} \oplus \beta^\mathrm{ext}. \tag{beta-tilde}

$$

Receiver 把 $u,\tau,\tilde\beta$ 发给 Sender. SoftSpoken 子协议中仅此一轮通信.

### 2.2.(4) Sender 计算全密钥原像

Sender 首先需计算密钥原像 $w\in\left\{0,1\right\}^{\kappa\times L'}$. 对行 $i' = i\cdot k + b$, Sender 用手里的 $q-1$ 片叶子和收到的 $u_{i,*}$ 计算

$$

w_{i',*} := \left\{
    \sum_{x \in [0, q)}
    \mathrm{bit}_b(\delta_i \oplus x) \cdot r_{i,x}
\right\} 
~ \oplus ~
\mathrm{bit}_b(\delta_i) \cdot u_{i,*}.
\tag{wmat}

$$

式中获取 $r_{i,x}$ 的方式与 Receiver (leaf) 相同. 式中虽然无法获取 $r_{i,\delta_i}$, 但其系数 $\mathrm{bit}_b(\delta_i \oplus \delta_i) = 0$, 因而 Sender 能够计算上式.

引理: 对每行 $i'$, Sender 全密钥原像 $w$ 与 Receiver 全密钥原像 $v$ 满足如下关系

$$

w_{i',*} = v_{i',*} \oplus \mathrm{bit}_b(\delta_i) \cdot\hat\beta.
\tag{wv-row-eq}

$$

证明: 讨论 $\mathrm{bit}_b(\delta_i)$ 的两种取值.

取 0 时 $\mathrm{bit}_b(\delta_i \oplus x) = \mathrm{bit}_b(x)$, (wmat) 花括号项即为 $v$, 另一项为 0.

取 1 时 $\mathrm{bit}_b(\delta_i \oplus x) = 1 \oplus \mathrm{bit}_b(x)$. 进而, 花括号收集 $\mathrm{bit}_b(x)=0$ 的叶子; 另一项收集全部叶子, 同时引入异或项 $\mathrm{bit}_b(\delta_i)\cdot\hat\beta$. 进而, 等式左边 $\mathrm{bit}_b(x)=0$ 的叶子成对消去, 留下 $\mathrm{bit}_b(x)=1$ 的叶子 (即 $v_{i',*}$) 与 $\hat\beta$.    $\blacksquare$

引理: 对每一列 $j \in [0, L)$ 有

$$

w_{*,j} = v_{*,j} \oplus \beta_j \cdot \Delta, \tag{wv-eq}

$$

其中,

$$

\Delta := \delta_0 \,\|\, \delta_1 \,\|\, \cdots \,\|\, \delta_{\kappa/k - 1} \in \left\{0,1\right\}^{\kappa}.
\tag{delta}

$$

证明: $\Delta$ 的第 $i'$ 比特是 $\Delta_{i'} = \mathrm{bit}_b\left(\delta_i\right)$. 代入 (wv-row-eq) 即得 (wv-eq).  $\blacksquare$

重要结论: Sender 密钥原像的公差为 $\Delta$. 

### 2.2.(5) Sender 验证挑战

把每行 $w_{i',*}$ 照 1.2.(3) 的刀法切段, 得 $\hat w_{i',j}$ 与 $w^\mathrm{ext}_{i'}$, 然后逐行验证

$$

\left\{
    \sum_{j\in[0,M)} \chi_j\cdot\hat w_{i',j}
\right\}
\oplus w^\mathrm{ext}_{i'}
\stackrel{?}{=}
\tau_{i'}\oplus\Delta_{i'}\cdot\tilde\beta.
\tag{verify}

$$

任何一行不成立即 abort.

诚实必过: 把 (wv-row-eq) 按段拆开, $\hat w_{i',j} = \hat v_{i',j} \oplus \Delta_{i'}\cdot\hat\beta_j$, $w^\mathrm{ext}_{i'} = v^\mathrm{ext}_{i'} \oplus \Delta_{i'}\cdot\beta^\mathrm{ext}$; 代入 (verify) 左边, 单比特标量 $\Delta_{i'}$ 在域乘法里自由移动, 恰得右边.

掺假必抓 (概率意义): Receiver 若在不同的行使用不同的选项串, 通过的概率与 [B. 详细论证 Sender (verify)](./02-kos15.md#b-sender-verify) 原理类似. 检查的可靠性由 Schwartz-Zippel 引理与 $S = 128$ 比特的域尺寸兜底, 不再赘述.

### 2.2.(6) 两方派生密钥

忽略陪跑列, 对列号 (实例编号) $j \in [0, L)$:

Receiver 计算

$$

\rho^{\beta_j}_j := \mathtt{Hash}\left(\mathtt{sid},\, \mathtt{tag5},\, j,\, v_{*,j}\right).

$$

Sender 计算

$$

\begin{align*}
\rho^0_j &:= \mathtt{Hash}\left(\mathtt{sid},\, \mathtt{tag5},\, j,\,
    w_{*,j}
\right),\\
\rho^1_j &:= \mathtt{Hash}\left(\mathtt{sid},\, \mathtt{tag5},\, j,\,
    w_{*,j} \oplus \Delta
\right).
\end{align*}
\tag{keys}

$$

两式的衔接由 (wv-eq) 的逐列形式保证: $v_{*,j} = w_{*,j} \oplus \beta_j\cdot\Delta$, 所以 Receiver 的哈希入参恰是 Sender 两个原像中 $\beta_j$ 一侧的那个.

Hash 这一下不能省: 它把 "两个原像差一个公差" 升格为 "两把密钥各自独立" ([2.3.2. 与 MtA 与 Base OT 对比思路](./01-iknp03.md#id-2-3-2-mta-base-ot)), 并掺入域分离参数 $(\mathtt{sid}, \mathtt{tag5}, j)$. 若不 Hash, 泄露任何一对密钥就等于泄露 $\Delta$.

# 3. 总结

### 3.1. 核对安全承诺

**"Sender 不知道 $\beta$".** (umat) 的掩码 $\sum_x r_{i,x}$ 含打孔叶的扩张 $r_{i,\delta_i}$, Sender 不知道它, 掩码对他均匀 —— 一次一密. 归约链: 窥 $\hat\beta$ $\to$ 求 $r_{i,\delta_i}$ $\to$ 得打孔叶 $\mathcal{T}_{i,\delta_i}$, 破 [PPRF 与 GGM 树](./04-pprf.md) 的承诺 "打孔叶学不到", 或破 $\mathtt{PRG}$. 新增消息 $\tau, \tilde\beta$ 各被一段新鲜陪跑 ($v^\mathrm{ext}$/$\beta^\mathrm{ext}$) 一次一密掩护, 对应 [KOS15 恶意安全](./02-kos15.md) §2.3.2 机制一的修补; 挑战被 Fiat-Shamir 钉死, Sender 没有定向挑 $\chi$ 的机会, 对应机制二的修补.

**"Receiver 不知道 $\rho^{1-\beta_j}_j$".** 归约到 "算不出另一个原像", 归约到 "不知道公差 $\Delta$". $\Delta$ 由打孔下标拼成, 归约到 [PPRF 与 GGM 树](./04-pprf.md) 的承诺 "打孔位置学不到", 落脚在 Base OT 藏住选择位. 恶意 Receiver 想靠掺假探 $\Delta$, 由 (verify) 兜住: 掺假以压倒性概率败露, 即便侥幸也只换得少数比特, $\Delta$ 剩余熵仍然巨大, 论证与 [KOS15 恶意安全](./02-kos15.md) §2.3.1 同型.

**"一致性".** 诚实双方由 (wv-eq) 自动对齐. Receiver 掺假由 (verify) 抓; Sender 在本协议零下行消息, 没有作恶的载体 —— 他的 selective failure 藏在下游拿密钥加密的时刻, 见 [随机 VOLE](./06-rvole.md).

### 1.3.2. 盘点通信和计算成本

唯一一条消息 $(u, \tau, \tilde\beta)$ 之中, $u$ 的带宽受益于 PPRF, 其带宽与行数成正比, 因而与 $1/k$ 成正比.

而在计算量方面, SoftSpoken 比 KOS 多出来的是叶子扩张 (leaf), 可以量化为 PRG 调用次数: Receiver 全叶扩张, 共 $2^k \cdot (\kappa/k)$ 次; Sender 缺打孔叶, 共 $(2^k - 1) \cdot (\kappa/k)$ 次. 代入 $k=1$ 恰好退化为 KOS 的账: Receiver 每行扩两侧种子, Sender 每行扩单侧.

把通信和计算的倍率一起拉个表如下, 计算列取 Sender 口径 $(2^k-1)/k$ 的近似值 $2^k/k$, Receiver 口径约为其一半. 注意 $\kappa/k$ 这个算式决定了 $k$ 需整除 $\kappa$, 因而 $k$ 有意义的取值只有 2 的幂.

|       | 带宽      | 计算       |
| ----- | ------- | -------- |
| 标的    | $u$ 的行数 | PRG 调用次数 |
| $k=1$ | 基准      | 基准       |
| $k=2$ | 1/2     | 2        |
| $k=4$ | 1/4     | 4        |
| $k=8$ | 1/8     | 32       |

DKLs23 的实践表明, $k=4$ 是一个甜点参数, 带宽收益和计算代价达到完美平衡.
