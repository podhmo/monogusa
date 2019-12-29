# notes

Tiny todo app like example, something like described by below pages.

- https://www.starlette.io/database/
- https://fastapi.tiangolo.com/tutorial/async-sql-databases/

## cli

```console
# init db
$ make init
python -m monogusa.cli cli.py init
$ ls *.db
test.db

# add notes
$ make add
python -m monogusa.cli cli.py add --text="hello"
{'text': 'hello', 'completed': False, 'id': 1}
$ make add TEXT="go to bed"
python -m monogusa.cli cli.py add --text="go to bed"
{'text': 'go to bed', 'completed': False, 'id': 2}

# list
$ make list
python -m monogusa.cli cli.py list
{'id': 1, 'text': 'hello', 'completed': False}
{'id': 2, 'text': 'go to bed', 'completed': False}
```

## as slackbot

:warning: need `SLACKBOT_API_TOKEN`

```console
$ make ui-slack
python -m monogusa.chatbot.slackcli cli.py --name=notes
```

## as discordbot

:warning: need `DISCORDBOT_API_TOKEN`

```console
$ make ui-discord
python -m monogusa.chatbot.discordcli cli.py --name=notes
```
