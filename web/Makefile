.PHONY: all clean

FILES = index.html

all: $(FILES)

clean:
	rm -f $(FILES)

.SUFFIXES: html md

%.html: %.md
	markdown $< >$@
