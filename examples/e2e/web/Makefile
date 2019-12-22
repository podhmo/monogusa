default: 00

00-generate:
	# dry run: --dry-run
	mkdir -p $(shell echo 00*/)dst
	cd $(shell echo 00*/) && python -m monogusa.web commands.py
	black $(shell echo 00*/)*.py

# call api
00: 00-generate
	mkdir -p $(shell echo $@*/)dst
	( test -f _$@.pid && kill $$(cat _$@.pid) || exit 0 ) && rm -f _$@.pid
	python $(shell echo $@*/)web.py --port=44444 & echo $$! > _$@.pid
	python $(shell echo $@*/)web.py --show-doc > $(shell echo $@*/)dst/openapi.yaml
	sleep 0.5
	cat $(shell echo $@*/)inputs/hello.json | http -b --json POST :44444/hello | jqfpy 'd = get(); d.pop("duration",None); d' | tee $(shell echo $@*/)dst/hello.output
	cat $(shell echo $@*/)inputs/bye.json | http -b --json POST :44444/bye | jqfpy 'd = get(); d.pop("duration",None); d' | tee $(shell echo $@*/)dst/bye.output
	( test -f _$@.pid && kill $$(cat _$@.pid) || exit 0 ) && rm -f _$@.pid

clean:
	rm -rf **/dst/*
.PHONY: clean
