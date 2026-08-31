# ============================================================
#  DKLS23 笔记编译 (Makefile)
#
#  用法 (在仓库根目录):
#    make                 # 全量编译 15 篇
#    make pdf/06-rvole.pdf    # 只编译一篇 (也可写 make 06-rvole)
#    make clean           # 删掉 pdf/ 和 _build/ (编译现场)
#
#  产物: pdf/<stem>.pdf (PDF 只进 pdf/; 编译现场在 _build/: 包装文件+aux/log)
#
#  增量语义: 每篇 pdf 依赖全部 15 个片段 —— 任意片段改动都会触发全量重编。
#  这是故意的: 任何一篇的编号都可能被别的篇引用, 全量重编保证交叉引用新鲜。
#  单篇编译只重建那一篇, 引用其它笔记时用的是 _build/ 里现有 aux (可能旧)。
# ============================================================

STEMS = 00-mta-baseot 01-iknp03 02-kos15 03-endemic-ot 04-pprf \
        05-softspoken 06-rvole 07-orchestration dkls23 \
        misc-f2k misc-fiat-shamir misc-gadget misc-rerand temp \
        uc-framework

FRAGMENTS = $(addsuffix .tex,$(STEMS))      # 根目录的笔记片段
WRAPPERS  = $(addprefix _build/,$(addsuffix .tex,$(STEMS)))   # 中间产物 (由 main.tex 生成)
PDFS      = $(addprefix pdf/,$(addsuffix .pdf,$(STEMS)))

# 包装文件是中间产物, 默认会被 make 在运行结束时删掉 (导致每次都全量重编)。
# 标记为 precious: 保留 (无改动时 make 是 no-op), 缺失时仍会重建。
.PRECIOUS: $(WRAPPERS)

.PHONY: all clean

all: $(PDFS)

# make 06-rvole 快捷方式
$(STEMS): %: pdf/%.pdf

# 任意片段改动 → 全量重编
# 在 _build/ 里编译 (aux/log 落在现场, 交叉引用从这读 aux), 产物 PDF mv 到 pdf/
pdf/%.pdf: _build/%.tex $(FRAGMENTS)
	@mkdir -p pdf && cd _build && \
	xelatex -interaction=nonstopmode -halt-on-error $*.tex >/dev/null 2>&1 \
	  && mv $*.pdf ../pdf/ \
	  && xelatex -interaction=nonstopmode -halt-on-error $*.tex >/dev/null 2>&1 \
	  && mv $*.pdf ../pdf/ \
	  || { echo "!! $*: 编译失败, 看 _build/$*.log:" >&2; tail -25 $*.log >&2; exit 1; }; \
	pages=$$(sed -n 's/.*Output written on .* (\([0-9]*\) page.*/\1/p' $*.log | head -1); \
	labels=$$(grep -c 'newlabel' $*.aux || true); \
	echo "ok  $*: $$pages 页, $$labels 个标签"

# 包装文件 = main.tex 改 \input 行 (指向片段) + 注入该片段的标题 (wrap.py 从 "% title:" 注释提取)
_build/%.tex: main.tex template/wrap.py %.tex
	@mkdir -p _build
	python3 template/wrap.py $* > $@

clean:
	rm -rf _build pdf
