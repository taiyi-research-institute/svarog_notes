承接 [zk币进阶2](zk币进阶2.md) 的地址化池子. 进阶3 只做一件事: 把 "链下交付 note 明文" 换成 "链上加密备注 + 收款人试解密". 合约状态模型 (承诺树 cm + 核销表 nf) 仍然一点没变.

## 进阶2 留下的弱点

进阶2 的第 (4) 步: Alice 造好 note 后, 要靠一条链下渠道把明文 $(10,\mathtt{pk}_B,\rho_1,r_1)$ 交给 Bob. 这有两个问题:

* 收款依赖链下渠道. 消息一丢, 树里明明有这片叶子, Bob 却永远不知道打开方式, 钱等于烧掉了.
* Bob 无法自主发现到账. 不守着渠道就不知道有钱进来, 谈不上 "钱包余额自动更新".

## 结构变化

### 密钥层级加一层

```
sk -> nk, ivk -> pk
```

* 核销密钥 `nk = KDF(sk, "nk")`, 照旧.
* 收款视图密钥 `ivk = KDF(sk, "ivk")`.
* 公开收款地址 `pk = [ivk] G`.

地址从进阶2 的哈希值变成群元素, 因为现在地址要能当 DH 公钥用, 参与 key agreement.

### 交易格式变化

note 本身不变, 仍是 $(v,\mathtt{pk},\rho,r)$, 承诺 $C$ 照旧. 变的是每片 output note 上链时附带两样东西:

* 一次性公钥 $\mathtt{epk}$.
* 加密备注 $\mathtt{ct}$.

Alice 造 output 时, 摇一次性私钥 $\mathtt{esk}$, 算

$$
\begin{aligned}
\mathtt{epk} &= [\mathtt{esk}]\,G \\
\mathtt{key} &= \mathrm{KDF}\big([\mathtt{esk}]\,\mathtt{pk}_B\big) \\
\mathtt{ct} &= \mathrm{Enc}\big(v,\rho,r;\;\mathtt{key}\big).
\end{aligned}
$$

Bob 侧用 `ivk` 能重建同一把对称钥:

$$
[\mathtt{ivk}_B]\,\mathtt{epk} = [\mathtt{ivk}_B][\mathtt{esk}]\,G = [\mathtt{esk}]\,\mathtt{pk}_B.
$$

### 电路 (命题) 变化: 没有

$\mathtt{ct}$ 和 $\mathtt{epk}$ 不进电路. 合约不解密、不校验密文, 只当作事件数据发布. 密文错了 (或 Alice 故意加密垃圾), 效果等同于进阶2 里链下发错明文: Bob 收不到, 链上其他人不受影响.

## 例1. Alice 池内给 Bob 转 10U (被动收款版)

Bob 只公布过地址 $\mathtt{pk}_B$, 与 Alice 没有任何链下渠道.

(1) Alice 造两片 output note 和两份加密备注.

先看给 Bob 的那片. Alice 在本地:

* 摇 $\rho_1, r_1$, 组成 note 明文 $(10,\mathtt{pk}_B,\rho_1,r_1)$. 这份明文就是进阶2 里要靠链下渠道交给 Bob 的东西, 本文的全部工作就是把它改走链上.
* 算承诺 $C_1 = \mathrm{Hash}(10,\mathtt{pk}_B,\rho_1,r_1)$.
* 摇一次性私钥 $\mathtt{esk}_1$, 算 $\mathtt{epk}_1 = [\mathtt{esk}_1]\,G$ 和 $\mathtt{key}_1 = \mathrm{KDF}([\mathtt{esk}_1]\,\mathtt{pk}_B)$.
* 对 Bob 此时尚不知道的内容进行加密:  $\mathtt{ct}_1 = \mathrm{Enc}(10,\rho_1,r_1;\;\mathtt{key}_1)$. $\mathtt{esk}_1$ 用完即扔.

⚠️ 分清三类数据的去向:

* 经由合约上链: $C_1, \mathtt{epk}_1, \mathtt{ct}_1$.
* 留在 Alice 本地, 用完即扔: $\mathtt{esk}_1$.
* 点对点发给 Bob 的: **没有**. Bob 拿到 $(10,\rho_1,r_1)$ 的唯一途径, 是之后自己从链上解密 $\mathtt{ct}_1$.

找零那片同理: 摇 $\rho_2, r_2$, 算 $C_2 = \mathrm{Hash}(20,\mathtt{pk}_A,\rho_2,r_2)$; 摇 $\mathtt{esk}_2$, 把 $(20,\rho_2,r_2)$ 加密给自己的 $\mathtt{pk}_A$, 得 $\mathtt{epk}_2, \mathtt{ct}_2$.

💡 找零也加密给自己, 是为了换设备恢复钱包时, 只凭 `sk` 就能从链上扫回全部资产.

(2) Alice 生成证明并调用合约.

命题与进阶2 完全一致: 成员、核销、花费授权、守恒、范围、产出. 调用参数多带 $(\mathtt{epk}_1,\mathtt{ct}_1), (\mathtt{epk}_2,\mathtt{ct}_2)$ —— 它们不是公开输入, 只是随交易携带的数据.

(3) 合约校验并记账.

照旧验证 $\pi$、记核销号、插叶子; 发布事件时把 $(C_1,\mathtt{epk}_1,\mathtt{ct}_1)$, $(C_2,\mathtt{epk}_2,\mathtt{ct}_2)$ 一起发出去.

(4) Bob 被动到账.

Bob 的钱包平时就同步事件流. 对每个新输出 $(C,\mathtt{epk},\mathtt{ct})$:

* 算 $\mathtt{key} = \mathrm{KDF}([\mathtt{ivk}_B]\,\mathtt{epk})$, 试解密 $\mathtt{ct}$.
* 绝大多数输出不是给他的, 解密失败, 跳过.
* 解出 $(10,\rho_1,r_1)$ 后, 重算 $\mathrm{Hash}(10,\mathtt{pk}_B,\rho_1,r_1)$ 与链上的 $C_1$ 核对, 对上即记一笔 +10U.

⚠️ 试解密必须对全部输出逐个做, 且是纯本地行为, 不向任何服务器查询 "哪些是发给我的". 这与基础篇 "拉全量叶子、本地找 $C$" 是同一条纪律.

(5) Bob 花钱照旧.

与进阶2 第 (5) 步相同: 用 $\mathtt{sk}_B$ 派生 $\mathtt{nk}_B$, 算核销号, 证明并花掉.

## 解锁与遗留

解锁:

* 真正的被动到账: 收款只需要公布一次地址, 无需链下渠道, 无需收款时在线; 余额 = 用 `ivk` 扫链即得. 这才是 "私密支付" 该有的体验.
* 到账与花费解耦: 想花再花.
* 顺带得到一个好性质: `ivk` 只能看、不能花 (花要 `sk`). 进阶5 会用它做选择性披露.

遗留一件事: 守恒式 $\sum v_{in} = \sum v_{out} + \text{fee}$ 目前在一个电路里证, 整笔交易的所有 note 都要塞进同一个证明, 交易一大电路就跟着膨胀. 进阶4 用同态 value commitment + binding signature 把守恒挪到电路外, 做到一片 note 一个小电路.
