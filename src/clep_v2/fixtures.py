"""Predeclared closed-label parallel items for CLEP protocol v2."""

from .core import ClosedItem


def pilot_items() -> list[ClosedItem]:
    groups = [
        ("g1", "ADA", "ARRIVE", "NEGATIVE", "POSSIBLE", ("Ada may not arrive.", "Ada는 도착하지 않을 수도 있다.", "Es posible que Ada no llegue.")),
        ("g2", "BRUNO", "APPROVE", "POSITIVE", "PROBABLE", ("Bruno will probably approve.", "Bruno는 아마 승인할 것이다.", "Bruno probablemente aprobará.")),
        ("g3", "CORA", "RESIGN", "POSITIVE", "CERTAIN", ("Cora will certainly resign.", "Cora는 확실히 사임할 것이다.", "Cora sin duda dimitirá.")),
        ("g4", "DIEGO", "ATTEND", "NEGATIVE", "CERTAIN", ("Diego definitely will not attend.", "Diego는 분명 참석하지 않을 것이다.", "Diego definitivamente no asistirá.")),
        ("g5", "ADA", "APPROVE", "POSITIVE", "POSSIBLE", ("Ada may approve.", "Ada는 승인할 수도 있다.", "Ada puede que apruebe.")),
        ("g6", "BRUNO", "RESIGN", "NEGATIVE", "PROBABLE", ("Bruno probably will not resign.", "Bruno는 아마 사임하지 않을 것이다.", "Bruno probablemente no dimitirá.")),
        ("g7", "CORA", "ATTEND", "POSITIVE", "PROBABLE", ("Cora is likely to attend.", "Cora는 참석할 가능성이 높다.", "Es probable que Cora asista.")),
        ("g8", "DIEGO", "ARRIVE", "POSITIVE", "CERTAIN", ("Diego will definitely arrive.", "Diego는 분명 도착할 것이다.", "Diego llegará con certeza.")),
    ]
    languages = ("en", "ko", "es")
    return [ClosedItem(f"{group}-{language}", language, evidence, speaker, action, polarity, certainty, group) for group, speaker, action, polarity, certainty, texts in groups for language, evidence in zip(languages, texts)]
