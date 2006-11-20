## 
## $Id: Makefile,v 1.14 2006/03/21 20:55:35 pspencer Exp $
##
## Makefile - Used to prepare ka-map distributions
##
## Useage:
##
## Run 'make' to build the default set of packages
## for windows (zip), linux (tar.gz) and ms4w.  For ms4w, make sure that
## your project is appropriate for an ms4w installation.  You will need
## to add an ms4w folder to the root of your project and create an ms4w
## directory structure that contains the appropriate files at the right
## places (like an httpd_project.conf file in ms4w/httpd.d/)
##
## used with make, targets are
##
##  <none> - builds default list which is 'all'
##  linux - builds a .tar.gz file
##  windows - builds a .zip file
##  ms4w - builds an ms4w package
##  all - all three :).
##
## Internal variables are:
## 
## BUILD        - the build date
## VERSION      - the build version, update with each release
## PROJECT-NAME - the name of the final package less the build and version
## PROJECT-DIRS - directories from the project to include in the package
##

BUILD           = $(shell date +%Y%m%d)
VERSION         = 0.2
PROJECT-NAME    = ka-map
KA-MAP-FILES    = docs htdocs include \
				  AUTHORS.TXT HISTORY.TXT \
				  README.TXT COPYING.TXT \
				  TODO.TXT
CUR-DIR         = $(shell pwd)
#CVS-TAG         = -P -d -r rel-0-2    #for version 0.2
CVS-TAG         = -P -d -A           #for HEAD

#JSDOC stuff
JSDOC			= /usr/bin/perl ../jsdoc/jsdoc.pl -d docs --project-name ka-Map

##
## You shouldn't need to edit anything past this point.
##

PROJECT-PKG = $(PROJECT-NAME)-$(VERSION)-$(BUILD)
LINUX-PKG   = $(PROJECT-PKG).tar.gz
WINDOWS-PKG = $(PROJECT-PKG).zip
MS4W-PKG    = $(PROJECT-NAME)-ms4w-$(VERSION).zip

default: all

all: linux windows ms4w

.PHONY: base
base:
	@if test ! -e builds; \
	then \
		echo "Making builds directory..."; \
		mkdir builds; \
	fi
	@echo "Creating build/$(PROJECT-PKG) temporary directory..."
	@if test -e builds/$(PROJECT-PKG); \
	then \
		echo "Removing previous temporary directory..."; \
		rm -rf builds/$(PROJECT-PKG); \
	fi

	@mkdir builds/$(PROJECT-PKG)

.PHONY: ka-map
ka-map: base
	@echo "updating ka-map and adding to build ..."
	@cvs -Q update $(CVS-TAG) >> /dev/null
	@cvs -Q update -A Makefile >> /dev/null
	@for f in $(KA-MAP-FILES); do \
		if test -e $$f; \
		then \
			mkdir -p `dirname builds/$(PROJECT-PKG)/$$f`; \
			cp -r $$f builds/$(PROJECT-PKG)/$$f; \
		fi; \
	done
	@echo "done."

.PHONY: jsdoc
jsdoc: ka-map
	@echo "running jsdoc ..."
	$(JSDOC) ./htdocs/DHTMLapi.js \
	         ./htdocs/kaKeymap.js \
	         ./htdocs/kaLegend.js \
	         ./htdocs/kaMap.js \
	         ./htdocs/kaQuery.js \
	         ./htdocs/kaScalebar.js \
	         ./htdocs/kaTool.js \
	         ./htdocs/kaZoomer.js \
	         ./htdocs/scalebar/scalebar.js \
	         ./htdocs/wmsLayer.js \
	         ./htdocs/xhr.js \
	         ./htdocs/XMLOverlay/kaOverlay.js \
	         ./htdocs/XMLOverlay/kaXmlOverlay.js \
	         ./htdocs/XMLOverlay/overlayLayer.js

.PHONY: archive
archive: jsdoc
	@if test -e builds/$(PROJECT-PKG); \
	then \
		echo "Removing CVS and other files..." ; \
		find builds/$(PROJECT-PKG) -name CVS -prune -exec rm -rf {} \; ; \
		find builds/$(PROJECT-PKG) -name "*~" -exec rm -rf {} \; ; \
		find builds/$(PROJECT-PKG) -name "*.ts" -exec rm -f {} \; ; \
		find builds/$(PROJECT-PKG) -name "*.cjs" -exec rm -f {} \; ; \
		find builds/$(PROJECT-PKG) -name ".DS_Store" -exec rm -f {} \; ; \
		find builds/$(PROJECT-PKG) -name "._*" -exec rm -f {} \; ; \
	fi

.PHONEY: windows
windows: archive
	@echo "Packaging $(PROJECT-NAME) for WINDOWS in $(WINDOWS-PKG)"
	@if test -e builds/$(WINDOWS-PKG); \
	then \
		echo "Removing old archive file..."; \
		rm builds/$(WINDOWS-PKG); \
	fi
	@if test -e builds/$(PROJECT-PKG); \
	then \
		echo "Archiving $(PROJECT-NAME) to builds/$(WINDOWS-PKG)..."; \
		cd builds; \
		zip -r -q -9 $(WINDOWS-PKG) $(PROJECT-PKG) ; \
		rm -rf $(PROJECT-PKG); \
		unzip -q $(WINDOWS-PKG); \
		cd ..; \
	fi

.PHONEY: linux
linux: archive
	@echo "Packaging $(PROJECT-NAME) for LINUX in $(LINUX-PKG)"
	@if test -e builds/$(LINUX-PKG); \
	then \
		echo "Removing old archive file $(LINUX-PKG)"; \
		rm builds/$(LINUX-PKG); \
	fi
	@if test -e builds/$(PROJECT-PKG); \
	then \
		echo "Archiving $(PROJECT-NAME) to builds/$(LINUX-PKG)..."; \
		cd builds; \
		tar czf $(LINUX-PKG) $(PROJECT-PKG); \
		rm -rf $(PROJECT-PKG); \
		tar zxf $(LINUX-PKG); \
		cd ..; \
	fi

.PHONEY: ms4w
ms4w: archive
	@echo "Packaging $(PROJECT-NAME) for MS4W in $(MS4W-PKG)";
	@if test -e builds/$(MS4W-PKG); \
	then \
		echo "Removing builds/$(MS4W-PKG) file..."; \
		rm builds/$(MS4W-PKG); \
	fi
	@if test -e builds/ms4w; \
	then \
		echo "Removing builds/ms4w build directory..."; \
		rm -rf builds/ms4w; \
	fi
	@if true; \
	then \
		echo "Copying ms4w support files into builds/ms4w..."; \
		cp -r ms4w builds; \
		cd builds; \
		pwd; \
		echo "Pruning cvs folders..."; \
		find ms4w -name CVS -prune -exec rm -rf {} \; ; \
		find ms4w -name .DS_Store -prune -exec rm -rf {} \; ; \
		mv ms4w/apps/$(PROJECT-NAME) ms4w/apps/$(PROJECT-NAME)-$(VERSION); \
		echo "Copying $(PROJECT-NAME) to ms4w/apps/$(PROJECT-NAME)..."; \
		cp -r $(PROJECT-PKG)/ ms4w/apps/$(PROJECT-NAME)-$(VERSION); \
		echo "Archiving $(PROJECT-NAME) to builds/$(MS4W-PKG)"; \
		zip -r -q -9 $(MS4W-PKG) ms4w; \
		cd ..; \
	fi

