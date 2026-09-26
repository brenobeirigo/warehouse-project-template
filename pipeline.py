"""One command for data acquisition, analysis, scenarios, and the report."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from collections import defaultdict
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from pathlib import Path

import xlrd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, StrMethodFormatter


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
ARTIFACTS = ROOT / "artifacts"
MANIFEST = ROOT / "data" / "sources.json"
EXAMPLE_FACTOR = Decimal("1.10")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_hash(path: Path, expected: str) -> None:
    actual = sha256(path)
    if actual.lower() != expected.lower():
        raise ValueError(
            f"Checksum mismatch for {path}. Expected {expected}, got {actual}. "
            "Remove the invalid file and run again."
        )


def sources() -> dict[str, dict[str, str]]:
    with MANIFEST.open(encoding="utf-8") as stream:
        return json.load(stream)


def download(url: str, destination: Path, expected_hash: str) -> None:
    """Save a verified download atomically, without retaining partial files."""
    partial = destination.with_name(destination.name + ".part")
    partial.unlink(missing_ok=True)
    print(f"Downloading {url}", flush=True)
    request = urllib.request.Request(
        url, headers={"User-Agent": "warehouse-course-template/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            with partial.open("wb") as output:
                shutil.copyfileobj(response, output)
        check_hash(partial, expected_hash)
        partial.replace(destination)
    finally:
        partial.unlink(missing_ok=True)


def ensure_source(spec: dict[str, str]) -> Path:
    """Verify a local source or fetch it from the approved course URL."""
    if "file" in spec:
        path = RAW / spec["file"]
        if path.exists():
            check_hash(path, spec["file_sha256"])
            print(f"Using checked local file: {path.relative_to(ROOT)}")
        else:
            download(spec["url"], path, spec["file_sha256"])
        return path

    extracted = RAW / spec["member"]
    archive = RAW / spec["archive"]
    if extracted.exists():
        check_hash(extracted, spec["member_sha256"])
        print(f"Using checked local file: {extracted.relative_to(ROOT)}")
        return extracted

    if archive.exists():
        check_hash(archive, spec["archive_sha256"])
        print(f"Using checked local archive: {archive.relative_to(ROOT)}")
    else:
        download(spec["url"], archive, spec["archive_sha256"])

    with zipfile.ZipFile(archive) as bundle:
        if spec["member"] not in bundle.namelist():
            raise ValueError(f"Expected {spec['member']} inside {archive.name}")
        partial = extracted.with_name(extracted.name + ".part")
        partial.unlink(missing_ok=True)
        try:
            with bundle.open(spec["member"]) as source_stream:
                with partial.open("wb") as output:
                    shutil.copyfileobj(source_stream, output)
            check_hash(partial, spec["member_sha256"])
            partial.replace(extracted)
        finally:
            partial.unlink(missing_ok=True)
    print(f"Extracted {extracted.relative_to(ROOT)}")
    return extracted


def ensure_data(include_all: bool = True) -> Path:
    """Restore the full SPR bundle and return the active-location workbook."""
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = sources()
    if not include_all:
        return ensure_source(manifest["active_locations"])
    paths = {name: ensure_source(spec) for name, spec in manifest.items()}
    print(f"Checked {len(paths)} approved source files in {RAW.relative_to(ROOT)}")
    return paths["active_locations"]


def read_inventory(path: Path) -> list[tuple[str, str, int]]:
    workbook = xlrd.open_workbook(str(path), on_demand=True)
    sheet = workbook.sheet_by_name("DC23ACTIVE")
    headers = [str(value).strip().upper() for value in sheet.row_values(0)]
    columns = {name: headers.index(name) for name in ("ZONE", "SKU", "QUANTITY")}
    records: list[tuple[str, str, int]] = []
    for row_index in range(1, sheet.nrows):
        values = sheet.row_values(row_index)
        # The historical export ends with one DOS Ctrl-Z marker row.
        if values[0] == "\x1a" and all(not str(value).strip() for value in values[1:]):
            continue
        if not any(str(value).strip() for value in values):
            continue
        zone = str(values[columns["ZONE"]]).strip()
        sku = str(values[columns["SKU"]]).strip()
        try:
            quantity = Decimal(str(values[columns["QUANTITY"]]))
        except InvalidOperation as exc:
            raise ValueError(f"Invalid quantity on Excel row {row_index + 1}") from exc
        if not zone or not sku or quantity < 0 or quantity != quantity.to_integral_value():
            raise ValueError(f"Invalid zone, SKU, or quantity on Excel row {row_index + 1}")
        records.append((zone, sku, int(quantity)))
    workbook.release_resources()
    if not records:
        raise ValueError("The active-location sheet has no data rows")
    return records


def summarize(records: list[tuple[str, str, int]]) -> list[dict[str, int | str]]:
    grouped: dict[str, dict[str, object]] = defaultdict(
        lambda: {"locations": 0, "skus": set(), "units": 0}
    )
    for zone, sku, quantity in records:
        group = grouped[zone]
        group["locations"] += 1
        group["skus"].add(sku)
        group["units"] += quantity
    return [
        {
            "zone": zone,
            "active_locations": group["locations"],
            "unique_skus": len(group["skus"]),
            "units_on_hand": group["units"],
        }
        for zone, group in sorted(grouped.items())
    ]


def latex_text(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in value)


def write_zone_chart(rows: list[dict[str, int | str]], record_count: int) -> None:
    """Plot checked location counts without adding source records to the output."""
    ordered = sorted(rows, key=lambda row: int(row["active_locations"]), reverse=True)
    labels = [str(row["zone"]) for row in ordered]
    counts = [int(row["active_locations"]) for row in ordered]

    figure, axis = plt.subplots(figsize=(3.4, 2.3))
    bars = axis.barh(labels, counts, color="#19538a", height=0.62)
    axis.invert_yaxis()
    axis.set_xlim(0, max(counts) * 1.23)
    axis.bar_label(bars, labels=[f"{count:,}" for count in counts], padding=3, fontsize=7)
    axis.set_xlabel("Active-location records", fontsize=8)
    axis.set_ylabel("Zone", fontsize=8)
    axis.tick_params(axis="both", labelsize=7, length=0)
    axis.xaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
    axis.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    axis.grid(axis="x", color="#d9e1e8", linewidth=0.6)
    axis.set_axisbelow(True)
    for edge in ("top", "right", "left"):
        axis.spines[edge].set_visible(False)
    axis.spines["bottom"].set_color("#9aa9b7")
    figure.tight_layout(pad=0.4)
    figure.savefig(ARTIFACTS / "zone_locations.png", dpi=240, facecolor="white")
    plt.close(figure)

    (ARTIFACTS / "zone_chart_count.tex").write_text(
        rf"\newcommand{{\activeLocationCount}}{{{record_count:,}}}" + "\n",
        encoding="utf-8",
    )


def write_settings_table(record_count: int, zone_count: int, factor: Decimal) -> None:
    """Record the exact data and calculation settings used by this example."""
    table = [
        r"\begin{tabular}{@{}p{0.43\columnwidth}p{0.45\columnwidth}@{}}",
        r"\toprule",
        r"\textbf{Setting} & \textbf{Value} \\",
        r"\midrule",
        r"\multicolumn{2}{@{}l}{\textit{Data}} \\",
        r"\quad Source & \texttt{DC23ACTIVE} snapshot \\",
        rf"\quad Location records & \num{{{record_count}}} \\",
        rf"\quad Zones represented & \num{{{zone_count}}} \\",
        r"\addlinespace",
        r"\multicolumn{2}{@{}l}{\textit{Analysis}} \\",
        r"\quad Location measure & records by zone \\",
        r"\quad SKU measure & distinct codes by zone \\",
        r"\quad Quantity measure & selling units on hand \\",
        r"\addlinespace",
        r"\multicolumn{2}{@{}l}{\textit{Illustrative scenario}} \\",
        rf"\quad Unit multiplier & \num{{{factor}}} \\",
        r"\quad Randomness & none; deterministic \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (ARTIFACTS / "settings_table.tex").write_text(
        "\n".join(table) + "\n", encoding="utf-8"
    )


def write_baseline(records: list[tuple[str, str, int]], path: Path) -> None:
    ARTIFACTS.mkdir(exist_ok=True)
    rows = summarize(records)
    with (ARTIFACTS / "zone_summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    table = [r"\begin{tabular}{lrrr}", r"\toprule"]
    table.append(r"Zone & Locations & SKUs & Units on hand \\")
    table.append(r"\midrule")
    for row in rows:
        table.append(
            f"{latex_text(str(row['zone']))} & {row['active_locations']:,} & "
            f"{row['unique_skus']:,} & {row['units_on_hand']:,} " + r"\\"
        )
    table.append(r"\midrule")
    table.append(
        f"All zones & {len(records):,} & {len({sku for _, sku, _ in records}):,} & "
        f"{sum(quantity for _, _, quantity in records):,} " + r"\\"
    )
    table.extend((r"\bottomrule", r"\end{tabular}"))
    (ARTIFACTS / "zone_table.tex").write_text("\n".join(table) + "\n", encoding="utf-8")

    summary = (
        f"The source contains {len(records):,} active-location records across "
        f"{len(rows)} zones. It records "
        f"{sum(quantity for _, _, quantity in records):,} selling units on hand. "
        "Table~\\ref{tab:zone-summary} summarizes the snapshot by zone.\n"
    )
    (ARTIFACTS / "summary.tex").write_text(summary, encoding="utf-8")
    write_zone_chart(rows, len(records))
    write_settings_table(len(records), len(rows), EXAMPLE_FACTOR)

    metadata = {
        "source_url": sources()["active_locations"]["url"],
        "source_file": path.name,
        "source_sha256": sha256(path),
        "records": len(records),
        "zones": len(rows),
        "xlrd_version": xlrd.__version__,
        "rows": rows,
    }
    (ARTIFACTS / "run.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {ARTIFACTS.relative_to(ROOT) / 'zone_summary.csv'}, chart, and LaTeX inputs")


def write_scenario(records: list[tuple[str, str, int]], factor: Decimal) -> None:
    if factor <= 0:
        raise ValueError("The scenario factor must be greater than zero")
    ARTIFACTS.mkdir(exist_ok=True)
    rows = summarize(records)
    write_settings_table(len(records), len(rows), factor)
    target = ARTIFACTS / "scenario_inventory_factor.csv"
    comparisons: list[tuple[str, int, int, int]] = []
    with target.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            ("zone", "baseline_units", "factor", "illustrative_units", "change_units")
        )
        for row in rows:
            baseline = int(row["units_on_hand"])
            projected = (Decimal(baseline) * factor).to_integral_value(
                rounding=ROUND_CEILING
            )
            change = int(projected) - baseline
            comparisons.append((str(row["zone"]), baseline, int(projected), change))
            writer.writerow((row["zone"], baseline, str(factor), projected, change))

    table = [
        r"\begin{tabular}{@{}l S[table-format=7.0] S[table-format=7.0] r@{}}",
        r"\toprule",
        r"& \multicolumn{2}{c}{Selling units} & \\",
        r"\cmidrule(lr){2-3}",
        r"{Zone} & {Observed} & {Illustrative} & Change \\",
        r"\midrule",
    ]
    for zone, baseline, projected, change in comparisons:
        table.append(
            f"{latex_text(zone)} & {baseline} & {projected} & "
            + rf"\num{{{change}}} \\"
        )
    total_baseline = sum(item[1] for item in comparisons)
    total_projected = sum(item[2] for item in comparisons)
    total_change = total_projected - total_baseline
    relative_change = Decimal(total_change) / Decimal(total_baseline) * 100
    table.extend(
        (
            r"\midrule",
            f"All zones & {total_baseline} & {total_projected} & "
            + rf"\num{{{total_change}}} \\",
            r"\bottomrule",
            r"\end{tabular}",
        )
    )
    (ARTIFACTS / "scenario_table.tex").write_text(
        "\n".join(table) + "\n", encoding="utf-8"
    )
    summary = (
        rf"Applying a factor of \num{{{factor}}} to each zone's observed units "
        rf"produces \num{{{total_projected}}} illustrative units, "
        rf"a change of \num{{{total_change}}} units "
        rf"(\num{{{relative_change:.1f}}}\%) from the snapshot. "
        "The total is the sum of zone values rounded up to whole units. "
        "This arithmetic example does not estimate demand or picking work.\n"
    )
    (ARTIFACTS / "scenario_summary.tex").write_text(summary, encoding="utf-8")
    print(f"Wrote {target.relative_to(ROOT)} (illustrative factor only)")


def build_pdf() -> None:
    command = [
        "latexmk",
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        "-outdir=artifacts",
        "report/main.tex",
    ]
    try:
        subprocess.run(command, cwd=ROOT, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError("latexmk is missing. Use run.cmd or run.sh with Docker.") from exc
    print(f"Built {ARTIFACTS.relative_to(ROOT) / 'main.pdf'}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("all", "data", "scenario"), default="all")
    parser.add_argument(
        "--factor", type=Decimal, default=Decimal("1.10"),
        help="Illustrative inventory multiplier for the scenario command (default: 1.10)",
    )
    args = parser.parse_args()
    try:
        path = ensure_data(include_all=args.command != "scenario")
        if args.command == "data":
            return 0
        records = read_inventory(path)
        if args.command == "scenario":
            write_scenario(records, args.factor)
            return 0
        write_baseline(records, path)
        write_scenario(records, EXAMPLE_FACTOR)
        build_pdf()
        return 0
    except (OSError, ValueError, zipfile.BadZipFile, xlrd.XLRDError, subprocess.CalledProcessError) as exc:
        print(f"Pipeline failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
