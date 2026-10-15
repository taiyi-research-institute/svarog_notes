# Saber Matrix DKLS23 实施笔记

本文档独立记录「Saber Base OT＋MatrixChecked 扩展＋DKLS23 RVOLE／ECDSA」路线，
不并入 `~/svarog_notes/dkls23`。版式复用后者的 `ruledprotocol.sty`，正文与构建产物留在本目录。

```bash
make
```

正文把六轮 `MatrixChecked` 作为标准实施路径，把五轮 confirmation 合包明确标为实验排程。
五轮接口的功能测试与冷启动测量已经完成，但交错调度的组合安全证明仍待补齐。
