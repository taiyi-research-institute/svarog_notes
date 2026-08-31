---
title: "Endemic OT"
---

参考: Masny-Rindal, "Endemic Oblivious Transfer", Fig. 8, https://eprint.iacr.org/2019/706.pdf.

Endemic OT 本质上是安全定义更弱的 Base OT. 虽然安全定义更弱, 但证明更完备. 而 MtA 与 Base OT 中的 OT 难以构造证明.

# 1. Endemic OT 两轮交互版

## 1.1. 规格

每场协议包含$\kappa$个二选一 OT 实例. 其中$\kappa$为曲线标量比特数, 对 secp256k1 而言取$\kappa = 256$. 对每个实例$i\in[\kappa]$:

输入: Receiver 的选择$s_i$.

输出: Sender 输出成对密钥$\rho_i^0, \rho_i^1$, Receiver 输出单个密钥$\rho_i^{s_i}$.

安全承诺:$s_i$与$\rho^{1-s_i}$对拥有者以外的人均匀随机.

这个安全承诺弱吗? 恶意 Sender 可以操纵$\rho^0, \rho^1$, 恶意 Receiver 可操纵$\rho^{s_i}$, 详见 §1.3. 即便如此, 对于后续只需要 OT 种子的协议, 例如 OT extension, PPRF 来说已经足够.

"Endemic" 的含义: Sender 输出的两个密钥都是协议执行过程中派生的随机值, 而不是 Sender 自选的任意明文.

## 1.2. 实施

### 1.2.1. Receiver 对选项发出承诺

对每个 OT 实例编号$i$:

Receiver 采样盲化项$u_i\in \mathbb{Z}_q$, 这里$q$为曲线点群的阶; 另采样新鲜随机串$w_i$. 然后对选项$s_i$进行如下承诺:

$$
\begin{align*}
R_i^{1-s_i} &:=
\mathtt{HashToGroup}(\mathtt{sid}, \mathtt{tag1}, i, w_i), \\
R_i^{s_i} &:=
u_i G \\
&- \mathtt{HashToGroup}(
\mathtt{sid}, \mathtt{tag2}, s_i, i,
R_i^{1-s_i}
). \tag{R}
\end{align*}
$$

三点说明. 其一,$\mathtt{HashToGroup}$输出离散对数未知的随机曲线点. 其二,$w_i$必须新鲜且保密: 若$R_i^{1-s_i}$只由公开值算出, Sender 重算一遍就能认出它, 选项当场泄露. 其三, 原文 Fig. 8 此处只要求$R_i^{1-s_i}$是均匀随机点, 对 Receiver 是否知道其离散对数不做说明. 这里用$\mathtt{HashToGroup}$是加固.

最后, Receiver 留存$s_i, u_i$, 按上标顺序发送$(R_i^0, R_i^1)$.

### 1.2.2. Sender 计算全密钥, 发送另一半密钥

对每个 OT 实例编号$i$:

Sender 无法区分收到的$R_i^0, R_i^1$中哪个承载着选项, 这正是协议追求的效果. 计算如下半密钥:

$$
\begin{align*}
U_i^0 &:= R_i^0 + \mathtt{HashToGroup}(
\mathtt{sid}, \mathtt{tag2}, 0, i,
R_i^1
),\\
U_i^1 &:= R_i^1 + \mathtt{HashToGroup}(
\mathtt{sid}, \mathtt{tag2}, 1, i,
R_i^0
).
\end{align*}
$$

两点说明. 其一, 这里复用 Receiver 侧的$\mathtt{tag2}$, 是正确性的前提. 其二, 必须用点哈希, 不能偷懒写成$\mathtt{Hash}(\cdots)\cdot G$, 否则 Receiver 能本地计算两个$U_i$(读者自行推导), 进而解出两把全密钥.

Sender 采样$v_i^0, v_i^1 \in \mathbb{Z}_q$, 令$V_i^0:=v_i^0 G$,$V_i^1 := v_i^1 G$. 生成全密钥:

$$
\begin{align*}
\rho_i^0 &:= \mathtt{Hash}(\mathtt{sid}, \mathtt{tag3}, 0, i,\,
v_i^0\cdot U_i^0), \\
\rho_i^1 &:= \mathtt{Hash}(\mathtt{sid}, \mathtt{tag3}, 1, i,\,
v_i^1\cdot U_i^1). \tag{keys}
\end{align*}
$$

Sender 输出$\rho_i^0, \rho_i^1$, 发送$V_i^0, V_i^1$.

### 1.2.3. Receiver 输出所选的全密钥

对每个 OT 实例编号$i$, Receiver 计算

$$
\rho_i^{s_i}:=\mathtt{Hash}(
\mathtt{sid}, \mathtt{tag3}, s_i, i,\,
u_i\cdot V_i^{s_i}
).
$$

正确性:$u_i\cdot V_i^{s_i} = v_i^{s_i}\cdot (u_i G) = v_i^{s_i}\cdot U_i^{s_i}$, 恰为 Sender 在$(\text{keys})$中喂给哈希的点.

