from monogusa import reactions


# TODO: rename
def setup() -> None:
    from monogusa import default_once
    from .reactions import reply_message, send_message

    @default_once
    def get_reply_function() -> reactions.reply_message:

        return reply_message

    @default_once
    def get_send_function() -> reactions.send_message:

        return send_message
