在 [进阶1](./zk币进阶1.md) , 所有权 = 知道 $N=(v, k, r)$, 转账 = 把这组秘密交出去. 这有两个问题:

* 发送方抢跑. Alice 把券发给 Bob 之后自己仍然知道 $(v, k, r)$, 理论上能抢在 Bob 之前把钱花掉. Bob 收到券后必须立刻转成只有自己知道的新券才安全.
* 没有 "地址". Bob 想收钱, 只能等 Alice 造好券再私下把秘密传给他, 无法像普通链那样把收款地址告诉付款人.

跟 [进阶1](./zk币进阶1.md) 相比, 券结构升级为下式
$$
N=(v,\mathtt{pk},\rho,r). \tag{note}
$$
核销号升级为下式
$$
h=\mathrm{Hash}(\rho,\mathtt{nk}). \tag{nf}
$$
$\mathtt{pk}$, $\mathtt{nk}$ 是从 $\mathtt{sk}$ 导出的, 具体方式如下式,
$$
\begin{aligned}
\mathtt{nk}&=\mathrm{Hash}(\mathtt{sk}, \texttt{"nk"}),\\
\mathtt{pk}&=\mathrm{Hash}(\mathtt{sk}, \texttt{"pk"}).
\end{aligned}
\tag{keygen}
$$
以上数学构造决定了这一版本的特点:

* 谁持有背后的 $\mathtt{sk}$, 谁就能花这张券. 别人不能.
* 把 $\mathtt{pk}$ 写给谁, 谁就能花这张券. 别人不能, 哪怕印券者也不能.

⚠️新的**纪律**: $\mathtt{pk}$ 不要上链, 可以公示, 最好只告诉付款人. 违反纪律的后果是收款人的资金去向对全网公开, 尤其是暴露 $\mathtt{pk}$ 与公链地址的关联.

## 例1. Alice 存 30U

### 1.0 Alice 生成密钥

按公式 (keygen), Alice 生成 $\mathtt{sk_A}$, $\mathtt{nk_A}$, $\mathtt{pk_A}$.

### 1.1 Alice 印新券

Alice 印一张给自己的券 $N_1=(v_1=30,\mathtt{pk_A},\rho_1,r_1)$, 算 $C_1=\mathrm{Hash}(N_1)$.

照 [进阶1](./zk币进阶1.md), Alice 生成金额证明 $\pi_0$: 公开输入是 $C_1$, $v_1$, 命题是存在 $\mathtt{pk_A}, \rho_1, r_1$ 使得 $C_1 = \mathrm{Hash}(v_1, \mathtt{pk}, \rho, r)$.

⚠️ 与进阶1 的差别只有命题里的承诺换成新格式. 特别地, $\mathtt{pk_A}$ 照纪律留在见证里: 合约只需要核对金额, 不需要知道这张券归谁.

Alice 给合约发送 $C_1$ 和 $\pi_0$, 并转账 30U.

### 1.2 合约登记新券

合约确认收到的 30U 恰为 $\pi_0$ 的公开输入 $v_1$, 确认 $\pi_0$ 成立, 且 $C_1$ 未登记. 然后登记 $C_1$. 跟 [进阶1](./zk币进阶1.md) 一样.

## 例2. Alice 池内给 Bob 转 10U

### 2.0 Bob 生成密钥

按公式 (keygen), Bob 生成 $\mathtt{sk_B}$, $\mathtt{nk_B}$, $\mathtt{pk_B}$.

Bob 给 Alice 发送 $\mathtt{pk_B}$.

### 2.1 Alice 印新券

接例1, Alice 手里有那张已登记的 30U 券 $N_1$.

Alice 给自己找零一张 $N_2=(v_2=20, \mathtt{pk_A}, ...)$.

Alice 给 Bob 发送一张 $N_3=(v_3=10,\mathtt{pk_B},...)$.

### 2.2 Alice 生成证明, 调用合约

