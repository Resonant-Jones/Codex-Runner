from __future__ import annotations

from .contracts import GateReceipt, LoopReceipt


def build_gate_receipt(**kwargs: object) -> GateReceipt:
    receipt = GateReceipt(**kwargs)
    receipt.validate()
    return receipt


def build_loop_receipt(**kwargs: object) -> LoopReceipt:
    receipt = LoopReceipt(**kwargs)
    receipt.validate()
    return receipt

