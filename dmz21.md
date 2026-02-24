# DMZ21 / CL15 所需的虚二次类群知识路线

这份笔记把 `materials/` 目录里的碎片内容，串成一条从「二元二次型」到「虚二次整环的理想类群」，再到「CL15 的类群 ElGamal 与 DMZ21 的承诺/证明协议」的主线。目标是：你能顺着一条线把符号、对象、算法接口和安全动机对上。

阅读路线（由浅入深）：

1. 二元二次型与判别式：对象是什么、怎么等价、怎么规约。
2. 虚二次整环（quadratic order）：从判别式定义出整环，理想是什么。
3. 二次型/理想/格之间对应：为什么可以用二次型代表理想类。
4. 类群与计算接口：规约、复合（乘法）、类数。
5. CL15：在非最大整环上构造一个“明文子群”（阶为 p），并让它的 DL 可解。
6. DMZ21：为什么朴素 Sigma 证明会被“低阶元素/子群混淆”攻击；Promise Sigma 如何把“密文是合法的 ElGamal 密文”也纳入证明。

---

## 0. 贯穿全文的对象与符号

- 二元二次型（binary quadratic form）：`f=(a,b,c)` 表示
  \[
  f(x,y)=ax^2+bxy+cy^2.
  \]
- 判别式（discriminant）：\(\Delta(f)=b^2-4ac\)。
- 虚二次（imaginary quadratic）场/整环：通常关注 \(\Delta<0\) 的情形（对应正定二次型、有限类群、便于密码学）。
- 二次整环 \(\mathcal O_\Delta\)：由一个“判别式” \(\Delta\equiv 0,1\pmod 4\)（且非平方）确定。
- 理想类群：\(\mathrm{CL}(\mathcal O_\Delta)=\mathcal I_\Delta/\mathcal P_\Delta\)，其中 \(\mathcal I_\Delta\) 为可逆理想群，\(\mathcal P_\Delta\) 为主理想群。
- 约定：本文中“理想/二次型的乘法”指理想乘法（或等价的 Gauss/Cohen 复合），然后再规约到标准代表。

---

## 1. 二元二次型：定义、判别式、正定性

### 1.1 定义与矩阵表示

二元二次型 `f=(a,b,c)` 可写为矩阵二次型：

\[
f(x,y)=\begin{bmatrix}x&y\end{bmatrix}
\begin{bmatrix}
a & b/2\\ b/2 & c
\end{bmatrix}
\begin{bmatrix}x\\y\end{bmatrix}.
\]

并且 \(\Delta(f)=-4\det(M_f)\)。这使得“正定/负定”可以用线性代数的正定矩阵刻画。

### 1.2 正定（虚二次的入口）

对于整系数二元二次型 `f=(a,b,c)`：当且仅当

- \(\Delta<0\) 且 \(a>0\)

时，`f` 为正定（positive definite）。在虚二次场/虚二次整环里，正定二次型对应的等价类集合是有限的，进而类群是有限交换群，这是密码学可用的关键。

---

## 2. 等价关系：SL(2,Z) 作用与“规约”

### 2.1 正规等价（proper equivalence）

令 \(U\in\mathrm{SL}(2,\mathbb Z)\)。把坐标作代换

\[
U(x,y)=(sx+ty,ux+vy),\quad U=\begin{bmatrix}s&u\\t&v\end{bmatrix}
\]

定义

\[
f\,U(x,y)=(\det U)\cdot f(U(x,y)).
\]

当 \(U\in\mathrm{SL}(2,\mathbb Z)\) 时 \(\det U=1\)，于是 `fU` 与 `f` 处在同一个“正规等价类”（proper equivalence class）。

### 2.2 primitive / reducible

- primitive（二次型本原）：\(\gcd(a,b,c)=1\)。
- reducible（可约）：当且仅当判别式 \(\Delta\) 为整数平方；等价地，存在非平凡整数解 \((x,y)\neq(0,0)\) 使 \(f(x,y)=0\)。

在虚二次场（\(\Delta<0\)）里，非零正定形式不会取到 0，因此关注的通常是不可约（irrational）情形。

### 2.3 规约（reduction）

