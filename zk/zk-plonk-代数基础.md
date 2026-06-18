

从运算到零知识证明: PLONK 式证明系统的代数基础

本文讲一个运算如何被改写成多项式约束, 这些约束如何被一个简短的协议验证.

# 1. 全景: 五步流水线

零知识证明要证的是: 某运算在某输入输出下确实执行过. 整条改写链可以压成五步.

1. 把运算拆成只含加法和乘法的基本门, 得到一个算术电路.
2. 运算 "执行过一遍" 等价于填好一张表 ( 每根线一个域元素 ) , 且每一行都满足门规则.
3. 把表的每一列插值成一条多项式.
4. "每行门都成立" 于是变成 "某条多项式在一组点上全为零", 而这又等价于 "它能被一个固定多项式整除". $N$ 条约束坍缩成 $1$ 条多项式恒等式.
5. 验证者只在一个随机点抽查这条恒等式, 并用多项式承诺让 "在某点取值" 既简洁又防赖账.

后面逐步展开.

---

## 2. 算术化: 多项式约束从哪来

贯穿全节的例子: 证明 "我知道一个 $x$, 使得 $x^3 + x + 5 = 35$" . 答案是 $x = 3$, 但不想把 $x$ 直接告诉验证者.

### 2.1 运算 → 算术电路

在有限域 $\mathbb{F}_p$ 上, 任何运算都能拆成一串只有加和乘的基本门. 上面的式子拆开是:

```
v1  = x  * x      ( = 9 )
v2  = v1 * x      ( = 27 )
v3  = v2 + x      ( = 30 )
out = v3 + 5      ( = 35 )
```

每一行是一个门. 一个门只管三根线: 左输入 $a$, 右输入 $b$, 输出 $c$ .

### 2.2 执行 = 填一张轨迹表

把每个门排成表的一行. 再用统一的门方程套住所有门:

$$q_L \cdot a + q_R \cdot b + q_M \cdot (a b) + q_O \cdot c + q_C = 0 .$$

乘门设 $q_M = 1, q_O = -1$ ( 即 $a b - c = 0$ ) , 加门设 $q_L = q_R = 1, q_O = -1$ ( 即 $a + b - c = 0$ ) . 代入 $x = 3$ 得到这张轨迹表:

| 行 | $a$ | $b$ | $c$ | 类型 | 激活的 selector |
|---|---|---|---|---|---|
| 1 | 3 | 3 | 9 | 乘 | $q_M = 1, q_O = -1$ |
| 2 | 9 | 3 | 27 | 乘 | $q_M = 1, q_O = -1$ |
| 3 | 27 | 3 | 30 | 加 | $q_L = q_R = 1, q_O = -1$ |
| 4 | 30 | 5 | 35 | 加 | $q_L = q_R = 1, q_O = -1$ |

"运算被正确执行过" 现在严格等价于: 存在这样一张表, 每行都满足门方程, 且输入那列等于 $x$, 输出那行等于 $35$ . 证明者知道整张表 ( 这就是 witness ) . 注意到这一步全是代数等式, 还没有多项式.

### 2.3 把每一列插值成多项式

选一组求值点 $H = \{ \omega^0, \omega^1, \omega^2, \omega^3 \}$ ( 通常取单位根 ) . 对每一列, 找那条唯一穿过这些点的低次多项式. 例如输出列 $c$, 就找 $c(X)$ 满足

$$c(\omega^0) = 9, \quad c(\omega^1) = 27, \quad c(\omega^2) = 30, \quad c(\omega^3) = 35 .$$

这一步叫插值. 它把 "离散的一列数" 变成 "一条连续的多项式曲线" . 同样地, $a$ 列, $b$ 列, 以及所有 selector 列都各自插成 $a(X), b(X), q_L(X), \dots$ 现在所有东西都是多项式了.

### 2.4 门规则坍缩成一条恒等式

把门方程里每个符号换成对应的多项式, 得到组合多项式

$$G(X) = q_L(X) a(X) + q_R(X) b(X) + q_M(X) a(X) b(X) + q_O(X) c(X) + q_C(X) .$$

"第 $i$ 行的门成立" 就是 $G(\omega^i) = 0$ ( 这里 $i$ 是行号, 从 $0$ 到 $n - 1$ ) . "每行都成立" 就是 $G(X)$ 在 $H$ 的每个点上都等于零. 关键事实: 一个多项式在 $H$ 上全为零, 当且仅当它能被这组点的消失多项式整除. 当 $H$ 取单位根时,

$$Z_H(X) = \prod_{i=0}^{n-1} (X - \omega^i) = X^n - 1 .$$

