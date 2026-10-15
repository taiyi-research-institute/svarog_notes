LATEXMK ?= latexmk

.PHONY: all clean

all: main.pdf

main.pdf: main.tex preamble.tex
	$(LATEXMK) -xelatex -interaction=nonstopmode -halt-on-error main.tex

clean:
	$(LATEXMK) -C main.tex

