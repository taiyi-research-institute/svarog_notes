## 前言

承接 [zk币进阶2](./zk币进阶2.md) 的地址化池子. 本文增设一个目标:

```
把 "链下交付券明文" 换成 "链上加密备注 + 收款人试解密".
```

### 老版本的问题

进阶2 Alice 要靠链下渠道把 note 交给 Bob. 这带来两个问题:

(1) 假如 Bob 未收到消息, 钱就会锁死在池子里. 因为 note 的公钥字段写给 Bob, 就连 Alice 都花不了这笔钱.

🤦‍♂️ 就连基础版和进阶1都没有这个问题. 进阶2在这个问题上开了一点倒车.

(2) Bob 无法自主发现到账, 不守着渠道就不知道有钱进来, 谈不上 "钱包余额自动更新".

### 这一版的关键变化

(1) 引入 "收款视图密钥" $\mathtt{ivk}$.

在 $\mathtt{sk}$ 和 $\mathtt{pk}$ 之间引入 $\mathtt{ivk}$. 

```
sk -> nk;
sk -> ivk; ivk -> pk;
```

核销密钥 (旧): $\mathtt{nk}=\mathrm{Hash}(\mathtt{sk}, \texttt{"nk"})$.

收款视图密钥 (新): $\mathtt{ivk}=\mathrm{Hash}(\mathtt{sk}, \texttt{"ivk"})$.

公开收款地址 (新): $\mathtt{pk}=\mathtt{ivk}\cdot G$. 这是为了支持密钥交换.

(2) 交易逻辑变化.

登记新券时要多传两个合约参数: 临时公钥 $\mathtt{epk}$, 密文 $\mathtt{ct}$. 假设 Alice 要登记新券, 那么她要按照下式构造这两个参数, ⚠️ 式中 $\mathtt{esk}$ 用完即弃.
$$
\begin{aligned}
\mathtt{epk} &:= \mathtt{esk}\cdot G \\
\mathtt{key} &:= \mathrm{Hash}\big(\mathtt{esk}\cdot\mathtt{pk_B}\big) \\
\mathtt{ct} &:= \mathrm{Enc}\big(N;\;\mathtt{key}\big).
\end{aligned}
\tag{ephgen}
$$
Bob 通过扫链 + 尝试解密来确认到账. 具体来说, 用下式来重放对称加密的密钥, 并尝试解密每一条链上消息. 成功解密就相当于券 $N$ 到账.
$$
\mathtt{key} = \mathrm{Hash}(\mathtt{ivk_B}\cdot\mathtt{epk}).
$$
⚠️ esk, epk, ct 是不进电路的. 电路不负责对 $N$ 进行对称加密.

## 例1. Alice 给 Bob 池内转 10U.

假设 Alice 已有 $N_1=(v_1=30, \mathtt{pk_A}, \rho_1, r_1)$; Bob 已 keygen, 公布 $\mathtt{pk_B}$. 

### 1.1 Alice 印券

先看给 Bob 的那张. Alice 印券 $N_2=(v_2=10, \mathtt{pk_B}, \rho_2, r_2)$, 算承诺 $C_2$. 按公式 (ephgen) 生成 $\mathtt{epk}_2$, $\mathtt{key}_2$ 和 $\mathtt{ct}_2$, 过程中的 $\mathtt{esk_2}$ 用完即弃.

再看给自己的那张. 生成 $N_3$ (公钥写 $\mathtt{pk_A}$), $C_3$, $\mathtt{epk}_3$, $\mathtt{key}_3$ 和 $\mathtt{ct}_3$.

💡 给自己找零也加密, 这是为了换设备恢复钱包时, 只凭 $\mathtt{sk}$ 就能从链上扫回全部资产.

### 1.2 Alice 出具证明

命题与进阶2完全一致: 登记, 核销, 身份, 守恒, 范围, 金额. 调用合约增加 $(\mathtt{epk}_1,\mathtt{ct}_1)$, $(\mathtt{epk}_2,\mathtt{ct}_2)$ 参数, 这些参数不是ZK公开输入, 只是随交易携带的数据.

### 1.3 合约受理

合约照旧验 $\pi$, 核销, 登记新券. 只是发布事件时把 $(C_1,\mathtt{epk}_1,\mathtt{ct}_1)$, $(C_2,\mathtt{epk}_2,\mathtt{ct}_2)$ 一起发出去.

### 1.4 Bob 自动查账

Bob 的钱包平时就同步事件流. 对每个事件 $(C, \mathtt{epk}, \mathtt{ct})$:

* 算 $\mathtt{key}=\mathrm{Hash}(\mathtt{ivk_B}\cdot\mathtt{epk})$, 试解密 $\mathtt{ct}$.
* 绝大多数事件不是给他的, 解密失败, 跳过.
* 解出 $N_1$ 后, 重算 $\mathrm{Hash}(N_1)$ 与事件结构体里的 $C$ 核对. 对得上则记一笔 +10U.

