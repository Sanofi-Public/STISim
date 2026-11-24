from STISim.config import get_config


def test_age_group_keys_are_tuples():
    config = get_config("config.json")

    first_age_group = next(iter(config["male_age_groups"].keys()))

    assert isinstance(first_age_group, tuple)
    assert first_age_group == (15, 19)
