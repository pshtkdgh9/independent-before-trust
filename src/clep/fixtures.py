"""Small hand-authored parallel fixtures for protocol falsification only."""

from .core import EpistemicItem


def pilot_items() -> list[EpistemicItem]:
    groups = [
        ("g1", "Ada", "arrive", "negative", "possible", {"en": "Ada may not arrive.", "ko": "Ada는 도착하지 않을 수도 있다.", "es": "Es posible que Ada no llegue."}),
        ("g2", "Bruno", "approve", "positive", "probable", {"en": "Bruno will probably approve.", "ko": "Bruno는 아마 승인할 것이다.", "es": "Bruno probablemente aprobará."}),
        ("g3", "Cora", "resign", "positive", "certain", {"en": "Cora will certainly resign.", "ko": "Cora는 확실히 사임할 것이다.", "es": "Cora sin duda dimitirá."}),
        ("g4", "Diego", "attend", "negative", "certain", {"en": "Diego definitely will not attend.", "ko": "Diego는 분명 참석하지 않을 것이다.", "es": "Diego definitivamente no asistirá."}),
    ]
    return [
        EpistemicItem(f"{group}-{language}", language, evidence, speaker, proposition, polarity, certainty, group)
        for group, speaker, proposition, polarity, certainty, texts in groups
        for language, evidence in texts.items()
    ]
