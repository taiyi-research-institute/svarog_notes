dkls23 论文: 
```
https://eprint.iacr.org/2023/765.pdf
```

开源实现:
```
https://github.com/silence-laboratories/dkls23
```

看 MPC ECDSA 算法, 要抓的关键就是: 签名阶段怎么做 MtA(乘转加).

DKLs23 采用 位分解+OT 的路数来做 MtA. 比起以 GG18 为代表的同态加密, 如果做好预处理和批量化, 速度会快很多. 批量化是可以拍脑袋想出来的, 但预处理需要智慧和技巧.

路线图:
* [base-ot-mta.md](./base-ot-mta.md) 如果不熟悉什么是 位分解+OT, 读这篇笔记以建立基础认知.
* [extended-ot.md](./extended-ot.md) 论文 iknp03 介绍了 OT 预处理的基本思路. 它并不是 ecdsa3round 中的预处理方法. 但读这篇笔记可以建立 OT 预处理相关的基础认知. 对于 MPC ECDSA, 总的来说, OT 预处理能够把 OT 密钥协商的一部分工作提前到 Keygen 阶段, 从而降低 Sign 阶段中 OT 的均摊成本.