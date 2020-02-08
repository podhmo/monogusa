import json
import datetime
from functools import (
    singledispatch,
    partial,
)


@singledispatch
def encode(o):
    # dateclasses
    if hasattr(o.__class__, "__dataclass_fields__"):
        from dataclasses import asdict

        return asdict(o)

    # pydantic.BaseModel
    if hasattr(o, "json"):
        return o.json()

    
    raise TypeError(
        "Object of type '%s' is not JSON serializable" % o.__class__.__name__
    )


register = encode.register

# register
@register(datetime.datetime)
def encode_datetime(o: datetime.datetime) -> str:
    return o.isoformat()


@register(datetime.date)
def encode_date(o: datetime.date) -> str:
    return o.isoformat()


dump = partial(json.dump, indent=2, ensure_ascii=False, sort_keys=True, default=encode)
dumps = partial(
    json.dumps, indent=2, ensure_ascii=False, sort_keys=True, default=encode
)
load = json.load
loads = json.loads
