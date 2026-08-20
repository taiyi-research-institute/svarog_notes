[[01-iknp03]] 末节 "半诚实的边界" 第 (3) 条路线在此展开: SoftSpokenOT 要把二选一 OT 升级成 $2^k$ 选一, 升级的载体就是本篇的 PPRF (Puncturable PRF, 可打孔伪随机函数) —— 用 $k$ 个二选一 Base OT 合成一棵 $q = 2^k$ 叶的 GGM 树, Sender 得到全部叶子, Receiver 得到除打孔叶子之外的一切. Base OT 的实施见 [[03-endemic-ot]], 下游消费见 [[05-softspoken]]. 本篇只讨论二叉的情况.

# 1. 介绍 GGM 树

GGM 树是一棵完美二叉树, 深度为 $k$, 叶子数 $q=2^k$. 第 $i$ 层有 $2^i$ 个节点, 节点在层内的编号为 $y\in [0, 2^i)$. 节点内容是长度 $\lambda$ 的比特串, 记为 $\mathcal{T}^i_y \in \left\{0, 1\right\}^\lambda$.

$\lambda$ 是计算安全参数. 其数值沿用 [[01-iknp03]] 的约定 $\lambda = \kappa$, 但两个记号分工不同: $\kappa$ 是 OT 实例数/矩阵行数, $\lambda$ 只是比特串的长度.

记 $\mathtt{PRF}: \left\{0,1\right\}^* \rightarrow \left\{0,1\right\}^{2\lambda}$, 入参为域分离参数与父节点内容, 出参对半切开分给两个孩子. 节点 $\mathcal{T}^i_y$ 的左孩子记为 $\mathcal{T}^{i+1}_{2y}$, 右孩子记为 $\mathcal{T}^{i+1}_{2y+1}$, 父子节点的关系为
$$
\mathcal{T}^{i+1}_{2y} \mathbin{\|} \mathcal{T}^{i+1}_{2y+1} := \mathtt{PRF}(\mathtt{sid},\, \mathtt{tid},\, \mathtt{tag1},\, \mathcal{T}^i_y).
\tag{step}
$$
PPRF 树有一个用不上的根节点, 视其为第 0 层.

所谓 "打孔": Receiver 持有打孔下标 $y\in[0, 2^k)$, 目标是学到未打孔节点 $\left\{\mathcal{T}^k_z: z\neq y\right\}$, 但学不到打孔节点 $\mathcal{T}^k_y$.

# 2. PPRF 协议

## 2.1. 规格

输入: 双方先跑 $k$ 个 Base OT (详见 [[03-endemic-ot]]).

* Sender 得到两侧串 $\left\{\left(\rho_i^0, \rho_i^1\right)\right\}$, $i\in[0, k)$, 作为本协议的输入.
* Receiver 得到选择位 $\beta_i$ 与单侧串 $\rho_i^{\beta_i}$, 作为本协议的输出.

输出:

* Sender 得到整个叶子层, 记为 $G: z \mapsto \mathcal{T}^k_z$, 共 $q$ 个叶子.
* Receiver 得到打孔点 $y$ 与打孔树 $G^*$, 即除 $z = y$ 外的所有叶子.

安全承诺:

* Sender 学不到 $y$.
* Receiver 学不到打孔叶子 $\mathcal{T}^k_y$.
* 一致性: 协议正常结束时, 双方的非打孔叶子相同. 恶意 Sender 掺假而不败露的概率见 §2.3.1.

安全假设:

* Sender 恶意: 他可以篡改修正值, 由 2.2.(2)/2.2.(4) 的证明-验证来防御.
* Receiver 恶意也无妨: 本协议中 Receiver 零上行消息, 没有作恶的载体.
* Base OT 来历合规: 种子确实是 endemic OT 的输出, 其安全承诺 ($\beta_i$ 与 $\rho_i^{1-\beta_i}$ 对外均匀随机) 未被破坏.
* $\mathtt{PRF}$, $\mathtt{Hash}$ 视作随机预言机.

