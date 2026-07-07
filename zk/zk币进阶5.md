承接 [zk币进阶4](zk币进阶4.md). 进阶5 只做一件事: 让一个 `sk` 派生出大量互不关联的地址, 顺带把 "看" 的权限做成一把可以单独交出去的钥匙. 合约状态模型 (承诺树 cm + 核销表 nf) 仍然一点没变.

## 进阶4 留下的弱点

一个 `sk` 只对应一个地址 `pk`, 于是收款人陷入两难:

* 复用地址. 商家把同一个 `pk` 挂在网站上, 每个付款人造钞票都要用它. 任何两个付款人一比对, 就知道付的是同一个人; 谁的钞票明文泄露, 谁的那份收款就被串进这个画像.
* 不复用地址. 给每个收款对象单独生成一个 `sk`, 则备份、扫链、花钱的密钥管理成本全部乘上地址数 —— 尤其扫链, 每把 `ivk` 都要把全链输出试解密一遍.

想要的形态: 地址随手发、无限发, 彼此不可关联; 但钱包只保管一个 `sk`, 扫链只用一把 `ivk`.

## 结构变化

### 地址多样化

回顾进阶3: 地址 $\mathtt{pk} = [\mathtt{ivk}]\,G$, 其中 $G$ 是全局固定基点. 全局固定, 所以一个 `ivk` 只能出一个地址.

多样化的思路: 把基点也个性化. 收款人每次发地址时:

* 摇一个 diversifier $\mathtt{d}$, 算个性化基点 $g_d = \mathrm{HashToCurve}(\mathtt{d})$.
* 地址 = 二元组 $(\mathtt{d},\ \mathtt{pkd})$, 其中 $\mathtt{pkd} = [\mathtt{ivk}]\,g_d$.

同一把 `ivk` 配不同的 $\mathtt{d}$, 得到不同的地址. 在 DDH 假设下, 外人拿着两个地址 $(\mathtt{d}_1, \mathtt{pkd}_1), (\mathtt{d}_2, \mathtt{pkd}_2)$, 无法判断它们是否出自同一把 `ivk`.

钞票里的地址字段跟着变: 钞票 $= (v,\ \mathtt{d},\ \mathtt{pkd},\ \rho,\ r)$,

$$
C = \mathrm{Hash}(v, \mathtt{d}, \mathtt{pkd}, \rho, r).
$$

### 加密备注跟着变

进阶3 的 key agreement 里, 基点 $G$ 全部换成该地址的 $g_d$. 发送方:

$$
\begin{aligned}
\mathtt{epk} &= [\mathtt{esk}]\,g_d \\
\mathtt{key} &= \mathrm{KDF}\big([\mathtt{esk}]\,\mathtt{pkd}\big).
\end{aligned}
$$

收款人侧的妙处: 重建对称钥**根本不需要知道对方用的是哪个地址**,

$$
[\mathtt{ivk}]\,\mathtt{epk} = [\mathtt{ivk}][\mathtt{esk}]\,g_d = [\mathtt{esk}]\,\mathtt{pkd},
$$

对哪个 $\mathtt{d}$ 都成立. 所以地址无限多, 扫链仍然是一把 `ivk` 对每个输出算一次 $\mathrm{KDF}([\mathtt{ivk}]\,\mathtt{epk})$, 成本不变. 解开之后再用明文里的 $\mathtt{d}$ 重算 $g_d$ 和 $\mathtt{pkd} = [\mathtt{ivk}]\,g_d$, 与承诺核对.

### 电路 (命题) 变化

花费时 "地址与 `nk` 同源" 那条命题跟着换: 存在 $\mathtt{sk}$ 使得

$$
\begin{aligned}
\mathtt{pkd} &= \big[\mathrm{KDF}(\mathtt{sk}, \texttt{"ivk"})\big]\,\mathrm{HashToCurve}(\mathtt{d}) \\
\land\quad h &= \mathrm{PRF}\big(\rho;\; \mathrm{KDF}(\mathtt{sk}, \texttt{"nk"})\big).
\end{aligned}
$$

