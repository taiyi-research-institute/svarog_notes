# 0. 铺垫

回顾 [[05-softspoken]], 其 Sender 得到 $L$ 对 OT 密钥, Receiver 得到相应的 $L$ 个单侧密钥.  对第 $j$ 实例, $j \in [0, L)$,

* Sender 持有成对密钥 $\rho^0_j, \rho^1_j$, 不知 Receiver 选哪一边.
* Receiver 持有选择位 $\beta_j\in\left\{0,1\right\}$, 所选密钥 $\rho^{\beta_j}_j$, 不知另一个密钥 $\rho_j^{1-\beta_j}$.

记号约定: $\vec\beta \in \left\{0,1\right\}^L$ 指选项串本身 (即 [[05-softspoken]] 的 $\beta$); 不带箭头的 $\beta := \sum_{j\in[0,L)}\beta_j g_j \pmod n$ 专指它的 gadget 加权聚合 ([[misc-gadget]]).

拿到这些密钥后, 兑现随机 MtA 关系 $y + z := w\beta \pmod n$. 其中 Sender 输入 $w$, 输出 $y$; Receiver 输入 $\beta$, 输出 $z$.

注意: 本协议不兑现 ECDSA MtA 关系 $y + z := wx \pmod n$. DKLs23 把消除 $\beta$ 的工作交给 ECDSA 编排层, 这是一个安全手段.

安全在哪? 若直接让 Receiver 输入选定值 $x$, 选择串就是 $x$ 的编码, 恶意 Sender 对个别实例 $j$ 掺假即可发动 selective failure —— 协议 abort 与否泄露该位 $\beta_j$, 也就是泄露 $x$ 的比特. 换成随机 $\vec\beta$ 后有两重保险: 其一, $\vec\beta$ 一次一换, 泄露不跨会话累积; 其二, gadget 编码留有 $2\lambda_s$ 比特富余熵 ($L = \kappa + 2\lambda_s = 512$), 即便个别 $\beta_j$ 败露, 聚合值 $\beta$ 对 Sender 仍统计均匀 (DKLs23 援引的依据是 Impagliazzo-Naor 子集和引理).

[[07-orchestration]] 描述了如何将 $w\beta$ 替换成 $wx$.

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

Sender 和 Receiver 分别聚合出自己的加法秘密份额. 聚合采用 gadget 方式, 详见 [[misc-gadget]].
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

RVOLE 完全版有三个索引维度: OT 实例 $j$, 检查编号 $k$, MtA 关系编号 $i$. 维度太多会干扰认知. 本章描述单个负载且无检查的 RVOLE 协议.

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

### 1.2.(2) Receiver 收尾

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

恶意 Sender 可能对不同的 OT 实例 $j$ 使用不同的 $w' \neq w$, 破坏聚合关系 $y + z = w\cdot\beta$ 的正确性. 为此, 我们约定每个 OT 实例携带 $N_2$ 个负载用于校验. DKLs23 论文取 $\lceil \kappa/\lambda_c \rceil$.

决定引入校验维度以后, 将使 RVOLE 内部运算变得向量化. 既然如此, 不妨继续引入 $N_1$ 个 MtA 关系. 对于 ECDSA 签名, 有 $N_1=2$.

综上, 完全版的协议兑现如下 $N_1+N_2$ 个 MtA 关系:
$$
y_{k}+z_{k} := w_{k}\cdot \beta \pmod n,
~~ k \in [0,\, N_1+N_2).
$$
其中, 前 $N_1$ 个 $w_k$ 为真实输入, 后 $N_2$ 个为 $\mathbb{Z}_n$ 随机标量.

## 2.1. 规格

输入: Sender 持有 $N_1+N_2$ 个秘密因子 $w_k$. Receiver 持有一个秘密因子 $\beta=\sum_{j\in[0,L)} \beta_j \cdot g_j$.

输出: Sender 获得 $N_1+N_2$ 个秘密加项 $y_k$. Receiver 获得 $N_1+N_2$ 个秘密加项 $z_k$.

安全承诺:

### (Round 1) Sender -> Receiver

