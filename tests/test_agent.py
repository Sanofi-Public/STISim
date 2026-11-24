from STISim.agent import Agent


def test_agent_assigns_incrementing_ids():
    Agent._id_counter = 1

    first = Agent("male", 20, (20, 24), "heterosexual", 1)
    second = Agent("female", 20, (20, 24), "heterosexual", 1)

    assert first.id == 1
    assert second.id == 2
