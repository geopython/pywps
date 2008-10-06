FILE=pywps-howto
SRC=${FILE}.tex
PDFLATEX=pdflatex
PROCESS=../pywps/Process

all: ${SRC}
	make pdf
	make html
	make txt
	make process

pdf: ${SRC}
	rm -f ${FILE}.pdf
	${PDFLATEX} ${SRC}

html: ${SRC}
	latex2html -local_icons -split 0 ${SRC}
	mv ${FILE} html

txt: ${SRC} html/${FILE}.html
	links2 -dump html/${FILE}.html > ${FILE}.txt

process: ${PROCESS}
	cd ${PROCESS} && pydoc -w ./Process.py && pydoc -w ./InAndOutputs.py && pydoc -w ./Lang.py && mv *.html ../../doc/

clean:
	rm -f *.aux *.log *.out *.nav *.snm *.toc *~ *.log *.bak all
veryclean:
	make clean
	rm -f *.pdf *.ps ${FILE}.txt ${FILE}.html

help:
	@echo all
	@echo pdf
	@echo txt
	@echo process
	@echo clean
	@echo veryclean
