from northstar.loader import load_knowledge_base


def test_knowledge_base_loads_and_validates():
    kb = load_knowledge_base()
    assert len(kb.programmes) >= 20, "seed must stay representative (>=20 real programmes)"
    assert kb.scale.points["A"] == 5.0
    assert kb.scale.points["S"] == 0.5
    assert not kb.scale.is_principal_pass("S")
    assert kb.scale.is_principal_pass("E")


def test_every_programme_is_sourced_and_checklisted():
    kb = load_knowledge_base()
    for p in kb.programmes:
        assert p.source, f"{p.id} missing source"
        assert "what_is_it" in p.checklist, f"{p.id} missing checklist"
        assert p.slots, f"{p.id} has no rule slots"


def test_combinations_reference_known_subjects():
    kb = load_knowledge_base()
    for c in kb.combinations.values():
        for s in c.subjects:
            assert s in kb.subjects