## 2.2. 实施

### 2.2.(1) Sender 建树, 出具逐层密文 (BuildPPRF)

先讲本节的密码学意义. 修正值 $t_i^b$ 的身份是密文: 以合成密钥 $\rho_i^b$ 为一次一密密钥, 加密 "第 $i+1$ 层 $b$ 侧孩子的异或和". 持有 $\rho_i^b$ 的一方恰能解出该层唯一缺失的兄弟节点, 拿不到 $\rho_i^b$ 的一方毫无所获.

Sender 按公式 (base) 构建第 $i=1$ 的两个节点. 随后按公式 (step) 递归地构建节点, 直到构建出第 $i+1=k$ 层 (即叶子层) 的所有节点.
$$
\mathcal{T}^1_0 := \rho_0^0, \quad \mathcal{T}^1_1 := \rho_0^1.
\tag{base}
$$
我们不妨假设这棵树有一个用不上的根节点, 视其为第 0 层.

接下来, 对第 $i, i\in[1, k)$ 层计算两个修正值
$$
t_i^b :=
\rho_i^b \oplus \bigoplus_{y \in [0, 2^i)} \mathcal{T}^{i+1}_{2y + b},
\quad
b \in \left\{0,1\right\}.
\tag{corr}
$$
Sender 发送所有 $(t_i^0, t_i^1)$, $i\in[1, k)$.

Sender 输出所有叶子节点, 记为 $G: z \mapsto \mathcal{T}^k_z$.

### 2.2.(2) Sender 承诺叶子 (ProvePPRF)

