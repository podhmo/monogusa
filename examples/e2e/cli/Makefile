default: 00 01 02 03 04 05 06

# normal usecase
00:
	mkdir -p $(shell echo $@*/)dst
	python -m monogusa.cli $(shell echo $@*/)commands.py hello | tee $(shell echo $@*/)dst/hello.txt
	python -m monogusa.cli $(shell echo $@*/)commands.py bye | tee $(shell echo $@*/)dst/bye.txt
	python -m monogusa.cli $(shell echo $@*/)commands.py bye -h 2>&1 | tee $(shell echo $@*/)dst/bye-help.txt

# async support (with varenv, and debugging flag)
01:
	mkdir -p $(shell echo $@*/)dst
	python -u -m monogusa.cli $(shell echo $@*/)commands.py hello | tee $(shell echo $@*/)dst/hello.txt
	DEBUG=1 LOGGING=INFO python -u -m monogusa.cli $(shell echo $@*/)commands.py hello 2>&1 | tee $(shell echo $@*/)dst/hello-with-environ.txt
	python -u -m monogusa.cli $(shell echo $@*/)commands.py --debug --logging=INFO hello 2>&1 | tee $(shell echo $@*/)dst/hello-with-option.txt
	python -u -m monogusa.cli $(shell echo $@*/)commands.py --debug - --logging=INFO hello --debug 2>&1 | tee $(shell echo $@*/)dst/hello-with-option-with-debug-ok.txt
	python -u -m monogusa.cli $(shell echo $@*/)commands.py --debug --logging=INFO hello --debug 2>&1 | tee $(shell echo $@*/)dst/hello-with-option-with-debug-ng.txt

# dependency injection (positional arguments)
02:
	mkdir -p $(shell echo $@*/)dst
	python -m monogusa.cli $(shell echo $@*/)commands.py list --uncompleted | tee $(shell echo $@*/)dst/list.json
	python -m monogusa.cli $(shell echo $@*/)commands.py -h 2>&1 | tee $(shell echo $@*/)dst/help.txt
	python -m monogusa.cli $(shell echo $@*/)commands.py list -h 2>&1 | tee $(shell echo $@*/)dst/list-help.txt

# call main (__name__ == "__main__")
03:
	mkdir -p $(shell echo $@*/)dst
	python $(shell echo $@*/)00*.py hello --name world | tee $(shell echo $@*/)dst/00hello.txt
	python $(shell echo $@*/)00*.py -h 2>&1 | tee $(shell echo $@*/)dst/00help.txt
	python $(shell echo $@*/)00*.py hello -h 2>&1 | tee $(shell echo $@*/)dst/00hello-help.txt
	python $(shell echo $@*/)01*.py hello --name world | tee $(shell echo $@*/)dst/01hello.txt

# ignore marker
04:
	mkdir -p $(shell echo $@*/)dst
	python -m monogusa.cli $(shell echo $@*/)commands.py -h 2>&1 | tee $(shell echo $@*/)dst/help.txt

# di with async/await
05:
	mkdir -p $(shell echo $@*/)dst
	python -m monogusa.cli $(shell echo $@*/)commands.py hello 2>&1 | tee $(shell echo $@*/)dst/hello.txt

# only marker
06:
	mkdir -p $(shell echo $@*/)dst
	python -m monogusa.cli $(shell echo $@*/)commands.py -h 2>&1 | tee $(shell echo $@*/)dst/help.txt
	python -m monogusa.cli --ignore-only $(shell echo $@*/)commands.py -h 2>&1 | tee $(shell echo $@*/)dst/help-ignore-only.txt


clean:
	rm -rf **/dst/*
.PHONY: clean
