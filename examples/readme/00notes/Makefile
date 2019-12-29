help:
	python -m monogusa.cli cli.py -h
init:
	python -m monogusa.cli cli.py init
add: TEXT ?= hello
add:
	python -m monogusa.cli cli.py add --text="${TEXT}"

list:
	python -m monogusa.cli cli.py list

ui-discord:
	python -m monogusa.chatbot.discordcli cli.py --name=notes
ui-slack:
	python -m monogusa.chatbot.slackcli cli.py --name=notes
ui-web: web-codegen
	python web.py --port=55555

web-codegen:
	python -m monogusa.web cli.py --dst .
