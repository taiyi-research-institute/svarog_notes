

从运算到零知识证明: PLONK 式证明系统的代数基础

本文讲一个运算如何被改写成多项式约束, 这些约束如何被一个简短的协议验证.



全景: 五步流水线

零知识证明要证的是:

```
存在某秘密输入, 在某公开算法下得到某公开输出.
```

分为五步:

1. 把运算拆成只含加法和乘法的基本门, 得到一个算术电路.
2. 运算 "执行过一遍" 等价于填好一张表 (每根线一个域元素) , 且每一行都满足门规则.
3. 把表的每一列插值成一条多项式.
4. "每行门都成立" 于是变成 "某条多项式在一组点上全为零", 而这又等价于 "它能被一个固定多项式整除". $N$ 条约束坍缩成 $1$ 条多项式恒等式.
5. 验证者只在一个随机点抽查这条恒等式, 并用多项式承诺让 "在某点取值" 既简洁又防赖账.

后文逐一展开.

---

-----

多项式约束从哪来? 

假如我要证明 "我知道一个 $x$, 使得 $x^3 + x + 5 = 35$", 答案是 $x = 3$, 但不想把 $x$ 直接告诉验证者. 那么我需要遵守以下五步协议.

## Step 1. 把运算转化为电路

在有限域 $\mathbb{F}_p$ 上, 任何运算都能拆成由加门和乘门组成的程序 / 电路. 上面的式子拆开是:

```
v1  = x  * x      (= 9)
v2  = v1 * x      (= 27)
v3  = v2 + x      (= 30)
out = v3 + 5      (= 35)
```

每一行是一个门. 一个门只有三路数据访问: 左输入 $a$, 右输入 $b$, 输出 $c$.

## Step 2. 执行电路, 把输入 & 输出 & 参数收集到一张表

把每个门编排成表格的一行. 再把所有门代入到如下关于 $a, b, c$ 的方程:
$$
q_L \cdot a + q_R \cdot b + q_M \cdot (a b) + q_O \cdot c + q_C = 0 .
$$
其中,

* 乘门参数为 $q_M = 1$, $q_O = -1$, 对应方程 $a b - c = 0$;
* 加门设 $q_L = q_R = 1$, $q_O = -1$, 对应方程 $a + b - c = 0$.

代入 $x = 3$ 得到这张轨迹表:

| 行 | 类型 | 左输入 $a$ | 右输入 $b$ | 输出 $c$ | 门参数 $q_\_$ `*` |
|:-:|---|:-:|:-:|:-:|:-:|
| 1 | 乘门 | 3 | 3 | 9 | 0,0,1,-1,0 |
| 2 | 乘门 | 9 | 3 | 27 | 0,0,1,-1,0 |
| 3 | 加门 | 27 | 3 | 30 |    1,1,0,-1,0     |
| 4 | 加门 | 30 | 5 | 35 | 1,1,0,-1,0 |

`*` 门参数的顺序为 LRMOC. 门参数是 setup / 硬编码结果.

到这里, 待证命题严格等价于:

```
存在这样一张表, 每行都满足门方程, 且输入那列等于 $x$, 输出那行等于 35.
```

证明者知道整张表, 这就是 "见证" witness. 注意到这一步全是代数等式, 还没有多项式.

## Step 3. 把每一列插值成多项式

选一组求值点 $\Omega = \{ \omega^0, \omega^1, \omega^2, \omega^3 \}$, 通常取单位根. 对每一列, 找那条唯一穿过这些点的 & 次数最低的多项式. 例如对于输出列 $c$, 就求解次数最低的 $c(X)$, 使得
$$
c(\omega^0) = 9, \quad c(\omega^1) = 27, \quad c(\omega^2) = 30, \quad c(\omega^3) = 35 .
$$
类似地, 求 $a(X)$, $b(X)$, $q_{\_}(x)$, $\dots$ 现在所有东西都是多项式了.

## Step 4. 把所有列压缩成一条恒等式

如节标题, 得到如下多项式:
$$
\begin{aligned}
G(X) &= q_L(X) a(X) \\
& + q_R(X) b(X) \\
& + q_M(X) a(X) b(X) \\
& + q_O(X) c(X) \\
& + q_C(X) .
\end{aligned}
$$
对 $\omega^i\in\Omega$, "表格第 $i$ 行成立" 形式化表达为 $G(\omega^i)=0$. 进而, "表格每一行都成立", 意味着 $G(X)$ 在 $\Omega$ 的每一个元素上都取零. 如此, 必然存在商多项式 $t(X)$, 使得
$$
\begin{aligned}
G(X) &= \prod_{i=0}^{n-1} (X-\omega^i)\cdot t(X) \\
&= (X^n-1)\cdot t(X).
\end{aligned}
$$


## 附: 这版省略了什么

上面的朴素协议只是骨架, 真实系统还要在它之上叠加三样东西:

1. **连线约束.** 门恒等式只逐行甚至逐格独立检查, 并不知道 "第 1 行的 $c$ 必须等于第 2 行的 $a$" 这类跨格相等关系. 这些电路连线由另一条名为 "置换论证" 的多项式方程单独保证.
2. **公共输入输出的绑定.** 需把输入那列等于 $x$, 输出等于 $35$ 这类边界条件单独钉住.
3. **零知识盲化.** 本版会泄露 $\bar a$ 等取值, 真正的零知识需要给多项式加随机盲化项.

## 附: 关键文献 (Halo 2 递归这条线)

- PLONK. Gabizon, Williamson, Ciobotaru. ePrint 2019 / 953. ( 算术化 )
- Bulletproofs / IPA. Bünz, Bootle, Boneh, Poelstra, Wuille, Maxwell. ePrint 2017 / 1066. ( 透明多项式承诺 )
- Halo: Recursive Proof Composition without a Trusted Setup. Bowe, Grigg, Hopwood. ePrint 2019 / 1021. ( 摊销验证的奠基思想 )
- Proof-Carrying Data from Accumulation Schemes. Bünz, Chiesa, Mishra, Spooner. ePrint 2020 / 499, TCC 2020. ( 把摊销严格化为 accumulation 原语 )
- Halo Infinite: Proof-Carrying Data from Additive Polynomial Commitments. Boneh, Drake, Fisch, Gabizon. CRYPTO 2021, ePrint 2020 / 1536. ( 推广到任意加性承诺 )
- 实现层文档: The Halo2 Book, The Orchard Book.

源码仓库: `zcash/halo2` ( 证明系统本体, IPA 版 ) , `zcash/orchard` ( Orchard 电路, 依赖 halo2_proofs ) , `privacy-scaling-explorations/halo2` ( KZG 版分支 ) .

