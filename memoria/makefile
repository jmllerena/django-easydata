NOM = memoria
# Nombre del documento a compilar
DOC = $(NOM).tex
# Nombre del fichero que generará el glosario
GLOS = $(NOM).gls.aux

PDF = pdflatex
BIB = bibtex
LATEX = latex
DVI = dvipdf

# Por defecto se ejecuta la primera orden
# Compila usando BibTeX para las referencias bibliográficas y el
# glosario y luego vuelve a compilar para generar índices y referencias
pdf-bib: 
	$(PDF) $(DOC) && $(BIB) $(NOM) && $(BIB) $(GLOS) | make pdf

pdf:
	$(PDF) $(DOC) && $(PDF) $(DOC)

latex-bib: 
	$(LATEX) $(DOC) && $(BIB) $(NOM) | make latex

latex: 
	$(LATEX) $(DOC) && $(LATEX) $(DOC)

dvi-pdf: 
	$(DVI) $(NOM).tex

clean: 
	$(RM) *.aux *.toc *.log \
	*.lof *.lot *.out *.bbl \
	*.blg *~ *\#
	$(RM) -r auto

clean-all:
	make clean
	$(RM) $(NOM).pdf $(NOM).dvi