于是 $N$ 条独立约束变成唯一一条多项式恒等式:

$$G(X) = (X^n - 1) \cdot t(X) , \qquad t(X) = \frac{G(X)}{Z_H(X)} .$$

商 $t(X)$ 是真多项式, 当且仅当所有门都满足. 多项式约束就此诞生: 它不是凭空设计的, 而是 "一整张执行表都合法" 这件事的等价改写.

### 2.5 选择子多项式怎么算

selector ( $q_L, q_R, q_M, q_O, q_C$ ) 只由电路结构决定, 与 witness 无关, 所以在 setup 阶段一次性插好并公开.

最干净的理解: selector 是指示函数的叠加. 设 $L_i(X)$ 是在第 $i$ 行取 $1$ , 在其余所有行取 $0$ 的 Lagrange 基多项式 ( "只在一行鼓一个包" ) , 则一个在行集合 $S$ 上被激活的 selector 就是

$$q(X) = \sum_{i \in S} L_i(X) .$$

在本例中加门是第 $3, 4$ 行, 所以 $q_L(X) = L_2(X) + L_3(X)$ . 它在两行取 $1$, 在另两行取 $0$, 没有任何冲突: 四个条件落在四个不同的点上, 而四个不同点上的任意四个目标值都对应唯一一条 $3$ 次多项式 ( Vandermonde 矩阵可逆 ) .

**具体算一遍.** 取 $\mathbb{F}_5$ , 其乘法群是 $4$ 阶, 生成元 $2$ 是本原 $4$ 次单位根:

$$\omega^0 = 1, \quad \omega^1 = 2, \quad \omega^2 = 4, \quad \omega^3 = 3 \qquad ( 4 = -1 = \omega^2, \ 2^4 = 16 = 1 ) .$$

要 $q_L$ 在 $1, 2$ 处取 $0$, 在 $4, 3$ 处取 $1$ . 因为它在 $1, 2$ 处为零, 先抽因子 $q_L(X) = (X - 1)(X - 2) \cdot g(X)$ , $g$ 是一次多项式. 由 $q_L(4) = 1$ 和 $q_L(3) = 1$ 解出 $g(X) = 3X + 4$ , 所以 ( 全部 mod $5$ )

$$q_L(X) = (X - 1)(X - 2)(3X + 4) = 3X^3 + 4X + 3 .$$

验证: $q_L(1) = 0$, $q_L(2) = 0$, $q_L(4) = 1$, $q_L(3) = 1$ , 四点全中. ( 真实系统里这个域是一个 $255$ 比特素数, 这里用 $5$ 只是为了根小, 能心算. )

---

## 3. 分工: PLONK 与 IPA / KZG

它们不是竞争关系, 而是一个 SNARK 里上下相邻的两层.

- **PLONK** 处在算术化加多项式 IOP 这两层 ( 前端加协议 ) . 它把运算编码成上面的恒等式, 并给出一个在 "能查询任意多项式取值" 这个理想假设下证明恒等式成立的交互协议. PLONK 对承诺方案不可知, 只假设 "存在某种多项式承诺" . halo2 用的是它的推广 PLONKish: 自定义门加 lookup.
- **Bulletproofs / IPA ( 或 KZG )** 处在多项式承诺这一层 ( 后端 ) . 它解决 PLONK 留下的那个理想假设: 怎么把抽象的多项式 oracle 用真东西实例化, 即承诺一条多项式并证明它在某点的取值.

zcash halo2 选 IPA ( 无可信设置 ) ; 以太坊生态的 PSE fork 选 KZG ( 验证 $O(1)$, 但需可信设置 ) . 同一个名字下分出两条分支, 区别就在这一层.

---

## 4. 朴素交互协议 ( prover 与 verifier )

下面是最朴素的交互版本, 只证门约束, 三条消息按通信分三轮. 砍掉了连线约束, 公共输入绑定, 零知识盲化 ( 见第 6 节 ) .

**公共约定 ( 双方事先共享 ) .** 域 $\mathbb{F}$ ; 求值域 $H = \{ \omega^0, \dots, \omega^{n-1} \}$ ; 消失多项式 $Z_H(X) = X^n - 1$ ; 公开的 selector $q_L, q_R, q_M, q_O, q_C$ ; 一个多项式承诺方案, 三个接口 $\mathsf{Commit}, \mathsf{Open}, \mathsf{Check}$ .

**Prover 私有输入.** 由轨迹插值出的 $a(X), b(X), c(X)$ , 据此构造 $G(X)$ 和 $t(X) = G(X) / Z_H(X)$ .

