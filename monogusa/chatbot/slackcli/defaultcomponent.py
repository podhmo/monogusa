from monogusa import reactions


def setup(token: str) -> None:
    from monogusa import default_once
    from .reactions import MessageHandler

    handler = MessageHandler(token)

    @default_once
    def get_reply_function() -> reactions.reply_message:
        return handler.reply_message

    @default_once
    def get_send_function() -> reactions.send_message:
        return handler.send_message
