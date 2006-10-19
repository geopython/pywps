FILE=install
SRC=${FILE}.tex
PDFLATEX=pdflatex

all: ${SRC}
	make pdf
	make html
	make txt

pdf: ${SRC}
	rm -f ${FILE}.pdf
	${PDFLATEX} ${SRC}

html: ${SRC}
	latex2html -split 0 ${SRC}
	mv ${FILE}/index.html ${FILE}.html
	rm -rf ${FILE}

txt: ${SRC} ${FILE}.html
	pdftotext ${FILE}.pdf
	lynx -dump ${FILE}.html > ${FILE}.txt


clean:
	rm -f *.aux *.log *.out *.nav *.snm *.toc *~ *.log *.bak all
veryclean:
	make clean
	rm -f *.pdf *.ps ${FILE}.txt ${FILE}.html

help:
	@echo all
	@echo pdf
	@echo txt
	@echo clean
	@echo veryclean
