哑约束为什么无法被同态消掉 ?

## 场景

混币池取款证明里, 要把收款地址 `recipient` 绑进证明 $\pi$, 以防抢跑者在 mempool 里截获交易, 把 `recipient` 改成自己的地址再提交. 做法是把 `recipient` 声明为电路的**公开输入**, 并补一条**哑约束**

$$
\text{recipientSquare} = \text{recipient} \cdot \text{recipient}
$$

把这根线拉进约束系统. 这条式子从不被别处使用, 平方也不限制取值 (任何地址平方都合法) , 它唯一的作用是让 `recipient` 这根线真实存在.

## 疑虑

这条哑约束和 $\mathrm{Hash}(k,r)$, $\mathrm{Hash}(k)$ 之间, 在电路数据流图上**毫无连线**, 是孤立的一块. 既然证明前它和别的约束没关系, 会不会存在某种同态, 让人在证明**之后**把 `recipient` 相关的部分平凡地剥离或替换, 从而把绑定架空?

**结论先行:** 加同态存在, 但被 witness 门控; 乘同态在群里根本不存在. 安全根基是 **witness 门 + Fiat-Shamir 挑战绑定**, 而不是 "没有同态".

---

-----

## 一. Fiat-Shamir 安全性兜底

按 [ipa-main](./ipa-main.md) 第 2 节, 挑战是
$$
x_j = \mathrm{Hash}\big( \underbrace{C_f, \zeta, v, L_1, R_1, \dots}_{\text{transcript}} \big) .
$$

公开输入是 transcript 的一部分, 所以 recipient 在所有挑战 $x_j$ 的上游. 它不是悬在末端可摘掉的因子, 而是决定后面全部随机性的种子.

## 二. 论证加同态存在但不起作用

先承认事实: 承诺方案就是加同态的. [kzg-main](./kzg-main.md) 里承诺的定义

$$
C_f = [f(\tau)]_1 = \sum_i f_i [\tau^i]_1
$$

对 $f$ 线性, 于是 $C_f + C_g = C_{f+g}$. 我们赖以做批量打开 (用 $\nu$ 把 $a,b,c,t$ 合一) 、以及 [ipa-main](./ipa-main.md) 的 $P_0 = C_f + v\,U$ 和折叠里的全部线性组合, 靠的正是这个加同态. 加同态是良性工具, 不是漏洞.

那攻击者为什么用不了它来换 recipient? 两道坎:

### 坎1. 补偿承诺需要 witness 系数.

想把 $C_t$ 同态地挪成 $C_{t'}$, 得加上 $C_{\Delta t} = \sum_i (\Delta t)_i [\tau^i]_1$. 而 SRS 只让你承诺 "自己知道系数" 的多项式 ([kzg-main] Round 1.1) , 而 $\Delta t$ 的系数依赖 witness.

### 坎2. 补偿项根本不是多项式.

honest 的 $a,b,c$ 让 $\text{gate}(a,b,c) + \mathrm{PI}$ 在 $H$ 上处处归零, 所以能被 $Z_H$ 整除, $t$ 是真多项式. 你把 recipient 改成 recipient$'$, $\mathrm{PI}$ 变成 $\mathrm{PI}'$, 用**同一套** $a,b,c$ 会得到
$$
\text{gate}(a,b,c) + \mathrm{PI}' = \underbrace{\big(\text{gate}(a,b,c) + \mathrm{PI}\big)}_{= Z_H \cdot t} + \Delta\mathrm{PI} .
$$

而 $\Delta\mathrm{PI}$ 只在 recipient 那一行非零 (形如 $\Delta v \cdot L_{\text{row}}(X)$) , 不在整个 $H$ 上归零, 因此不被 $Z_H$ 整除. 于是合法的 $t'$ 根本不是多项式, 也就没有对应的承诺可加. 要修复, 你必须换一套在 $\mathrm{PI}'$ 下仍归零的 $a,b,c$ —— 也就是换 witness, 而 $C_a, C_b, C_c$ 在 $\zeta$ 出现前就已冻结, 要打开还得有 witness.

## 三. 论证乘同态不存在

攻击者真正想要的是把 recipient "因子" 乘进 / 除出 $\pi$, 这需要**两个群元素相乘**. 而 [kzg-main](./kzg-main.md) 的 "插叙 Pairing" 已经点明: 普通群运算只能加减和缩放, **无法计算两个群元素的乘积**.

Pairing 确实提供了**恰好一次**乘法

$$
e([a]_1, [b]_2) = e(g_1, g_2)^{ab} ,
$$

但:

- 结果落进 $\mathbb{G}_T$, 不能再配对, 用完即止;
- 它是给验证用的 ([kzg-main] 的 verify 式) , 不是留给攻击者的可复用原语.

所以没有任何可供攻击者反复利用的乘同态.
