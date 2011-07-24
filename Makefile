DESTDIR?=/
datadir?=$(DESTDIR)/usr/share
INSTALL=install

SOURCES=$(wildcard *.desktop.in)
TARGETS=${SOURCES:.in=}

all: $(TARGETS) icons

icons:
	for i in 96 72 64 48 36 32 24 22 16; do \
		convert -background none ojuba-mimic.svg -resize $${i}x$${i} ojuba-mimic-$${i}.png; \
	done
pos:
	make -C po all

install: all
	python setup.py install -O2 --root $(DESTDIR)
	$(INSTALL) -d $(datadir)/applications/
	$(INSTALL) -m 0644 ojuba-mimic.desktop $(datadir)/applications/
	$(INSTALL) -m 0644 -D ojuba-mimic.svg $(datadir)/icons/hicolor/scalable/apps/ojuba-mimic.svg;
	for i in 96 72 64 48 36 32 24 22 16; do \
		install -d $(datadir)/icons/hicolor/$${i}x$${i}/apps; \
		$(INSTALL) -m 0644 -D ojuba-mimic-$${i}.png $(datadir)/icons/hicolor/$${i}x$${i}/apps/ojuba-mimic.png; \
	done

%.desktop: %.desktop.in pos
	intltool-merge -d po $< $@

clean:
	rm -f $(TARGETS)
	for i in 96 72 64 48 36 32 24 22 16; do \
		rm -f ojuba-mimic-$${i}.png; \
	done

