from magicalimport import import_symbol
from fastapi import FastAPI
from monogusa.web import cli

router = import_symbol("./routes.py:router", here=__file__)
app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    cli.run(app)