规约把一个等价类里的无穷多个代表，选出一个“大小受控”的标准代表。典型定义（正定情形）是：

`f=(a,b,c)` reduced 若满足

- \(-a<b\le a < c\)，或
- \(0\le b\le a=c\)。

关键事实：每个正规等价类中恰有一个 reduced form（唯一性），因此可以用“规约后的代表”当作等价类的 canonical 表示。

实现上常见的两步：

- `normalize`: 通过 \(T^s\) 把 \(b\) 拉回到 \((-a,a]\) 附近；
- `rho`（reduction step）: 用一个特定的 \(U\) 交换并缩小系数，重复直到 reduced。

---

## 3. 从判别式到虚二次整环：\(\mathcal O_\Delta\)

### 3.1 “判别式”与“基本判别式”

这里的判别式 \(\Delta\) 是一个满足 \(\Delta\equiv 0,1\pmod 4\) 的非零整数。

- conductor：最大的正整数 \(f\)，使得 \(\Delta/f^2\) 仍是判别式。
- fundamental discriminant：conductor 为 1 的判别式。

直觉：fundamental discriminant 对应“最大整环”（maximal order）；非 fundamental 则对应“非最大整环”（子整环）。

### 3.2 二次域与代数整数（和 \(d\equiv 1\pmod 4\) 的分支）

二次域 \(F=\mathbb Q(\sqrt d)\)（\(d\) 通常取平方自由）。其整数环（最大整环）为

\[
\mathcal O_F=
\begin{cases}
\mathbb Z\left[\frac{1+\sqrt d}{2}\right], & d\equiv 1\pmod 4,\\
\mathbb Z[\sqrt d], & d\equiv 2,3\pmod 4.
\end{cases}
\]

这解释了为什么很多公式里会出现 \((b+\sqrt\Delta)/2\)：当判别式为 1 mod 4 时，整基的自然写法就带一个 1/2。

### 3.3 Quadratic order（与 \(\Delta\) 对应的整环）

固定判别式 \(\Delta\) 后，可构造一个二次整环 \(\mathcal O_\Delta\subset \mathbb Q(\sqrt\Delta)\)。它是一个秩为 2 的 \(\mathbb Z\)-格，同时又是带 1 的子环。

---

## 4. 理想、可逆理想与类群

### 4.1 理想的基本定义

在交换环里，理想 \(\mathfrak a\subset \mathcal O\) 是一个加法子群，并满足对任意 \(r\in\mathcal O\) 与 \(x\in\mathfrak a\) 有 \(rx\in\mathfrak a\)。

理想可以加、可以乘：

- \(\mathfrak a+\mathfrak b=\{a+b\}\)
- \(\mathfrak a\mathfrak b\) 为所有有限和 \(\sum a_i b_i\) 的集合。

### 4.2 分式理想、主理想、可逆性

- 分式理想：\(\mathfrak b\subset F\) 且存在整数 \(d>0\) 使 \(d\mathfrak b\subset \mathcal O\) 为（整）理想。
- 主理想：\(\alpha\mathcal O\)。
- 可逆理想：\(\mathfrak a\mathfrak a^{-1}=\mathcal O\)。在二次整环里，可逆理想正好对应 primitive 形式（在适当对应下）。

### 4.3 类群

\[
\mathrm{CL}(\mathcal O_\Delta)=\mathcal I_\Delta/\mathcal P_\Delta.
\]

在 \(\Delta<0\) 时，这个群是有限交换群；其大小是类数 \(h(\Delta)\)。

---

## 5. 二次型、格、理想之间的对应（为什么“可以用二次型算类群”）

一个核心事实（在很多教材里以“形式/理想对应”出现）：

- 固定 \(\Delta\)，primitive 的整二次型的正规等价类，与 \(\mathcal O_\Delta\) 的可逆理想类之间存在自然的双射。

常用的理想表示（与 CL15/DMZ21 代码习惯一致）是：

\[
\mathfrak a = a\mathbb Z + \frac{-b+\sqrt\Delta}{2}\mathbb Z.
\]

这常简写为 `(a,b)`。其中 `a>0`，并且存在整数 `c` 使 \(\Delta=b^2-4ac\)。