重放 $h_1=\mathrm{Hash}(\rho_1, \mathtt{nk_A})$, $C_1=\mathrm{Hash}(N_1)$, 重放 Merkle 根 $R_1$ 和登记路径 $(i_1, P_1)$.

公开输入: $h_1$, $R_1$, $C_2$, $C_3$.

⚠️ 根据本文开头的纪律, 不能把 $\mathtt{pk_A}$ 作为公开输入.

见证: $N_1$, $i_1$, $P_1$, $N_2$, $N_3$, $\mathtt{sk_A}$. 

约束:

* 登记. 跟 [进阶1](./zk币进阶1.md) 一样, 从 $\mathrm{Hash}(N_1)$ 沿着 $(i_1, P_1)$ 逐层哈希恰为给定的根 $R_1$.
* 核销 ※. 对 [进阶1](./zk币进阶1.md) 大改. 存在 $\mathtt{sk_A}$ 使得

$$
h_1=\mathrm{Hash}\big(
\rho_1,\;
\mathrm{Hash}(\mathtt{sk_A},\texttt{"nk"})
\big). \tag{nf-circ}
$$

  注意核销用不到公钥, 用到的是核销密钥 $\mathtt{nk_A} = \mathrm{Hash}(\mathtt{sk_A},\texttt{"nk"})$.

* 身份. $N_1$ 与 $h_1$ 依赖同一个 $\mathtt{sk_A}$: 登记约束里 $N_1$ 的地址字段满足 $\mathtt{pk_A}=\mathrm{Hash}(\mathtt{sk_A}, \texttt{"pk"})$, 式中 $\mathtt{sk_A}$ 与 (nf-circ) 用的是同一个见证 entry.
* 守恒, 范围, 金额. 跟 [进阶1](./zk币进阶1.md) 一样.

最后 Alice 给合约传证明 $\pi$ 以及公开输入.

### 2.3 合约登记

合约验 $\pi$, 核销 $h_1$, 登记 $C_2$, $C_3$, 跟 [进阶1](./zk币进阶1.md) 一样.

以后不再罗里吧嗦说 "若 $h_1$ 未核销则记为已核销", 默认这个 check-if 逻辑隐含在 "核销" 这个动词里.

## 例3. Bob 提现到公链地址

Bob 把例2 收到的 10U 提 4U 到自己的公链地址 `addr`, 找零 6U 留在池内.

注意 `addr` 是公链地址, 与池内地址 $\mathtt{pk_B}$ 不相干的.

### 3.1 Bob 印券

生成 $N_4=(v_4=6, \mathtt{pk_B}, ...)$. 算 $C_4=\mathrm{Hash}(N_4)$.

### 3.2 Bob 生成证明, 调用合约

准备工作: 重放 $R_3$, $C_3$, $h_3$, $i_3$, $P_3$.

公开输入: $h_3$, $R_3$, $C_4$, `addr`, 提现金额 4.

见证: $N_3$, $i_3$, $P_3$, $N_4$, $\mathtt{sk_B}$.

约束:

* 核销: 套用公式 (nf-circ).
* 登记: 从 $\mathrm{Hash}(N_3)$ 沿着 $(i_3, P_3)$ 逐层哈希恰为给定的根 $R_3$.
* 身份: $N_3$ 与 $h_3$ 依赖同一个 $\mathtt{sk_B}$.
* 地址, 守恒, 范围, 金额.

Bob 给合约发送证明和相应的公开输入.

### 3.3 合约受理 Bob 业务

合约检验证明, 核销 $h_3$, 登记 $C_4$, 给 `addr` 打 4U.

## 讨论

解锁两件事:

* 按地址收款: 收款人只需事先把 $\mathtt{pk}$ 告诉付款人. 收款前无需任何秘密交接.
* 发送方事后无法再花已发出的钱: 所有权从 "知道秘密" 收紧为 "持有私钥".

遗留一件事: Alice 仍要靠链下渠道把券明文交给 Bob, Bob 才知道自己有钱. 进阶3 用链上加密备注 + 试解密解决它, 实现真正的被动收款.
