# 前言

承接 [zk币进阶4](zk币进阶4.md). 进阶5 设立两个目标:

* 让一个 sk 派生出大量互不关联的地址.
* 顺便把 "读账本" 的权限做成一把可以单独交出去的钥匙.

进阶4 的不足之处: 一个 sk 只对应一个地址 pk, 于是收款人陷入两难: 复用地址会留下公开画像, 不复用地址需要记忆大量 sk.

想要: 地址随手发、无限发, 彼此不可关联; 但钱包只保管一个 sk, 扫链只用一把 ivk.

## 结构变化

### 地址多样化

回顾进阶3: 地址 $\mathtt{pk_B} = [\mathtt{ivk_B}]\,G$, 其中 $G$ 是全局固定基点. 如此, 一个 ivk 只能出一个地址.

这一版把基点也个性化 (diversify). 收款人 Bob 每次 (第 $j$ 次) 发地址时, 计算
$$
\begin{aligned}
d_j &:= \mathrm{Rand}(), \\
G_j &:= \mathrm{HashToCurve}(d_j), \\
\mathtt{pkd}_j &:= \mathtt{ivk_B}\cdot G_j .
\end{aligned}
\tag{addr}
$$
地址 / 公钥定义为元组 $(\mathtt{pkd_B}, d)$. 因此券演变为
$$
N_j = \big( v_j,d_j,\mathtt{pkd}_j,\rho_j,r_j \big). \tag{note}
$$
元组的第二个字段用 $d$ 而不用 $G$, 是为了在结构上强制使用 HashToCurve. 如果该字段用 $G$ 则死无对证, 除了制作 $G_d$ 的人, 没人知道它是否忠实地使用 HashToCurve.

### 加密方式跟着变

进阶3 的密钥交换演变为如下两式. 发送方 Alice 计算
$$
\begin{aligned}
\mathtt{epk}_j &= \mathtt{esk}_j\cdot G_j, \\
\mathtt{key}_j &= \mathrm{Hash}(\mathtt{esk}_j \cdot \mathtt{pkd}_j).
\end{aligned}
$$
接收方计算
$$
\mathtt{key}_j = \mathrm{Hash}(\mathtt{ivk_B}\cdot \mathtt{epk}_j).
$$
注意到接收方 Hash 参数满足下式
$$
\mathtt{ivk_B}\cdot \mathtt{epk}_j
= \mathtt{ivk_B}\cdot \mathtt{esk}_j\cdot G_j
= \mathtt{esk}_j \cdot \mathtt{pkd}_j.
$$
Bob 感受到的妙处: 他只需要用同一个 $\mathtt{ivk_B}$ 就能解密别人写给他的券, 无论写的是哪个衍生公钥 $(\mathtt{pkd}_j, d_j)$.

### 电路 (命题) 跟着变

花券时的 "身份" 子命题 ($N_j$ 与 $h_j$ 依赖同一个 $\mathtt{sk}$) 演变为: 存在 $\mathtt{sk_B}$ 使得
$$
\begin{aligned}

N_j.\mathtt{pkd} &= \mathrm{Hash}(\mathtt{sk_B}, \texttt{"ivk"})\cdot\mathrm{HashToCurve}(N_j.d) \\

\land\quad h_j &= \mathtt{Hash}\big(
N_j.\rho,\, \mathrm{Hash}(\mathtt{sk_B}, \,\texttt{"nk"}
)\big).

\end{aligned}
$$

### ivk 的业务权限

至此, $\mathtt{ivk_B}$ 恰好演变为 Bob 可以单独交出去的 "只读钥匙". Bob 的披露是分层的:

* 交出 $\mathtt{ivk_B}$: 对方能重建 Bob 的全部收款记录, 但花不了钱, 也看不出哪笔收款已被花掉.
* 再交出 $\mathtt{nk_B}$. 还能去链上查是否已花掉. 但仍然花不了钱. 🧠因为对方证明不了知道 $\mathtt{nk_B}$ 背后的 $\mathtt{sk_B}$.
* $\mathtt{sk_B}$ 永远不交: 花钱的权力留在自己手里.

# 例1. Bob 收款

例1. 商家 Bob 给每个顾客发不同地址

## 1.1 Bob 发地址

给 Alice: 摇 $d_1$, 算 $G_{d_1}$, $\mathtt{pkd}_1$. 发送地址 $(d_1, \mathtt{pkd}_1)$.

给 Carol: 同理发出 $(d_2, \mathtt{pkd}_2)$.

Alice 和 Carol 把地址摆在一起比, 也看不出收款方是同一个 Bob.

## 1.2 Alice, Carol 各自付款

流程与进阶 3 或 4 几乎完全相同. 只是印券时的地址字段按公式 (note) 填写, 加密备注 $\mathtt{ct}_j$ 的基点用 $G_j$.

注意 Alice / Carol 摇的 $\mathtt{epk}$ 是一次性的, 每印一张券都要现摇一个.

## 1.3 Bob 扫链

钱包对每个新输出照旧只做一件事: 算如下密钥, 试解密.
$$
\mathtt{key}_j = \mathrm{Hash}(\mathtt{ivk_B}\cdot \mathtt{epk}_j)
$$
Alice 和 Carol 的两笔付款发往不同地址, 却被同一把 $\mathtt{ivk_B}$ 一次扫描全部认领.

## 1.4 Bob 把 ivk 交给会计 / 审计.

会计跑与 §1.3 相同的扫描, 得到 Bob 的完整收款流水: 金额, 时间, 目标地址. 但会计没有 $\mathtt{sk_B}$ 花不了钱. 会计没有 $\mathtt{nk_B}$ 也看不出 Bob 花掉了哪些进账, 除非 Bob 主动披露.

## 拼起来就是 Zcash

五级走完. 回头看, 合约端的全局状态模型 —— 承诺树 + 核销表, 从基础篇的固定面额池到现在**一个字没改**; 改的全在券结构和电路命题上:

| 电路命题 | 来自哪一级 |
|---|---|
| 登记 (券在承诺树里) | 基础 |
| 核销正确 | 基础; 进阶2 改绑 `nk`; 进阶5 改绑多样化地址 |
| 身份 ($N$ 与 $h$ 依赖同一个 `sk`) | 进阶2 |
| 范围 | 进阶1 |
| 金额 (输出承诺正确) | 进阶1; 进阶3 配加密备注 |
| cv 一致 (守恒的电路内残留) | 进阶4 |

这六条正好对应 Zcash Orchard 每个 Action 电路要证的命题; 守恒本身在电路外由 binding signature 扛着.

一句话: 固定面额池 = 只证 "登记 + 核销"; 复杂 zk币 = 把金额 (进阶1、4)、所有权 (进阶2)、被动收款 (进阶3)、地址体系 (进阶5) 逐条加进券和电路 —— 状态模型不动, 命题变长.
