本文描述零知识证明里一些形而上的概念.

-----

存在性命题有着这样的基本结构: 存在 $w$, 使得子命题 $\phi(x;w)$ 为真. 这里的 $w$ 称为 "见证" (witness), $x$ 称为 "实例" (instance).

"关系" $\mathcal{R}$ 是所有使子命题 $\phi(x;w)$ 为真的 $(w, x)$ 的集合. 形式化表述为
$$
\mathcal{R}=\left\{
(x,w) \mid \phi(x;w)
\right\}.
$$
💡 关系体现子命题的结构. 关系把见证和实例都视为命题的自由变量.

"语言" $\mathcal{L}$ 是所有使主命题 $\exists \,w,\;\phi(x;w)$ 为真的 $x$ 的集合. 形式化表述为
$$
\mathcal{L}=\left\{
x\mid \exists \,w,\;\phi(x;w)
\right\}.
$$
💡 语言体现主命题的结构. 语言把实例视为命题的自由变量.



关系是 NP 关系, 当:

1. (见证短) 见证的长度是实例长度的多项式量级, 即 $|w| \le \mathrm{poly}(|x|)$.
2. (验证快) 存在多项式时间的算法, 判断 $\phi(x;w)$ 是否成立.

NP 语言是定义在 NP 关系上的语言. 



PPT = 概率多项式时间. 定义: 一个随机化算法, 无论随机决策怎么摇, 都在多项式步数内停机. PPT 是密码学里的 "高效参与方/高效对手" 的标准形式化.

* Verifer 是 PPT. 意味着验证者必须高效, 否则协议没有实用价值.
* Simulator 是 PPT. 意味着他必须高效地编造视图. 如果放松要求, 允许他采用指数时间的算法去暴力解算, 模拟就变得平凡, 失去了意义.



我们假设一个交互协议, 有 $\mathcal{P}$ (Prover) 和 $\mathcal{V}$ (Verifier) 两方, 见证一个关系 $\mathcal{R}$. 该协议是零知识证明系统, 当且仅当以下三个条件同时成立:

(1) 完备性 completeness

对所有 $(x, w)\in \mathcal{R}$, 有
$$
\mathrm{Pr}\big[
\left<\mathcal{P}(w),\mathcal{V}\right>(x)=1
\big]\ge
1-\mathrm{negl}(\lambda). \tag{comp}
$$
直觉: 真命题几乎一定能过关.

式中, 

* "$\left<P(w),V\right>(x)$" 的意思是 (诚实地) 执行一次交互协议.
* $x$ 是公共输入, 就是待证的命题, Prover 和 Verifier 都知道.
* $w$ 是 Prover 的隐私输入, 就是命题的见证.
* "$=1$" 协议的输出是验证者的判决, 结果只有 0 (False) 和 1 (True) 二选一.
* 函数 $\mathrm{negl}(\lambda)$ 是 neglegible 误差函数, 比任何 $1/\mathrm{poly}(\lambda)$ 都更快地趋于 0. $\lambda$ 是安全参数, 比如比特数等等.
* 整个公式在说: 诚实执行的情况下, 协议返回 True 的概率无限接近 1.

(2) 可靠性 soundness

对所有 $x\not\in L$ 和所有作弊 Prover $\mathcal{P}^*$, 有
$$
\Pr\big[\
\langle P^{*}, V \rangle ( x ) = 1 
\big] \le \mathrm{negl}(\lambda). \tag{sound}
$$
直觉: 假命题几乎不能过关.

按作弊方 $\mathcal{P}^*$ 的能力, 对协议进行分类:

* 如果允许 $\mathcal{P}^*$ 计算能力无界, 则称协议为 proof (统计可靠).
* 如果只允许 $\mathcal{P}^*$ 为 PPT, 则称协议为 argument (计算可靠). SNARK 属于此类.

(3) 零知识 zero-knowlege

对每一个 PPT 验证者 $\mathcal{V}^*$ (不论他是否恶意), 存在一个 PPT 模拟器 $\mathcal{S}$, 使下面两个分布族不可区分:
$$
\begin{aligned}
&\phantom{{}={}} \big\{
\mathrm{view}^{\mathcal{V}^{*}}_{\mathcal{P}(w)}(x,z)
\big\}_{(x, w) \in\mathcal{R};\,z} \\
&\approx \big\{
\mathcal{S}(x, z)
\big\}_{(x, w) \in \mathcal{R};\, z} .
\end{aligned}
\tag{zk}
$$
直觉: $\mathcal{S}$ 只拿到公共的 $x$ 与 $z$, 拿不到 $w$, 却要 (却能) 产出与真实视图无法区分的输出. 既然无 $w$ 也能编造出视图, 视图便不包含 $w$ 的任何可计算信息. 这就把 "$\mathcal{V}^*$ 什么都学不到" 给形式化了.

