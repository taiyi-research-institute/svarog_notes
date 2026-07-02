承接 [zk币进阶1](zk币进阶1.md) 的任意面额池. 进阶2 只做一件事: 把 "谁知道秘密谁拥有" 换成 "谁持有私钥谁拥有". 合约状态模型 (承诺树 cm + 核销表 nf) 仍然一点没变.

## 进阶1 留下的弱点

在进阶1, 所有权 = 知道 $(v, k, r)$, 转账 = 把这组秘密交出去. 这有两个问题:

* 发送方抢跑. Alice 把 note 发给 Bob 之后自己仍然知道 $(v, k, r)$, 理论上能抢在 Bob 之前把钱花掉. Bob 收到 note 后必须立刻转成只有自己知道的新 note 才安全.
* 没有 "地址". Bob 想收钱, 只能等 Alice 造好 note 再私下把秘密传给他, 无法像普通链那样公布一个收款地址.

## 结构变化

### note 结构变化

引入密钥层级. Bob 一次性生成:

```
sk -> nk, pk
```

* 根秘密 `sk`.
* 核销密钥 `nk = KDF(sk, "nk")`.
* 公开收款地址 `pk = KDF(sk, "pk")`.

note 从 $(v, k, r)$ 变成 $(v, \mathtt{pk}, \rho, r)$:

$$
C = \mathrm{Hash}(v,\mathtt{pk},\rho,r).
$$

核销号的原像 $k$ 被拆成了两半: Alice 摇一个公开的一次性编号 $\rho$, Bob 从他自己的 `sk` 衍生出核销密钥 `nk`. 最终的核销号为
$$
h = \mathrm{PRF}(\rho;\; \mathtt{nk}).
$$
如此, Alice 知道 note 的全部字段, 但算不出核销号 $h$, 因此花不掉这张 note.

### 电路 (命题) 变化

与进阶1 相比, 电路的命题变了两条:

(1) 负责核销的命题变为: 存在 $\mathtt{sk}$ 使得
$$
\begin{aligned}
\mathtt{pk}&=\mathrm{KDF}(\mathtt{sk}, \texttt{"pk"}) \\
\land\quad h&=\mathrm{PRF}\big(
\rho;\;
\mathrm{KDF}(\mathtt{sk},\texttt{"nk"})
\big).
\end{aligned}
$$
(2) 新增花费授权命题: 签名与 note 公钥同源.

⚠️ 电路里必须约束 `pk` 和 `nk` 出自同一个 `sk`.

## 例1. Alice 池内给 Bob 转 10U (按地址)

Bob 事先公布地址 $\mathtt{pk}_B$. Alice 手里有一片 30U 的 note $(30,\mathtt{pk}_A,\rho_0,r_0)$, 已在树中.

(1) Alice 造两片 output note.

给 Bob 一片: 摇 $\rho_1, r_1$, 算 $C_1 = \mathrm{Hash}(10,\mathtt{pk}_B,\rho_1,r_1)$.

给自己找零一片: 摇 $\rho_2, r_2$, 算 $C_2 = \mathrm{Hash}(20,\mathtt{pk}_A,\rho_2,r_2)$.

注意 Alice 只需要 Bob 的公开地址 $\mathtt{pk}_B$, 不需要和 Bob 有任何事前的秘密交接.

(2) Alice 生成证明并调用合约.

对 input note 算 $h_0 = \mathrm{PRF}(\rho_0;\;\mathtt{nk}_A)$. 照旧重放 Merkle 树, 拿到路径和近期根 $R$. 要证的命题:

* 成员: $(30,\mathtt{pk}_A,\rho_0,r_0)$ 在根为 $R$ 的树里;
* 核销正确: $h_0$ 与 $\mathtt{pk}_A$ 都来自 $\mathtt{sk}_A$.
* 花费授权: 知道 $\mathtt{sk}_A$.
* 守恒: 30 = 10 + 20 + fee, 设 fee = 0;
* 范围: 10 和 20 都落在 $[0, 2^{64})$;
* 产出: $C_1, C_2$ 分别是两片输出 note 的正确承诺.

调用合约: 传证明 $\pi$; 公开输入: 近期根 $R$, 核销号 $h_0$, 两片新叶子 $C_1, C_2$.

(3) 合约校验并记账.

验证 $\pi$ 对某近期根成立, 且 $h_0$ 未核销. 通过则把 $h_0$ 记入已核销, 把 $C_1, C_2$ 插入 Merkle 树并发布事件. 与进阶1 完全一致 —— 合约根本感知不到 "地址" 这一层, 状态模型没动.

(4) Alice 把 note 明文发给 Bob.

Alice 私下把 $(10,\mathtt{pk}_B,\rho_1,r_1)$ 发给 Bob. Bob 核对 $C_1$ 确实在树里, 即确认到账.

与进阶1 的本质区别: 这份明文泄露给谁都不怕. 知道它只能 "看见" 这片钱 (金额、收款人), 花它需要 $\mathtt{sk}_B$. 特别地, Alice 自己也花不掉.  Bob 不再需要收款后立刻转存.

(5) Bob 以后花钱.

Bob 用 $\mathtt{sk}_B$ 派生 $\mathtt{nk}_B$, 算 $h_1 = \mathrm{PRF}(\rho_1;\;\mathtt{nk}_B)$, 照 (2) 的方式证明并花掉.

## 解锁与遗留

解锁两件事:

* 按地址收款: 公布 pk 即可, 收款前无需任何秘密交接.
* 发送方事后无法再花已发出的钱: 所有权从 "知道秘密" 收紧为 "持有私钥".

遗留一件事: 第 (4) 步 Alice 仍要靠链下渠道把 note 明文交给 Bob, Bob 才知道自己收了钱. 进阶3 用链上加密备注 + 试解密解决它, 实现真正的被动收款.
