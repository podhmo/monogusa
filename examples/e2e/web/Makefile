default: 00 01

CUT := jqfpy 'd = get(); d.pop("duration",None); d'

generate: TARGET ?= 00
generate:
	# dry run: --dry-run
	mkdir -p $(shell echo ${TARGET}*/)dst
	cd $(shell echo ${TARGET}*/) && python -m monogusa.web commands.py
	black $(shell echo ${TARGET}*/)*.py

# call api
00-generate:
	TARGET=00 $(MAKE) generate
00: 00-generate
	mkdir -p $(shell echo $@*/)dst
	( test -f _$@.pid && kill $$(cat _$@.pid) || exit 0 ) && rm -f _$@.pid
	python $(shell echo $@*/)web.py --port=444$@ & echo $$! > _$@.pid
	python $(shell echo $@*/)web.py --show-doc > $(shell echo $@*/)dst/openapi.yaml
	sleep 0.5
	cat $(shell echo $@*/)inputs/hello.json | http -b --json POST :444$@/hello | $(CUT) | tee $(shell echo $@*/)dst/hello.output
	cat $(shell echo $@*/)inputs/bye.json | http -b --json POST :444$@/bye | $(CUT) | tee $(shell echo $@*/)dst/bye.output
	( test -f _$@.pid && kill $$(cat _$@.pid) || exit 0 ) && rm -f _$@.pid


# with dependency injection
01-generate:
	TARGET=01 $(MAKE) generate
01: 01-generate
	mkdir -p $(shell echo $@*/)dst
	( test -f _$@.pid && kill $$(cat _$@.pid) || exit 0 ) && rm -f _$@.pid
	python $(shell echo $@*/)web.py --port=444$@ & echo $$! > _$@.pid
	python $(shell echo $@*/)web.py --show-doc > $(shell echo $@*/)dst/openapi.yaml
	sleep 0.5
	cat $(shell echo $@*/)inputs/hello.json | http -b --json POST :444$@/hello | $(CUT) | tee $(shell echo $@*/)dst/hello.output
	http -b --json POST :444$@/byebye | $(CUT) | tee $(shell echo $@*/)dst/byebye.output
	( test -f _$@.pid && kill $$(cat _$@.pid) || exit 0 ) && rm -f _$@.pid

clean:
	rm -rf **/dst/*
.PHONY: clean
