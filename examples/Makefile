00:
	python -m monogusa.cli $$(echo $@*)/commands.py hello | tee $$(echo $@*)/output.hello.txt
	python -m monogusa.cli $$(echo $@*)/commands.py bye | tee $$(echo $@*)/output.bye.txt
	python -m monogusa.cli $$(echo $@*)/commands.py bye -h 2>&1 | tee $$(echo $@*)/output.bye-help.txt
