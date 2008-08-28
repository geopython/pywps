FILE=pywps-howto
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
	latex2html -local_icons -split 0 ${SRC}
	mv ${FILE} html

txt: ${SRC} html/${FILE}.html
	links2 -dump html/${FILE}.html > ${FILE}.txt

process:
	${SRC}
	cd ../pywps/Wps/
	pydoc -w ./process.py
	mv process.html ../../doc
	cd -

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