把这看成：二次型 `(a,b,c)` 与理想 `(a,b)` 共享同一个判别式 \(\Delta\)，并且“等价/乘法/规约”等运算可在二次型表示与理想表示之间互译。

---

## 6. 计算接口：规约与复合（乘法）

### 6.1 规约（Reduce）

在实现里通常提供 `Reduce`：

1. 给定一个理想或二次型代表；
2. 通过等价变换把它变成 reduced 代表；
3. reduced 代表作为该类的 canonical 表示。

在密码学协议里，这一步的意义是：让“群元素”有一个稳定、短小、可比较的编码。

### 6.2 复合（Composition / Ideal multiplication）

理想类群的群运算是理想乘法再取类（再规约）。

在 `materials/二次型的复合.md` 里整理了 Cohen 的一个关键引理（Lemma 5.4.5）：

- 两个理想 \(I_1, I_2\)（或对应的二次型/参数）相乘，可以写回同样形状的 \(A\mathbb Z + \frac{-B+\sqrt\Delta}{2}\mathbb Z\)。
- 系数 \(A,B\) 的计算涉及若干 gcd 与 Bezout 系数（扩展欧几里得）。

同一文件里也解释了为什么某些实现里会出现“对一个中间量取模”（比如 mod \(v_1\)）：这是利用 Bezout 解的周期性做数值缩小，不会破坏数学约束，反而能加速。

另外：NUCOMP（Cohen Algorithm 5.4.9）是更快的复合/规约变体，常用于大判别式下的高性能实现。

---

## 7. CL15：从类群里做一个“线性同态”的 ElGamal

CL15 的关键结构是：在某个虚二次整环的类群中，构造一个阶为 \(p\) 的子群用来承载明文，并且让这个子群上的离散对数“刻意变简单”，同时让“用于随机性/加密遮蔽”的那部分仍然保持 DL 困难。

### 7.1 判别式与两个整环

CL15 常用的设定是：

- 先选一个 fundamental discriminant \(k\)（常取 \(k\equiv 1\pmod 4\)，并写成 \(k=-pq\) 形状以控制 2-Sylow）。
- 构造非最大整环 \(\mathcal O_{kp^2}\) 与最大整环 \(\mathcal O_k\) 之间的自然映射（通过“扩张/收缩理想”实现）。

你在 `materials/CL15.md` 里已经把三个映射接口梳理成了可实现的算法：

- \(\bar\varphi_p: C(\mathcal O_{kp^2})\to C(\mathcal O_k)\)（先找与 \(p\) 互素的代表理想，再扩张）。
- \(\varphi_p\) 与 \(\varphi_p^{-1}\)：在 `(a,b)` 表示上对参数做可计算的变换。

### 7.2 明文子群 \(\langle f\rangle\)（阶为 p）与“容易的 DL”

CL15 里一个非常关键（也容易让人误解）的点：

- 他们构造了一个理想类 \(f=[\mathfrak t]\)（例如 \(\mathfrak t=(p^2,p)\)），它生成了 \(\bar\varphi_p\) 的核。
- 这个核的阶是 \(p\)。因此 \(\langle f\rangle\) 是一个阶为 \(p\) 的循环子群。
- 更强：对 \(f^m\) 做 `Reduce` 后会得到一个非常特殊的 reduced 代表（形如 `(p^2, m^{-1}p)`），因此在这个子群上求 DL 本身是“故意设计为容易”的。

这不是漏洞，而是“明文编码接口”：明文 \(m\in\mathbb Z_p\) 映射到 \(f^m\)，解密时需要把密文中的 \(h^r\) 消掉后，再把剩下的 \(f^m\) 读回 \(m\)。

### 7.3 为什么另一部分的 DL 仍然困难

加密需要随机扰动（类似经典 ElGamal 的 \(g^r\)、\(y^r\)）。CL15 的解释路径是：在选取判别式很大时，类数/群阶相关量难以计算；很多通用 DL 算法在这里的可行性受到限制。

你在 `materials/CL15.md` 里也记录了一个重要直觉：

- “明文子群 DL 容易”不等于“整体 DL 容易”。真正要破的是隐藏在 \(h^r\) 里的随机性/密钥部分。