⚠️ $\mathtt{pkd} = [\mathtt{ivk}]\,g_d$ 与 $g_d = \mathrm{HashToCurve}(\mathtt{d})$ 两条绑定在电路里一条都不能断. 断了意味着攻击者能给同一张钞票配出多把 "合法" 密钥、派生多个核销号 —— 同一张钱花多次. Zcash Orchard 出过的一个真实漏洞正是打断了 $\mathtt{pkd} = [\mathtt{ivk}]\,g_d$ 这条.

### viewing key 的权限边界

到这一级, `ivk` 恰好长成了一把可以单独交出去的 "只读钥匙". 披露是分层的:

* 交出 `ivk`: 对方能重建你的**全部收款记录** (覆盖所有多样化地址), 但花不了钱, 也看不出哪笔收款已被花掉 (算核销号要 `nk`).
* 再交出 `nk`: 对方连 "花没花" 也能对出来 (拿核销号去链上核销表里查). 两把合起来即所谓 full viewing key.
* `sk` 永远不交: 花钱的权力留在自己手里.

## 例1. 商家 Bob 给每个顾客发不同地址

(1) Bob 发地址.

给 Alice: 摇 $\mathtt{d}_1$, 算 $g_{d_1} = \mathrm{HashToCurve}(\mathtt{d}_1)$, $\mathtt{pkd}_1 = [\mathtt{ivk}_B]\,g_{d_1}$, 发出地址 $(\mathtt{d}_1, \mathtt{pkd}_1)$.

给 Carol: 摇 $\mathtt{d}_2$, 同法发出 $(\mathtt{d}_2, \mathtt{pkd}_2)$.

Alice 和 Carol 把地址摆在一起比, 也看不出收款方是同一个 Bob.

(2) Alice、Carol 各自付款.

流程与进阶3、4 完全相同, 只是造钞票时地址字段填 $(\mathtt{d}, \mathtt{pkd})$, 加密备注的基点用 $g_d$.

注意 $\mathtt{epk}$ 是一次性的, **每张输出钞票现摇一个**: Alice 这笔摇的是 $[\mathtt{esk}]\,g_{d_1}$, Carol 那笔另摇一个 $[\mathtt{esk}']\,g_{d_2}$; 即使日后 Alice 再付一笔到同一地址, 也是全新的 $\mathtt{epk}$. 长期的 `ivk` (一把管所有) 对一次性的 $\mathtt{epk}$ (一张钞票一个), 正是这套 key agreement 的形状.

(3) Bob 扫链.

钱包对每个新输出照旧只做一件事: 算 $\mathrm{KDF}([\mathtt{ivk}_B]\,\mathtt{epk})$ 试解密. Alice 和 Carol 的两笔付款发往不同地址, 却被同一把 `ivk` 一次扫描全部认领.

(4) Bob 把 `ivk` 交给会计.

会计跑与 (3) 相同的扫描, 得到 Bob 的完整收款流水 (金额、时间、来款所进的地址). 但会计没有 `sk` 花不了钱, 没有 `nk` 也看不出 Bob 花掉了哪些. Bob 若愿意连支出侧也披露, 再交 `nk`.

## 拼起来就是 Zcash

五级走完. 回头看, 合约端的全局状态模型 —— 承诺树 + 核销表, 从基础篇的固定面额池到现在**一个字没改**; 改的全在钞票结构和电路命题上:

| 电路命题 | 来自哪一级 |
|---|---|
| 成员 (钞票在承诺树里) | 基础 |
| 核销正确 | 基础; 进阶2 改绑 `nk`; 进阶5 改绑多样化地址 |
| 花费授权 | 进阶2 |
| 范围 | 进阶1 |
| 发行合法 | 进阶1; 进阶3 配加密备注 |
| cv 一致 (守恒的电路内残留) | 进阶4 |

这六条正好对应 Zcash Orchard 每个 Action 电路要证的命题; 守恒本身在电路外由 binding signature 扛着.

一句话: 固定面额池 = 只证 "成员 + 核销"; 复杂 zk币 = 把金额 (进阶1、4)、所有权 (进阶2)、被动收款 (进阶3)、地址体系 (进阶5) 逐条加进钞票和电路 —— 状态模型不动, 命题变长.
