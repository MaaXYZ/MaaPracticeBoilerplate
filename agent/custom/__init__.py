import sys

from . import action, reco

sys.modules.setdefault("custom", sys.modules[__name__])
sys.modules.setdefault("custom.action", action)
sys.modules.setdefault("custom.reco", reco)


def register_all() -> None:
    action.register_all()
    reco.register_all()


__all__ = ["register_all"]
