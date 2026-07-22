"""Hand-authored controlled facts for the falsification pilot."""

from __future__ import annotations

from .core import EvidenceTemplate


_FACTS = (
    ("Aster probe", "was launched in", "2012", "2017", "What year was the Aster probe launched?"),
    ("Beryl bridge", "opened in", "1998", "2003", "What year did the Beryl bridge open?"),
    ("Cobalt archive", "contains", "48 volumes", "53 volumes", "How many volumes does the Cobalt archive contain?"),
    ("Dahlia station", "stands", "610 meters", "740 meters", "At what elevation does Dahlia station stand?"),
    ("Elm ferry", "departs at", "06:40", "07:15", "When does the Elm ferry depart?"),
    ("Flint museum", "was founded in", "1964", "1971", "When was the Flint museum founded?"),
    ("Garnet trail", "extends for", "18 kilometers", "23 kilometers", "How long is the Garnet trail?"),
    ("Hazel library", "closes at", "20:00", "21:30", "When does the Hazel library close?"),
    ("Indigo tunnel", "has", "7 exits", "9 exits", "How many exits does the Indigo tunnel have?"),
    ("Juniper clinic", "opened in", "2008", "2014", "When did the Juniper clinic open?"),
    ("Kestrel tower", "is", "84 meters tall", "96 meters tall", "How tall is the Kestrel tower?"),
    ("Linden reservoir", "holds", "32 million liters", "41 million liters", "What is the capacity of the Linden reservoir?"),
    ("Mica observatory", "began operations in", "1986", "1991", "When did the Mica observatory begin operations?"),
    ("Nectar tram", "serves", "14 stops", "17 stops", "How many stops does the Nectar tram serve?"),
    ("Onyx theater", "seats", "520 people", "680 people", "What is the seating capacity of the Onyx theater?"),
    ("Pine laboratory", "has", "6 clean rooms", "8 clean rooms", "How many clean rooms does the Pine laboratory have?"),
    ("Quartz canal", "was completed in", "1924", "1931", "When was the Quartz canal completed?"),
    ("Rowan hall", "hosts", "12 exhibits", "15 exhibits", "How many exhibits does Rowan hall host?"),
    ("Saffron route", "takes", "45 minutes", "58 minutes", "How long does the Saffron route take?"),
    ("Topaz garden", "contains", "27 species", "34 species", "How many species does the Topaz garden contain?"),
)


def pilot_templates() -> list[EvidenceTemplate]:
    templates: list[EvidenceTemplate] = []
    for index, (subject, relation, original, counterfactual, query) in enumerate(_FACTS, 1):
        templates.append(
            EvidenceTemplate(
                item_id=f"dcea-{index:03d}",
                query=query,
                subject=f"the {subject}",
                relation=relation,
                original_value=original,
                counterfactual_value=counterfactual,
                distractor=f"The {subject} is described in the regional directory.",
                source_ids=(f"S{index:02d}A", f"S{index:02d}B", f"S{index:02d}C"),
            )
        )
    return templates
