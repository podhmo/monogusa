ui-slack:
	@SLACKCLI_API_TOKEN=$(shell jqfpy 'get("slack/api-token")' ~/.config/monogusa/config.json -r ) python -m monogusa.chatbot.slackcli cli.py
