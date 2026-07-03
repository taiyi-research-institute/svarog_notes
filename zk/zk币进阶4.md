承接 [zk币进阶3](zk币进阶3.md) 的被动收款池子. 进阶4 只做一件事: 把余额守恒从电路里挪到电路外, 用同态 value commitment + binding signature 验证. 合约状态模型 (承诺树 cm + 核销表 nf) 仍然一点没变.

## 进阶3 留下的弱点

守恒式 $\sum v_{in} = \sum v_{out} + \text{fee}$ 是在电路里证的. 这要求整笔交易的所有 note 的金额出现在**同一个电路**的私有输入里, 带来两个问题:

* 电路形状被钉死. 2 进 2 出的电路证不了 3 进 5 出. 要么为每种形状各造一个电路, 要么把所有交易 padding 成最大形状, 白白多付证明开销.
* 证明无法拆分并行. 一笔大交易只能生成一个大证明.

理想形态: 一片 input 一个小证明, 一片 output 一个小证明, 任意 $m$ 进 $n$ 出自由拼装. 但一拆开, 守恒就没人证了 —— 每个小电路只看得见自己那片 note 的 $v$, 看不见全局.

## 结构变化

### 交易格式变化

note 本身不变. 变的是: 交易里的**每片** note (input 和 output 都算) 附带一个 value commitment:

$$
\mathtt{cv} = [v]\,V + [\mathtt{rcv}]\,R.
$$

其中 $V, R$ 是两个固定生成元, $\mathtt{rcv}$ 是为这片 note 摇的盲化因子. $\mathtt{cv}$ 上链, 但 Pedersen 承诺是隐藏的, 不泄露 $v$.

⚠️ $V, R$ 必须用 hash-to-curve 之类的方式独立生成, 保证没人知道 $\log_R V$. 后面会看到, 谁知道这个离散对数谁就能凭空增发.

### 电路 (命题) 变化

大电路拆成两种固定形状的小电路:

* spend 电路 (每片 input 一个): 成员、核销正确、花费授权, 外加一条新命题 —— $\mathtt{cv}$ 与承诺 $C$ 里藏的是**同一个** $v$.
* output 电路 (每片 output 一个): 产出承诺正确、范围 $0 \le v < 2^{64}$, 外加同一条新命题.

守恒命题从电路里**删掉了**. 没有任何电路看全局.

⚠️ 范围证明不但不能扔, 还要更严格: 守恒现在只在群里 ($\bmod$ 群阶) 成立, 没有范围钉住每个 $v$, "负数金额" 照样能让 $V$ 分量归零.

### 电路外: binding signature

守恒改由合约用 $\mathtt{cv}$ 的同态性验证. 把整笔交易的 value commitment 加加减减:

$$
\begin{aligned}
&\phantom{{}={}}\mathtt{bvk} \\
&= \sum \mathtt{cv}_{in} - \sum \mathtt{cv}_{out} - [\text{fee}]\,V \\
&= \Big[\underbrace{\textstyle\sum v_{in} - \sum v_{out} - \text{fee}}_{\text{守恒} \Rightarrow\ 0}\Big] V + \big[\Delta\mathtt{rcv}\big]\,R,
\end{aligned}
$$

其中 $\Delta\mathtt{rcv} = \sum \mathtt{rcv}_{in} - \sum \mathtt{rcv}_{out}$. (fee 是明文, 合约直接看得到.)

若守恒成立, $V$ 分量消掉, $\mathtt{bvk} = [\Delta\mathtt{rcv}]\,R$ 恰好是一把以 $R$ 为基的**签名公钥**, 私钥就是 $\mathtt{bsk} = \Delta\mathtt{rcv}$ —— 只有掌握全部 $\mathtt{rcv}$ 的交易构造者算得出.

签名方案就是普通的 Schnorr, 只是把基点从惯用的 $G$ 换成 $R$. 记 $m$ 为整笔交易的内容:

* 构造者签名: 摇 nonce $t$, 算 $T = [t]\,R$, $e = \mathrm{Hash}(T, m)$, $s = t + e \cdot \mathtt{bsk}$. 发出 $\sigma = (T, s)$.
* 合约验签: 先自己同态算出 $\mathtt{bvk} = \sum \mathtt{cv}_{in} - \sum \mathtt{cv}_{out} - [\text{fee}]\,V$, 再算 $e = \mathrm{Hash}(T, m)$, 检查

$$
[s]\,R \overset{?}{=} T + [e]\,\mathtt{bvk}.
$$

与普通验签的唯一区别: 公钥 $\mathtt{bvk}$ 不是交易者上传的, 而是合约从链上的 $\mathtt{cv}$ 加加减减**自己算出来的**. 交易者上传的只有 $\sigma = (T, s)$.

为什么这等价于守恒? 验签通过意味着构造者知道 $\mathtt{bvk}$ 关于基 $R$ 的离散对数 (Schnorr 的知识性). 若守恒不成立, $\mathtt{bvk} = [\Delta v]\,V + [\Delta\mathtt{rcv}]\,R$ 混着非零的 $V$ 分量, 知道它以 $R$ 为基的离散对数就等价于知道 $\log_R V$ —— 没人知道. 所以: 能出示合法 $\sigma$ $\iff$ $V$ 分量为零 $\iff$ 守恒.