这个式子怎么读?

* view 那一坨. 是 $\mathcal{V}^*$ 在一次真实交互中看到的全部东西. 这包括: 他自己的输入, 他摇的随机数, 他从 $\mathcal{P}^*$ 收到的所有消息.
* 分布族是怎么回事? 后文专开一节说.
* $z$ 是对 $\mathcal{V}^*$ 所收集的旁路信息的建模. 后文专开一节说 $z$.



分布族是怎么回事?

给定 $x, w, z$ (也就是把他们仨当参数), 那么 $\mathrm{view}^{\mathcal{V}^{*}}_{\mathcal{P}(w)}(x,z)$ 是一个随机变量, 其分布为 $\mathcal{P}, \mathcal{V}^*$ 内部的随机数所诱导. 类似地, $\mathcal{S}(x, z)$ 也是一个随机变量, 其分布为 $\mathcal{S}$ 内部的随机数所诱导.

两个确定的分布, 其统计距离也是确定的, 谈不上 “随参数增大而可忽略”. 但是, 我们要建模的是**两类**分布随着参数越来越大所表现出的渐进 (asymptotic) 性质, 所以我们要收集所有参数下的分布, 这就引入了分布族的概念.

插一句, “确定的 (随机) 分布” 这句话看起来又确定又随机, 显得荒谬, 但实际上是合理的. 从分布里采集的样本是随机的, 但分布本身是确定的.



$z$ 到底干什么用?

引入 $z$ 为了建模 $\mathcal{V}^*$ 收集的种种旁路信息. 这种收集行为往往有着不利于 $\mathcal{P}$ 的目的.

Goldreich–Oren 的经典结果是: 不带辅助输入的朴素零知识,在顺序组合下不封闭. 通俗地讲, 把一个看似零知识的协议连续跑多次, 合起来可能就不再零知识.

举个例子: 一个恶意 $\mathcal{V}^*$ 与同一个诚实 $\mathcal{P}$ 多次执行同一个交互协议, 这个恶意 $\mathcal{V}^*$ 可以把前几次执行攒下的状态带进当前执行, 从而降低破译 $w$ 的难度. 例如 GG18 多次签名泄露私钥分片, 就是一种 Verifier 攒状态的攻击手法. 详见 `CVE-2023-33241`.

再举个玩具协议的例子: 假设有一个离散对数困难的生成元 $G$. 协议提供一个公共设置: $Y=yG$,  其中 $y$ 是协议参与方不知道的秘密值, 称为陷门.

交互 **$\langle \mathcal{P}(w),\, \mathcal{V} \rangle(x)$**

1. $\mathcal{V} \to \mathcal{P}$: 发送标量 $\alpha$. 
2. $\mathcal{P}$ 验证 $\alpha G \stackrel{?}{=} Y$ (即 $\alpha$ 是否为陷门 $y$):
   1. **是** $\Rightarrow$ $\mathcal{P} \to \mathcal{V}$: 泄露见证 $w$. (病态分支)
   2. **否** $\Rightarrow$ $\mathcal{P}$ 与 $\mathcal{V}$ 正常跑一个可靠的 ZK 子证明证 $x$, 不泄露 $w$.

**完备性 (completeness)** 诚实的 $\mathcal{V}$ 不知道 $y$, 以压倒概率有 $\alpha \ne y$, 必走 "否" 分支. 公式 (comp) 成立.

**朴素零知识成立 (无辅助输入 $z$)** PPT 的 $\mathcal{V}^*$ 要触发泄露, 需自造 $\alpha$ 使 $\alpha G = Y$, 即求 $Y$ 的离散对数 $\Rightarrow$ 困难. 故泄露分支几乎不可达, 模拟器 $\mathcal{S}(x)$ 只需模拟子证明, 两族分布不可区分. 公式 (zk) 成立.

**辅助输入零知识失败 (取 $z = y$)** 将陷门作为辅助输入喂给 $\mathcal{V}^*$, 即令 $z = y$:

- $\mathcal{V}^*$ 发 $\alpha = y$, 满足 $\alpha G = Y$, $\mathcal{P}$ 交出 $w$; 
- 真实视图**含** $w$, 而 $\mathcal{S}(x, z) = \mathcal{S}(x, y)$ **无** $w$, 且 $x$ 不决定 $w$, 造不出含有效见证的视图.

区分器 $\mathcal{D}(x, z, \cdot)$ 只需检验所揭值 $w'$ 是否满足 $(x, w') \in \mathcal{R}$ ($\mathcal{R}$ 可验, 故 $\mathcal{D}$ 高效), 即以压倒优势区分两族. 公式 (zk) 不成立.
