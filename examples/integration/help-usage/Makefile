default: 00 01 02 03

00: dst
	python -u -m monogusa.cli -h 2>&1 | tee dst/$@cli-help.output
01: dst
	python -u -m monogusa.web -h 2>&1 | tee dst/$@web-help.output
02: dst
	python -u -m monogusa.chatbot.slackcli -h 2>&1 | tee dst/$@chatbot.slackcli-help.output
03: dst
	python -u -m monogusa.chatbot.discordcli -h 2>&1 | tee dst/$@chatbot.discordcli-help.output

dst:
	mkdir -p $@