## 例1. Bob 池内 2 进 2 出给 Carol 转 12U

Bob 手里两片 note: 进阶3 收到的 10U, 和另一片 5U. 他要给 Carol 转 12U, 给自己找零 3U. 设 fee = 0.

(1) Bob 为四片 note 各摇一个 $\mathtt{rcv}$, 算 value commitment.

```
// input
cv1 = 10*V + rcv1*R;
cv2 = 5*V + rcv2*R;

// output
cv3 = 12*V + rcv3*R;
cv4 = 3*V + rcv4*R;
```

(2) Bob 生成 4 个小证明.

* 2 个 spend 证明: 各证一片 input 的成员、核销、授权、$\mathtt{cv}$ 一致.
* 2 个 output 证明: 各证一片 output 的承诺正确、范围、$\mathtt{cv}$ 一致.

output note 的构造与加密备注照进阶3, 不再重复. 4 个证明互相独立, 可并行生成.

(3) Bob 算 binding signature.

$$
\mathtt{bsk} = (\mathtt{rcv}_1 + \mathtt{rcv}_2) - (\mathtt{rcv}_3 + \mathtt{rcv}_4),
$$

用 $\mathtt{bsk}$ 对整笔交易内容 $m$ (全部证明、核销号、新叶子、$\mathtt{cv}$、加密备注) 做基为 $R$ 的 Schnorr 签名, 得 $\sigma = (T, s)$. 调用合约, 参数: 4 个证明、2 个核销号、2 片新叶子、4 个 $\mathtt{cv}$、2 份加密备注、交易签名 $\sigma$.

(4) 合约校验并记账.

* 逐个验 4 个小证明, 核对 2 个核销号未用过.
* 同态算 $\mathtt{bvk} = \mathtt{cv}_1 + \mathtt{cv}_2 - \mathtt{cv}_3 - \mathtt{cv}_4$. 本例 10 + 5 = 12 + 3, $V$ 分量抵消, 展开后 $\mathtt{bvk} = [\mathtt{rcv}_1 + \mathtt{rcv}_2 - \mathtt{rcv}_3 - \mathtt{rcv}_4]\,R$  $= [\mathtt{bsk}]\,R$, 正是 Bob 签名私钥对应的公钥.
* 算 $e = \mathrm{Hash}(T, m)$, 检查 $[s]\,R = T + [e]\,\mathtt{bvk}$. 因为上一条成立, Bob 的 $\sigma$ 能通过; 换任何一个金额 (比如把 output 改成 13U), $\mathtt{bvk}$ 就混进 $V$ 分量, 谁也签不出来.
* 照旧记核销号、插叶子、发事件.

合约全程不知道 10、5、12、3 中的任何一个数, 只知道它们配平了.

## 例2. Carol 提现 4U 到公链地址

Carol 花掉例1 收到的 12U note: 提 4U 到自己的公链地址 `addrCarol`, 找零 8U. 设 fee = 0.

要点先行: 明文出金与 fee 的地位完全相同 —— 都是合约看得见的量, 由合约亲手以 $V$ 分量计入 $\mathtt{bvk}$.

(1) Carol 摇 $\mathtt{rcv}$, 算 value commitment.

```
// input
cv1 = 12*V + rcv1*R;

// output (找零)
cv2 = 8*V + rcv2*R;
```

提现的 4U 没有 cv —— 它是明文, 不需要藏.

(2) Carol 生成 1 个 spend 证明、1 个 output 证明, 照例1.

(3) Carol 算 binding signature.

$\mathtt{bsk} = \mathtt{rcv}_1 - \mathtt{rcv}_2$, 对整笔交易内容 $m$ 签名得 $\sigma$ —— 注意 $m$ 里包含明文金额 4 和 `addrCarol`.

(4) 合约校验并放款.

$$
\begin{aligned}
&\phantom{{}={}}\mathtt{bvk} \\
&= \mathtt{cv}_1 - \mathtt{cv}_2 - [4]\,V \\
&= [12 - 8 - 4]\,V + [\mathtt{rcv}_1 - \mathtt{rcv}_2]\,R \\
&= [\mathtt{bsk}]\,R,
\end{aligned}
$$

验 $\sigma$ 通过, 则记核销号、插找零叶子、向 `addrCarol` 转出 4U.

💡 进阶1~3 的提现要靠哑约束把公链地址焊进证明; 到这一级哑约束可以退休了 —— $\sigma$ 签的就是整笔交易, 谁想换掉 `addrCarol` 或改明文金额, 验签直接失败.

## 解锁与遗留

解锁:

* 电路形状解耦: 只需 spend、output 两个固定小电路, 任意 $m$ 进 $n$ 出自由拼装, 证明并行生成.
* 整笔交易焊成一体: $\sigma$ 盖住全部内容, 谁也无法把两笔交易的证明拆出来重新拼装 (mix-and-match), 也改不了 fee.

遗留一件事: 一个 `sk` 只对应一个地址 `pk`. 地址一复用, 曾给同一个人打过款的发送方们就能互相比对、拼出这个收款人的画像; 而完全不复用又要管理一堆 `sk`. 进阶5 用多样化地址解决它, 顺带把 `ivk` 变成给审计方的选择性披露工具.
