from types import SimpleNamespace

import pytest

from STISim.relationship import vaccine_transmission_factors


@pytest.mark.parametrize(
    ("mechanism", "expected"),
    [
        ("none", (1.0, 1.0)),
        ("susceptibility_only", (1.0, 0.2)),
        ("infectiousness_only", (0.2, 1.0)),
        ("both", (0.2, 0.2)),
    ],
)
def test_vaccine_transmission_mechanisms(mechanism, expected):
    infector = SimpleNamespace(vaccined=True, current_efficacy=0.8)
    infectee = SimpleNamespace(vaccined=True, current_efficacy=0.8)

    factors = vaccine_transmission_factors(infector, infectee, mechanism)

    assert factors == pytest.approx(expected)
