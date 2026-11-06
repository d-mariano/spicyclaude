"""The shared severity scale, strictest first. Imported by ship_config and review_gate."""

SEVERITIES = ("Critical", "High", "Medium", "Low")


def at_least(severity, floor):
    """True when severity is as strict as floor or stricter."""
    return SEVERITIES.index(severity) <= SEVERITIES.index(floor)
