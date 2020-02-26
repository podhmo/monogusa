default: 00 01

00: dst
	cat $(shell echo $@*messages) | python -m monogusa.cli $(shell echo $@*.py) read | tee dst/$(patsubst %.py,%.output,$(shell echo $@*.py))

01: dst
	cat $(shell echo $@*messages) | python -m monogusa.cli $(shell echo $@*.py) read | tee dst/$(patsubst %.py,%.output,$(shell echo $@*.py))
	@echo --- 1>&2
	python -m monogusa.cli $(shell echo $@*.py) read | tee dst/$(patsubst %.py,%.fake.output,$(shell echo $@*.py))

02: dst
	DEBUG=1 LOGGING_LEVEL=INFO python -m monogusa.cli $(shell echo $@*.py) read | tee dst/$(patsubst %.py,%.output,$(shell echo $@*.py))

typing:
	mypy --strict *.py
.PHONY: typing
clean:
	rm -rf dst
.PHONY: clean
dst:
	mkdir -p dst
