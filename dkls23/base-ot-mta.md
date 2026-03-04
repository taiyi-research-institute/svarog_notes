# 为什么要做 MtA

ECDSA签名就是在计算

$$
\begin{align}
k &\leftarrow \mathbb{Z}_q; \textrm{也就是1到q的均匀随机数}\\
R &= kG; \\
s &= k^{-1}(m+R.x \cdot \mathtt{sk}).
\end{align}
$$

在 MPC 中, 各方有随机的 $k_i$, 很容易算出 $R$. 然而算 $s$ 的时候要算 $k^{-1}$. 如果直接把 $k_i$ 加起来, 那就泄露了 $k$, 从而泄露私钥. 因此需要对 $s$ 进行变形.

设非0随机数 $\gamma$. 则

$$
s = (k\gamma)^{-1}\left(m+R.x \cdot (\mathtt{sk}\cdot \gamma)\right).
$$

有了这个变形, MtA (Multiplication to Addition) 马上就要登场了. 我们不需要预先指定 $\gamma$. 实际上这是件先打枪再画靶子的事情. 我们要求各方生成秘密随机数 $\gamma_i$, 并约定 $\gamma=\sum_i \gamma_i$.

然后, 对于不同的两方 $i, j$, 不妨假设 $i < j$, i 为先手方, j 为后手方. 我们假设存在一种协议, 使得先手方得到秘密 $a_{i,j}$, 后手方得到秘密 $b_{i,j}$, 满足:

$$
a_{i,j}+b_{j,i}=k_j\cdot \gamma_i.
$$

简单验算一下就能知道, 把所有的 $a_{i,j}$ 和 $b_{i,j}$ 加起来就能得到 
$k\gamma$. 各方得到相同的明文 $k\gamma$, 因此可以直接求逆. 乘法因子难以分解, 这保证了 $k$ 不会泄露. 用类似的方法可以算出 $\mathtt{sk}\cdot \gamma$.

Q: 我们可能会问, a,b 两种份额都是秘密的, 怎么传输和求和呢?

站在第 i 方的视角上, 他作为先手方, 持有与其他 $j$ 生成的先手份额 $a_{i,:}$; 他作为后手方, 持有与其他 $j$ 生成的后手份额 $b_{:,i}$. 他把自己的ab份额加起来, 把这个和记为 $\sigma_i$. 加项难以分解, 这保证了具体的 $a, b$ 份额不会泄露.

# 基于位分解OT的 MtA.

今有Alice, Bob两方, 分别持有秘密值 $x_a \bmod q$, $x_b \bmod q$.
他们要得到另外的秘密值 $y_a, y_b$, 使得
$$
y_a + y_b=x_a\cdot x_b \pmod q.
$$

这里 $q$ 是质数, 比如曲线的阶.

怎么做? 一个朴素的办法如下, 称为 "位分解OT(不经意传输)".

## 位分解的逻辑

(0) Bob 获取 $x_b$ 的二进制表示, 记为
$$
x_b=\sum_k d_k2^k.
$$

(1) Alice 对每个 $k$, 摇随机数 $r_k\leftarrow \mathbb{Z}_q$. 准备好两条消息. 这两条消息既不明文发送, 也不一起发送. 下一节会讲为什么.
$$
\begin{align}
m[k,0]&=r_k \\
m[k,1]&=r_k+x_a\cdot 2^k \bmod q.
\end{align}
$$

(2) 对每个 $k$, 双方执行一次 1-out-of-2 OT 协议. 协议执行之后, Bob 得到 $m[k,d_k]$. 下一节会讲这是个什么协议.

(3) Alice和Bob计算各自的本地份额 
$$
\begin{align}
y_a&=-\sum_k r_k \bmod q; \\
y_b&=\sum_k m[k,d_k] \bmod q.
\end{align}
$$

(Finally...) 验算一下.

$$
\begin{align}
y_b&=\sum_k\left( r_k + d_k \cdot x_a\cdot 2^k \right) \\
&=\sum_k r_k + x_a \sum_k d_k2^k \\
&=-y_a+x_a\cdot x_b.
\end{align}
$$

## OT的逻辑

在位分解的第2步中, Bob 不可以把 $d_k$ 告诉 Alice, 因为Alice集齐所有 $d_k$ 就能算出 $x_b$.
Alice 也不可以把两个 $m[k, :]$ 都告诉 Bob, 因为 Bob 把二者相减就得到 $x_a$.

问题来了, Bob 怎么隐蔽地做选择? 

我们假设 Bob 要在 $m_0$, $m_1$ 中选 $m_d$.

(1) Alice 摇随机数 $\alpha \leftarrow \mathbb{Z}_q$. 计算 $A:=\alpha G$ 告诉 Bob.

(2) Bob 摇随机数 $\beta \leftarrow \mathbb{Z}_q$. 计算
$$
B=\begin{cases}
\beta G & \textrm{if~} d=0, \\
\beta G+A & \textrm{if~} d=1,
\end{cases}
$$
然后告诉 Alice.

这里的 insight 是: Bob 选0还是1藏在B的构造里, 对Alice来说只是曲线上随机均匀分布的点. (严格地说, 点的分布非常接近均匀分布).

(3) Alice 计算两个密钥
$$
K_0=\mathrm{Hash}(\alpha B), K_1=\mathrm{Hash}(\alpha(B-A)).
$$

计算两个对称加密的密文
$$
C_0=\mathrm{Enc}(K_0, m_0), C_1=\mathrm{Enc}(K_1, m_1).
$$

把两个密文告诉 Bob.

(4) Bob 只能算出一个密钥, 就是 $K=\mathrm{Hash}(\beta A)$. 其恰好等于 $K_0, K_1$ 中的某一个. 这就让 Bob 只能解密两个密文中的一个, 解不开另一个. 具体来说, 当 $d=0$ 时能解开 $C_0$, 当 $d=1$ 时能解开 $C_1$.

如此, Bob就获取了他想选择的 $m$, 并且双方都没暴露 $x_a, x_b$.
