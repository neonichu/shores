.PHONY: all clean deploy

FILES = index.html

deploy: all
	scp $(FILES) vu0:vu0.org/projects/shores

all: $(FILES)

clean:
	rm -f $(FILES)

.SUFFIXES: html md

%.html: %.md
	markdown $< >$@
