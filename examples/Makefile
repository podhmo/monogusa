default: 00 01 02 03 04

00:
	mkdir -p $(shell echo $@*/)dst
	python -m monogusa.cli $(shell echo $@*/)commands.py hello | tee $(shell echo $@*/)dst/hello.txt
	python -m monogusa.cli $(shell echo $@*/)commands.py bye | tee $(shell echo $@*/)dst/bye.txt
	python -m monogusa.cli $(shell echo $@*/)commands.py bye -h 2>&1 | tee $(shell echo $@*/)dst/bye-help.txt

01-generate:
	mkdir -p $(shell echo 01*/)dst
	python -m monogusa.web --with-main 01*/commands.py | black - | sed "s@$(shell pwd)/@@g" > $(shell echo 01*/)web.py

01: 01-generate
	mkdir -p $(shell echo $@*/)dst
	( test -f _$@.pid && kill $$(cat _$@.pid) || exit 0 ) && rm -f _$@.pid
	python $(shell echo $@*/)web.py --port=44444 & echo $$! > _$@.pid
	python $(shell echo $@*/)web.py --show-doc > $(shell echo $@*/)dst/openapi.yaml
	sleep 0.5
	cat $(shell echo $@*/)inputs/hello.json | http -b --json POST :44444/hello | jqfpy 'd = get(); d.pop("duration",None); d' | tee $(shell echo $@*/)dst/hello.output
	cat $(shell echo $@*/)inputs/bye.json | http -b --json POST :44444/bye | jqfpy 'd = get(); d.pop("duration",None); d' | tee $(shell echo $@*/)dst/bye.output
	( test -f _$@.pid && kill $$(cat _$@.pid) || exit 0 ) && rm -f _$@.pid

02:
	mkdir -p $(shell echo $@*/)dst
	python -m monogusa.cli $(shell echo $@*/)commands.py hello | tee $(shell echo $@*/)dst/hello.txt
	DEBUG=1 LOGGING=DEBUG python -m monogusa.cli $(shell echo $@*/)commands.py hello 2>&1 | tee $(shell echo $@*/)dst/hello-with-environ.txt
	python -m monogusa.cli $(shell echo $@*/)commands.py --debug --logging=DEBUG hello 2>&1 | tee $(shell echo $@*/)dst/hello-with-option.txt
	python -m monogusa.cli $(shell echo $@*/)commands.py --debug --logging=DEBUG - hello --debug 2>&1 | tee $(shell echo $@*/)dst/hello-with-option-with-debug-ok.txt
	python -m monogusa.cli $(shell echo $@*/)commands.py --debug --logging=DEBUG hello --debug 2>&1 | tee $(shell echo $@*/)dst/hello-with-option-with-debug-ng.txt

03:
	mkdir -p $(shell echo $@*/)dst
	python -m monogusa.cli $(shell echo $@*/)commands.py list --uncompleted | tee $(shell echo $@*/)dst/list.json
	python -m monogusa.cli $(shell echo $@*/)commands.py -h 2>&1 | tee $(shell echo $@*/)dst/help.txt
	python -m monogusa.cli $(shell echo $@*/)commands.py list -h 2>&1 | tee $(shell echo $@*/)dst/list-help.txt

04:
	mkdir -p $(shell echo $@*/)dst
	python $(shell echo $@*/)00*.py hello --name world | tee $(shell echo $@*/)dst/00hello.txt
	python $(shell echo $@*/)00*.py -h 2>&1 | tee $(shell echo $@*/)dst/00help.txt
	python $(shell echo $@*/)00*.py hello -h 2>&1 | tee $(shell echo $@*/)dst/00hello-help.txt
	python $(shell echo $@*/)01*.py hello --name world | tee $(shell echo $@*/)dst/01hello.txt


clean:
	rm -rf **/dst/*
.PHONY: clean