## 1.3. 回顾安全承诺

§1.1 说恶意方可以操纵自家密钥, 这里补上操纵具体怎么发生. 机制是研磨 (grinding), 倚仗的是"看到对方消息之后才定自己的随机数".

恶意 Sender 操纵$\rho^0, \rho^1$: 两轮版里 Sender 天然是后手. 收到$(R_i^0, R_i^1)$后,$U_i^0, U_i^1$已完全确定, 于是$\rho_i^j = \mathtt{Hash}(\cdots, v_i^j \cdot U_i^j)$只是$v_i^j$的函数. 他可以反复重采$v_i^j$, 每次得到一个候选密钥, 直到密钥满足心仪的谓词 (比如前$k$比特全零, 代价约$2^k$次哈希). 他不能把密钥精确定成任意给定值 (那要求逆随机预言机), 但 "能任意偏置分布" 已足以摧毁 "密钥均匀随机" 这个承诺.

恶意 Receiver 操纵$\rho^{s_i}$: 两轮版里 Receiver 是先手, 发出$R$时$u_i$已被式$(\text{R})$锁死, 而密钥还依赖他没见过的$v_i^{s_i}$, 所以两轮版里 Receiver 其实没有研磨空间. 操纵空间出现在第 2 章的一轮同发版: 双方同轮出牌时, rushing 对手可以先扣住自己的消息, 等收到$V_i^0, V_i^1$再研磨$u_i$—— 地位与上面的 Sender 完全对称.

为什么安全定义干脆写成 "可任选": 定义要同时罩住两轮版和一轮版, 而模拟器在证明里的动作是, 盯着对手的随机预言机查询, 把对手自己算出来的那把密钥原样提交给理想功能 —— 对手"派生"出什么, 就算它"选择"了什么. 理想功能索性放权到上限 "corrupt 方任选自家密钥", 一切研磨都被覆盖. 反过来, 对手接触不到的$s_i$与$\rho^{1-s_i}$不经它的手, 均匀性保得住.

顺带一提, 有一种操纵做不到: 让不同实例或不同会话的密钥相互关联.$(\text{keys})$的哈希输入里钉死了$(\mathtt{sid}, s_i, i)$, 输入必不相同, 随机预言机的输出就互相独立.

# 2. Endemic OT 一轮交互版

## 2.1. 观察: Sender 的消息不依赖 Receiver 的消息

回看 §1.2: Sender 发出的$(V_i^0, V_i^1)$只由他自己采样的$(v_i^0, v_i^1)$决定; 收到的$(R_i^0, R_i^1)$只用于本地计算$U_i$与密钥, 不影响他要发的任何比特. 既然如此, 两轮可以压成一轮: 双方在同一轮给对方投递消息, 各自收齐后在本地收尾.

## 2.2. 实施

消息内容与第 1 章完全相同, 只是投递方式变了. 同一轮内:

* Receiver 按 §1.2.1 生成并发送$(R_i^0, R_i^1)$;
* Sender 按 §1.2.2 采样并发送$(V_i^0, V_i^1)$.

收齐对方消息后, 各自本地收尾. Sender 算$U_i$, 然后算$\rho_i^0$,$\rho_i^1$. Receiver 算$\rho_i^{s_i}$. 公式不改.

## 2.3. 代价: rushing 对手

一轮同发挡不住 rushing: 对手可以扣住自家消息, 等看到对方的消息再定自己的随机数 —— 现实网络里, 消息谁先谁后本来就没有保证. 后果正是 §1.3 预告的那条: Receiver 拿到与 Sender 对称的研磨能力, 边看$V_i^{s_i}$边重采$u_i$, 偏置自家的$\rho_i^{s_i}$.

但 §1.1 的安全承诺一个字不用改, 它只保$s_i$与$\rho^{1-s_i}$的隐私:

*$s_i$的隐私:$R_i^0, R_i^1$都是均匀随机点, 与 Sender 先看后看无关.
*$\rho^{1-s_i}$的隐私: Receiver 想要它, 就得算出$v_i^{1-s_i} \cdot U_i^{1-s_i}$; §1.2.2 的点哈希论证只依赖 "$U_i^{1-s_i}$的离散对数无人知晓", 与消息顺序同样无关.

换个角度看, endemic 定义预先让渡了 "自家密钥不可操纵", 换来的正是对消息顺序的免疫. 更强的承诺 (例如密钥均匀的 Uniform OT) 在一轮同发下不可能达成, 因为 rushing 研磨总是存在; endemic 恰是一轮协议能拿到的上限. 这就是原文标榜 "single round" 的分量.

顺带一提带宽: 原文作者的 libOTe 实现里, Sender 全场只采样一个指数$z$、只广播单点$zG$, 两把密钥分别从$z\cdot U_i^0,\ z\cdot U_i^1$导出. 本文按实例、按半边独立采样$v_i^0, v_i^1$, 更贵, 但安全性不降.

