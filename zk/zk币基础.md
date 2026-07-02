账本由两部分组成:

* 承诺树 (commitment, cm): 历史上产生的所有 note.
* 核销表 (nullifier, nf): 历史上核销的所有 note.

cm 是 note 的确定性承诺, 天然一对一.

nf 是给 note 另外绑定的编号, 由电路保证一对一.

## 例1. 固定面额池: Alice 给 Bob 转 10U.

假设链上有一个 10U 面额的混币合约.

(1) Alice 存款.

Alice 本地生成两个随机数: $k, r$. 其中 $k$ 是 nf 的原像. 算出 $C=\mathrm{Hash}(k,r)$. 

Alice 把 $C$ 发给合约, 把 10U 转给合约.

Alice 把 note 也就是 $(k, r)$ 发给 Bob.

(2) 合约处理存款.

合约收到 Alice 转账之后, 把 $C$ 放入 Merkle 树的下一个空叶子, 更新 Merkle 根. 

合约并不直接存储所有叶子, 这是为了节约 gas; 而是把叶子值 $C$ 和叶子索引发布为链上事件/日志. 

(3) Bob 取款.

重放 cm 和 nf. 算出 $h=\mathrm{Hash}(k)$, $C=\mathrm{Hash}(k,r)$.

重放 Merkle 树. 从链上拉取全部 Deposit 事件, 用于重建 Merkle 树. Bob 要从这个树知道:

* 值为 $C$ 的叶子下标 $i$, 
* 认证路径, 即叶子到根的每一层的兄弟哈希, 以及左右方向.
* 当前根 $R$.

💡 Bob 可以把链上拉取全部事件的工作量拆分出去. 比如, 让池子服务器完成大头工作, 或者他自己平时就保持同步.

⚠️Bob 一定不要在 RPC / Indexer 上面问 "这个 $C$ 在哪", 尤其不要在取款前夕问, 这就把存款方和取款方关联起来, 破坏匿名性. Bob 正确的做法是拉取叶子集合, 在本地查询 "$C$ 在哪".

生成 ZK 证明 $\pi$. 要证的命题是: 存在 $(k,r)$ 和一条 Merkle 路径, 使得 $\mathrm{Hash}(k,r)$ 是根为 $R$ 的 Merkle 树的叶子, 且 $h=\mathrm{Hash}(k)$.

⚠️ 为了避免别人 (Eva) 用 Bob 的证明和 Eva 的地址, 还需要在生成 ZK 证明时引入一条哑约束 `addrBobSquare = addrBob * addrBob`.

调用合约取款. 要传的参数是证明结构体 $\pi$ ; 以及证明时所用到的公开输入, 这里有 Merkle 根 $R$, 核销号 $h$, 收款地址 `addrBob`.

(4) 合约校验并放款.

合约验证 $\pi$ 对某个近期根 $R$ 成立, 且 $h$ 不在已核销集合里. 若通过, 则把 $h$ 记入已核销集合, 再向 `addrBob` 转出 10U.



