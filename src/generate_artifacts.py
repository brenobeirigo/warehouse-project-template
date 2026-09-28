"""Generate the example analysis outputs without compiling the report."""

from src.pipeline import (
    EXAMPLE_FACTOR,
    ensure_data,
    read_inventory,
    write_baseline,
    write_scenario,
)


def generate_artifacts():
    source = ensure_data(include_all=False)
    records = read_inventory(source)
    write_baseline(records, source)
    write_scenario(records, EXAMPLE_FACTOR)


if __name__ == "__main__":
    generate_artifacts()