对每个 OT 实例 $j$ 和负载 $k$, Sender 对 OT 密钥进行衍生, 得到:
$$
\alpha^b_{j,k}:=\mathrm{Hash}\left(
\mathtt{sid},j,k, \rho^b_j
\right);
\quad
b\in\left\{0,1\right\}.
$$
对每个 OT 实例 $j$ 和负载 $k$, Sender 计算修正项:
$$
\tilde{a}_{j,k} := \alpha^0_{j,k}-\alpha^1_{j,k}+w_{k}.
$$
对每个**功能**负载 $k$, Sender 计算加法份额:
$$
y_{k}:=-\sum_j g_j\cdot \alpha^0_{j,k} ~.
$$
对每个**校验**负载 $k$, Sender 计算挑战向量 $\theta_k \in \mathbb{Z}_n^{N_1}$:
$$
\theta_k:=\mathrm{Hash}(\mathtt{sid},\, k,\, \tilde{a}).
\tag{challenge}
$$
⚠️ 哈希入参是**整张** $\tilde{a}$ 矩阵, 功能列与校验列一并绑定. 若只喂第 $k$ 列, Sender 可在 $\theta$ 定死后自由解出功能列的掺假偏移, 使校验恒过. 对应原论文的 $\theta := \mathrm{RO}(\mathtt{sid}, \tilde{a})$.
对每个**校验**负载 $k$, Sender 计算 eta-响应:
$$
\eta_k := w_{k}+\sum_{i\in[0,N_1)}\theta_{k,i}\cdot w_{i} ~. \tag{resp-eta}
$$
对每个 OT 实例 $j$ 和**校验**负载 $k$, Sender 计算 mu-响应:
$$
\begin{align*}
\mu_{j,k} &:= \alpha^0_{j,k}
+\sum_{i\in[0,N_1)}\theta_{k,i}\cdot \alpha^0_{j,i}, \\

\mu &:= \mathrm{Hash}\left(\mathtt{sid},\, \left\{\mu_{j,k}\right\}_{j,k}\right).
\end{align*}
\tag{resp-mu}
$$
Sender 本地保存 $y_{k}$, 发送 $\tilde{a}_{j,k}$, $\eta_k$ 与短摘要 $\mu$. 注意不发 $\mu_{j,k}$ 矩阵本身: Receiver 能自行重算它, 摘要足以比对, 省带宽.

### (Round 2) Receiver 结束

Receiver 的随机选择串 $\vec{\beta}\in\left\{0,1\right\}^L$ 无需现摇: 它在 [[05-softspoken]] 扩展 OT 开跑之前就已定好 —— 否则 Receiver 拿不到 $\rho^{\beta_j}_j$. 此处直接取用.

对每个 OT 实例 $j$ 和负载 $k$, Receiver 对 OT 密钥进行衍生, 得到
$$
\alpha^{\beta_j}_{j,k}:=\mathrm{Hash}\left(
\mathtt{sid},j,k, \rho^{\beta_j}_j
\right).
$$
对每个 OT 实例 $j$ 和负载 $k$, Receiver 计算
$$
\begin{align*}
t_{j,k} &:= \alpha^{\beta_j}_{j,k}+\beta_j\cdot \tilde{a}_{j,k}, \\
&= \alpha^0_{j,k}+\beta_j\cdot w_{k}.
\end{align*}
$$
基于 Sender 发来的 $\tilde{a}$, Receiver 也采用公式 (challenge) 计算挑战.
$$
\theta_k:=\mathrm{Hash}(\mathtt{sid},\, k,\, \tilde{a}).
$$
对每个 OT 实例 $j$ 和校验负载 $k$, Receiver 在本地计算 $\hat\mu_{j,k}$ 和 $\hat{\mu}$.
$$
\begin{align*}
\hat\mu_{j,k} &:= t_{j,k} 
+ \left\{\sum_{i\in[0,N_1)} \theta_{k,i}\cdot t_{j,i} \right\}
- \beta_j\cdot\eta_k, \\

\hat\mu &:= \mathrm{Hash}\left(\mathtt{sid},\, \left\{\hat\mu_{j,k}\right\}_{j,k}\right).
\end{align*}
$$
然后检验 $\hat\mu\stackrel{?}{=}\mu$.

如果检验通过, 那么 Receiver 对每个功能负载 $k$ 计算本地份额
$$
z_{k} := \sum_{j}g_j\cdot t_{j,k} ~.
$$
Receiver 本地保存 $z_{k}$.

-----