仅有 BuildPPRF 还不够. 恶意 Sender 可以把某层修正值 $t_i^b$ 替换成乱数, 让 Receiver 顺着错误的 $\mathcal{T}^{i+1}_{2y_i + \beta_i}$ 一路向下, 最终得到一棵跟 Sender 不一致的子树, 而 Receiver 自己察觉不到. 为此 SoftSpokenOT 原文 (Roy, CRYPTO'22, eprint 2022/192, Fig. 14; BuildPPRF/EvalPPRF 是同文 Fig. 13, DKLS23 引用其做 OT 扩展) 在 BuildPPRF 末尾追加一段 "叶子层一致性证明".

Sender 对每个叶子算一个长度 $2\lambda$ 的标签. 注意 $\mathtt{tag2}$ 把它与 (step) 的节点派生隔离开:
$$
\tilde s_z := \mathtt{PRF}(\mathtt{sid},\, \mathtt{tid},\, \mathtt{tag2},
\mathcal{T}^k_z), ~ z \in [0, q).
\tag{sz}
$$

然后计算如下两个 $2\lambda$-比特串, 发给 Receiver. 其意义依次为: 对所有叶子节点的异或承诺, 对所有叶子节点的哈希承诺.
$$
\tilde t := \bigoplus_{z \in [0, q)} \tilde s_z.
\tag{com-x}
$$
$$
\tilde s := \mathtt{Hash}\bigl(\mathtt{sid},\, \mathtt{tid},\, \mathtt{tag3},s_0 \,\|\, \tilde s_1 \,\|\, \cdots \,\|\, \tilde s_{q-1}\bigr)
\tag{com-h}
$$
### 2.2.(3) Receiver 建树 (EvalPPRF)

Receiver 的选择向量 $\beta = (\beta_0, \beta_1, \dots, \beta_{k-1}) \in \left\{0,1\right\}^k$ 对应一个打孔下标

$$
\hat y = \sum_{i=0}^{k-1} (1-\beta_i) \cdot 2^{k-1-i}. \tag{hole}
$$

实际上, 打孔下标是由如下递归式直接推导出来的. 下式同时还定义了 "活动路径" $\left\{y_1, \dots, y_k\right\}$.
$$
\begin{align*}
y_1     &:= 1-\beta_0, \,\dots \\
y_{i+1} &:= 2y_i+(1-\beta_i), \,\dots \\
y_k &:= \hat y.
\end{align*}
\tag{path}
$$

#### 构建第一层

Receiver 通过 Base OT 实例 0 已拿到 $\rho_0^{\beta_0}$, 按定义这就是 $\mathcal{T}^1_{\beta_0}$; 拿不到兄弟节点 $\mathcal{T}^1_{1-\beta_0}$.

#### 建好第 $i$ 层, 构建第 $i+1$ 层

对第 $i$ 层除 $y_i$ 以外的节点编号 $z \in [0, 2^i) \setminus \{y_i\}$, 按 (step) 派生两个孩子, 与 Sender 建树逻辑相同.

而对编号为 $(i, y_i)$ 的节点, 只能恢复出编号为 $(i+1, 2y_i+\beta_i)$ 的子节点. 恢复方法如下式:
$$
\mathcal{T}^{i+1}_{2 y_i + \beta_i} = 
t_i^{\beta_i} \oplus \rho_i^{\beta_i} 
\oplus \bigoplus_{z \neq y_i} \mathcal{T}^{i+1}_{2z + \beta_i}.
$$
这样恢复是因为 Sender 视角下的 $t_i^{\beta_i}$ 满足下式
$$
t_i^{\beta_i} = \rho_i^{\beta_i} \oplus \bigoplus_{z \in [0, 2^i)} \mathcal{T}^{i+1}_{2z + \beta_i}.
$$
以上递归在 $i=k-1$ 执行完毕时结束. 此时 Receiver 获得树 $G^*$, 是 Sender 视角下的树在整条活动路径打孔的版本.

### 2.2.(4) Receiver 校验 (VerifyPPRF)

紧接 EvalPPRF, Receiver 要校验 Sender 的 $(\tilde t, \tilde s)$ 一致. Receiver 只算得出 $z\ne \hat y$ 的标签, 详见公式 (sz). 缺的那一项 $\tilde s_{\hat y}$ 可以从 $\tilde t$ 解出:

$$
\tilde s_y := \tilde t \oplus \bigoplus_{z \ne y} \tilde s_z. \tag{sy}
$$

补齐后, Receiver 按公式 (com-h) 重算, 记 Receiver 算出的为 $\tilde s^*$. Receiver 验 $\tilde s^* \stackrel{?}{=} \tilde s$, 等式不成立则 abort. 协议至此结束.

## 2.3. 小结

### 2.3.1. 核对安全承诺

"Sender 得不到 $y$": $y$ 只由 Base OT 选择位 $\beta$ 决定. 归约到 "Base OT 藏住 $\beta_i$". Sender 猜中 $y$ 的概率为 $2^{-k}$. 在 [[05-softspoken]] 中, 虽然 $k=4$, 但 Sender 需猜中所有 $\kappa/k$ 棵树才能骗过 Receiver.
 
"Receiver 得不到 $\mathcal{T}^k_y$": 逐层归纳. 第 1 层缺 $\mathcal{T}^1_{1-\beta_0}$, 归约到 "Base OT 藏住 $\rho_0^{1-\beta_0}$". 往后每层, 修正值 $t_i^{1-\beta_i}$ 虽然是线上消息的一个异或项, 但异或项 $\rho_i^{1-\beta_i}$ 在 Recevier 视角下是随机的. 进而, 安全性归约到 "Base OT 藏住 $\rho_i^{1-\beta_i}$", 以及 $\mathtt{PRF}$ 的安全性.

### 2.3.2. 清点通信成本

* Sender 给 Receiver 的修正值: $2(k-1)$ 个 $\lambda$ 比特串.
* ProvePPRF 输出: $\tilde t, \tilde s$ 两个 $2\lambda$ 比特串, 共 $4\lambda$.

总扩展通信约 $2(k-1)\lambda + 4\lambda = 2(k+1)\lambda$ 比特, 得到 $q = 2^k$ 大小的 PPRF.
