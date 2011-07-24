POTFILE=$(shell cat POTFILES.in)
SOURCES=$(addprefix ../, $(POTFILE))
POFILES=$(wildcard *.po)
MOFILES=$(patsubst %.po,%.mo,$(POFILES))

all: ojuba-mimic.pot $(MOFILES)

ojuba-mimic.pot: $(SOURCES)
	echo $(SOURCES)
	intltool-update -g ojuba-mimic -p

%.mo: %.po
	msgfmt $*.po -o $*.mo
	mkdir -p ../locale/$*/LC_MESSAGES/ || :
	cp $*.mo ../locale/$*/LC_MESSAGES/ojuba-mimic.mo

%.po: ojuba-mimic.pot
	intltool-update -g ojuba-mimic -d $*

