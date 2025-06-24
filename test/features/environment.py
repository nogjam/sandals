from behave.runner import Context

from sandals import core
from test.features.util import ContextStore


def before_all(ctx: Context) -> None:
    ctx.store = ContextStore()