**第 1 轮 — P → V ( 承诺 ) .** 发送四个承诺, 不含任何取值:

$$C_a = \mathsf{Commit}(a), \quad C_b = \mathsf{Commit}(b), \quad C_c = \mathsf{Commit}(c), \quad C_t = \mathsf{Commit}(t) .$$

此刻四条多项式已被密码学冻结.

**第 2 轮 — V → P ( 挑战 ) .** 抽一个随机点并发回:

$$\zeta \xleftarrow{\ \$\ } \mathbb{F} \setminus H .$$

之所以排除 $H$: $Z_H(\zeta) = \zeta^n - 1 = 0$ 当且仅当 $\zeta \in H$ , 落在 $H$ 上会让检查退化, 测不到整除关系. 注意 $H$ 是全部 $n$ 个单位根, 不是单个 $\omega$ ; 真实系统要求 $|\mathbb{F}| \gg n$ 才有足够的随机点.

**第 3 轮 — P → V ( 打开 ) .** 计算四个取值 $\bar a = a(\zeta), \bar b = b(\zeta), \bar c = c(\zeta), \bar t = t(\zeta)$ , 各附取值证明 $\pi_a, \pi_b, \pi_c, \pi_t$ , 一并发送.

**终判 — V 本地 ( 不再通信 ) .** 两件事全过才接受.

1. 取值证明都对:

$$\mathsf{Check}(C_a, \zeta, \bar a, \pi_a) = \dots = \mathsf{Check}(C_t, \zeta, \bar t, \pi_t) = 1 .$$

2. 门恒等式在 $\zeta$ 处成立 ( 公开量 $q_\bullet(\zeta)$ 和 $Z_H(\zeta) = \zeta^n - 1$ 由验证者自行代入 ):

$$q_L(\zeta) \bar a + q_R(\zeta) \bar b + q_M(\zeta) \bar a \bar b + q_O(\zeta) \bar c + q_C(\zeta) \ \overset{?}{=}\ (\zeta^n - 1) \bar t .$$

**可靠性.** 若轨迹非法, 则 $Z_H \nmid G$ , 对任何 $t$ 都有 $P = G - Z_H t \neq 0$ , 次数不超过系统上界 $d$ , 故 $\Pr_\zeta [ P(\zeta) = 0 ] \le d / |\mathbb{F}|$ , 可忽略. 第 1 轮先承诺保证了作弊者不能看到 $\zeta$ 再凑多项式.

**非交互化.** 删掉第 2 轮, 改令 $\zeta = \mathsf{Hash}(C_a, C_b, C_c, C_t)$ ( Fiat-Shamir ) , 协议变成单向发一个证明.



## 6. 这版省略了什么

上面的朴素协议只是骨架, 真实系统还要在它之上叠加三样东西, 都不改变轮次结构.

1. **连线约束.** 门恒等式只逐行甚至逐格独立检查, 并不知道 "第 1 行的 $c$ 必须等于第 2 行的 $a$" 这类跨格相等关系. 这些电路连线由另一条多项式恒等式 ( 置换论证, grand product ) 单独保证.
2. **公共输入输出的绑定.** 需把输入那列等于 $x$, 输出等于 $35$ 这类边界条件单独钉住.
3. **零知识盲化.** 本版会泄露 $\bar a$ 等取值, 真正的零知识需要给多项式加随机盲化项.

---

## 附: 关键文献 ( Halo 2 递归这条线 )

- PLONK. Gabizon, Williamson, Ciobotaru. ePrint 2019 / 953. ( 算术化 )
- Bulletproofs / IPA. Bünz, Bootle, Boneh, Poelstra, Wuille, Maxwell. ePrint 2017 / 1066. ( 透明多项式承诺 )
- Halo: Recursive Proof Composition without a Trusted Setup. Bowe, Grigg, Hopwood. ePrint 2019 / 1021. ( 摊销验证的奠基思想 )
- Proof-Carrying Data from Accumulation Schemes. Bünz, Chiesa, Mishra, Spooner. ePrint 2020 / 499, TCC 2020. ( 把摊销严格化为 accumulation 原语 )
- Halo Infinite: Proof-Carrying Data from Additive Polynomial Commitments. Boneh, Drake, Fisch, Gabizon. CRYPTO 2021, ePrint 2020 / 1536. ( 推广到任意加性承诺 )
- 实现层文档: The Halo2 Book, The Orchard Book.

源码仓库: `zcash/halo2` ( 证明系统本体, IPA 版 ) , `zcash/orchard` ( Orchard 电路, 依赖 halo2_proofs ) , `privacy-scaling-explorations/halo2` ( KZG 版分支 ) .