---

## 8. DMZ21：为什么需要 Promise Sigma Protocol

`materials/DMZ21-Notes.md` 的主线在于：如果你在“不是严格素阶/不是单一循环群”的群里，直接套用传统 Sigma 协议去证明“我知道 \((r,m)\) 使得 \(c_1=g^r, c_2=h^r f^m\)”，会遇到一个典型问题：证明者可以提交一个“形式上能过等式检查，但并非合法 ElGamal 密文”的对象。

### 8.1 朴素 Sigma 的问题：低阶元素/子群混淆

朴素的等式检查依赖同态：

- \(g^{z_r}=a_1c_1^e\)
- \(h^{z_r}f^{z_m}=a_2c_2^e\)

如果证明者用一个“低阶元素” \(g'\) 去扭曲密文（例如把 \(c_1,c_2\) 同时乘上 \(g'\)），并且碰巧 \((g')^e=1\)，那么验证等式里会把这部分消掉，导致验证通过。

本质问题不是“等式推导错了”，而是：

- 通过等式检查的 \((c_1',c_2')\) 并不一定存在 \(r',m'\) 使得它真的是 \(c_1'=g^{r'}\)、\(c_2'=h^{r'}f^{m'}\)。

也就是说，验证者被说服的是“关于一个畸形密文的知识”，而不是“关于合法密文的知识”。

### 8.2 Promise Sigma 的思路

Promise Sigma 协议把“对象属于正确子群/满足正确结构（例如确实是某个同态加密输出）”也变成要证明的一部分。

在 DMZ21 的应用中，你同时有两条加密通道（例如 EC ElGamal 与 CL ElGamal），并要证明它们承载的是同一个明文（consistency of plaintexts）。协议会让验证者只看到一个与明文相关的响应量（例如一个 \(z_m\)），从而避免“两个通道用不同明文但各自过检”的可能。

---

## 9. 你现有材料里线索断点/可能错误

这部分按“会影响理解/实现”的优先级列：

1. `materials/虚二次笔记.md` 第 1 段把二元二次型定义成满足 `abc != 0`，这过强：二次型通常只要求 `(a,b,c)` 不全为 0；允许某个系数为 0（例如 `b=0` 很常见）。如果后续推导默认允许 `b=0`，那这里的 `abc != 0` 应改成“不是全 0”。
2. `materials/虚二次笔记.md` 里 `Algorithm 5.5` 的伪代码写了 `b ^ 2`，在很多语言里 `^` 是按位异或而不是乘方；这里应理解为 \(b^2\)。
3. `materials/CL Notes.md` 对“理想”的定义写成同时要求 `xy` 与 `yx` 落在理想里；在交换环这两条等价，不影响，但更标准的写法是“对任意 `r in R`，`a in I`，有 `ra in I`”（非交换环再补 `ar in I`）。
4. `materials/DMZ21-Notes.md` 里举的“朴素 Sigma 会被低阶元素攻击”这一段，逻辑上需要的条件是 `(g')^e=1`（例如 `ord(g') | e`），否则等式不会对所有挑战成立。你写的“order divides e”是足够条件，但建议在最终表述里明确依赖的是 `(g')^e` 这一项是否消掉。

---

## 10. 这条线如何落到实现（最小接口清单）

如果你是为了读源码/复现协议，建议把“类群当作黑盒群”所需接口收敛到：

- 表示：群元素的 canonical 编码（通常就是 reduced 代表，如 `(a,b)` 或 `(a,b,c)`）。
- 运算：`Mul`（复合/理想乘法）、`Inv`、`Pow`。
- 规约：`Reduce`（乘法后规约、或任意代表规约）。
- 辅助：判别式/互素性判定、Kronecker 符号、模平方根（Tonelli-Shanks）等，用于 CL15 的参数生成。

以上这些接口在你现有材料中都出现了：

- 规约与类数枚举：`materials/虚二次笔记.md`
- 复合与实现细节：`materials/二次型的复合.md`
- \(\varphi_p\) 家族映射与明文子群：`materials/CL15.md`
- DMZ21 的 ZK/一致性证明动机：`materials/DMZ21-Notes.md`
