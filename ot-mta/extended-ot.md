以下是 iknp03 半诚实安全的算法骨架. 需要再加 KOS/SoftSpokenOT 等一致性检查手段.

## 用 Base OT 为 Payload OT 生成种子

消息长度为 $\lambda$, OT 询问个数为 $\kappa$. 有几个 OT 询问, 就有几个选择位. 很多实现取 $\lambda=\kappa$.

Bob 随机摇 $2\kappa$ 个随机消息, 记为 $k_{0,i}$ 和 $k_{1,i}$, 范围: $1 \le i \le \kappa$.

Alice 随机摇 $\kappa$ 个选择, 记为 $s_i$. 范围: $i$ 同上, $s_i\in\left\{0,1\right\}$.

Alice 通过朴素 OT 从 Bob 获得 $k_{s_i,i}$.

种子可以长期保留.

## 交换 Payload OT 密钥

### 校正矩阵 U

设有 $m$ 次 Payload OT 询问.
找一个哈希函数 $G: \left\{0,1\right\}^\lambda \rightarrow \left\{0,1\right\}^m$. 实现上可以选择 AES-CTR, ChaCha20 等.

Bob 算出两个 $\kappa\times m$ 的扩展矩阵 $T_0$, $T_1$.
Alice 算出一个 $\kappa\times m$ 的扩展矩阵 $T$. 这些矩阵的第 $i$ 行分别是:

$$
\begin{align}
(T_0)_{i,*}&=G(k_{0,i}), \\
(T_1)_{i,*}&=G(k_{1,i}), \\
T_{i,*}&=G(k_{s_i,i}).
\end{align}
$$

所谓 "带相关矩阵" 本质就是把 Bob 在 Payload OT 中的选择向量 $b\in\left\{0,1\right\}^m$ 注入到前述随机矩阵 $T$ 里.

Bob 逐行计算并发送矩阵 $U$, 称为校正矩阵, 算法如下. 这里 $\oplus$ 是按位异或.
$$
U_{i,*} = (T_0)_{i,*} \oplus (T_1)_{i,*} \oplus b.
$$

### 密钥矩阵 Q

Alice 逐行计算矩阵 $Q$, 算法如下.
$$
Q_{i,*} = T_{i,*} \oplus (s_i\cdot U_{i,*}).
$$

我们揭示一下 $Q_{i,*}$ 到底有什么意义. 实际上,
* 当 $s_i=0$ 时, $Q_{i,*}=(T_0)_{i,*}$;
* 当 $s_i=1$ 时, $Q_{i,*}=(T_0)_{i,*}\oplus b$. 证明如下式.

$$
\begin{align}
Q_{i,*}&=(T_1)_{i,*}\oplus U_{i,*}\\
 &= (T_1)_{i,*}\oplus (T_0)_{i,*} \oplus (T_1)_{i,*} \oplus b \\
 &=(T_0)_{i,*} \oplus b.
\end{align}
$$

安全性: Alice 只拿到 $k_{s_i,i}$, 拿不到另一条 $k_{1-s_i,i}$.
因此她只知道 $T_0, T_1$ 的其中一个, 不可能知道 $T_0\oplus T_1$.
如此, 在 Bob 那边就相当于用 $T_0\oplus T_1$ 对 $b$ 进行异或加密.

### 密钥 K

最后, Alice 对第 $j$ 个询问 (也就是每列 $j$) 计算两把密钥, 算法如下.
$$
\begin{align}
K_{0,j}&=\mathtt{Hash}(Q_{*,j}),\\
K_{1,j}&=\mathtt{Hash}(Q_{*,j} \oplus s).
\end{align}
$$

Bob 对第 $j$ 个询问计算一把密钥, 算法如下.
$$
K_{b_j,j}=\mathtt{Hash}((T_0)_{*,j}).
$$

验算: 
* 当 $b_j=0$ 时, $K_{0,j}=\mathtt{Hash}((T_0)_{*,j})$;
* 当 $b_j=1$ 时, $K_{1,j}=\mathtt{Hash}\left(((T_0)_{*,j}\oplus s) \oplus s\right)$.

交换密钥之后, Alice 就可以对第 i 对消息进行对称加密, 然后发给 Bob. Bob 只能解密其中一个, 因为他不知道 $s$.

### 变量的生命周期

种子 $k$, 以及相应的选项 $s$ 可以长期保留. 也就是说可以放进keystore.

矩阵 $T_0, T_1$ 是一次性的.
如果复用, 那么对于Bob的两场询问 $b, b'$, Alice就可以算
$$
b\oplus b'=U\oplus U'.
$$

这虽然没有直接泄露 $b$ 或 $b'$ 中的任何一个, 但是泄露了二者的异或值.
