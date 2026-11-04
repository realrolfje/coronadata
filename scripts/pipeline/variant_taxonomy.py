from dataclasses import dataclass
from datetime import date as date_type, timedelta
import json
from pathlib import Path


@dataclass(frozen=True)
class VariantTaxonomy:
    version: str
    rules: dict
    sources: tuple[dict, ...]

    def rule(self, code, date=None):
        rule = self.rules.get(code, {})
        if not rule or date is None:
            return rule
        valid_from = rule.get("valid_from")
        valid_until = rule.get("valid_until")
        if valid_from and date < valid_from:
            return {}
        if valid_until and date > valid_until:
            return {}
        return rule


@dataclass(frozen=True)
class ExclusiveVariantWeek:
    date: str
    sample_size: int
    counts: dict[str, int]
    unresolved_parents: tuple[str, ...] = ()

    @property
    def total(self):
        return sum(self.counts.values())

    @property
    def proportions(self):
        return {
            code: count / self.sample_size
            for code, count in self.counts.items()
        }


@dataclass(frozen=True)
class PooledVariantWeek:
    date: str
    sample_size: int
    counts: dict[str, int]

    @property
    def proportions(self):
        return {
            code: count / self.sample_size
            for code, count in self.counts.items()
        }


def pool_exclusive_weeks(weeks, window_weeks=4, minimum_samples=20):
    """Pool independent weekly samples into trailing calendar-week windows."""
    ordered = sorted(weeks, key=lambda week: week.date)
    pooled = []
    for current in ordered:
        current_date = date_type.fromisoformat(current.date)
        first_date = current_date - timedelta(weeks=window_weeks - 1)
        window = [
            week for week in ordered
            if first_date <= date_type.fromisoformat(week.date) <= current_date
        ]
        sample_size = sum(week.sample_size for week in window)
        if sample_size < minimum_samples:
            continue
        counts = {}
        for week in window:
            for code, count in week.counts.items():
                counts[code] = counts.get(code, 0) + count
        pooled.append(PooledVariantWeek(current.date, sample_size, counts))
    return pooled


def load_taxonomy(path: Path) -> VariantTaxonomy:
    value = json.loads(path.read_text())
    if value.get("schema_version") != 1:
        raise ValueError(f"Unsupported variant taxonomy schema in {path}")
    rules = value["rules"]
    for code, rule in rules.items():
        if rule.get("exclude") and rule.get("parent"):
            raise ValueError(f"{code}: taxonomy rule cannot both exclude and reparent")
        valid_from = rule.get("valid_from")
        valid_until = rule.get("valid_until")
        if valid_from and valid_until and valid_from > valid_until:
            raise ValueError(f"{code}: invalid taxonomy validity interval")
    return VariantTaxonomy(
        version=value["taxonomy_version"],
        rules=rules,
        sources=tuple(value["sources"]),
    )


def make_exclusive_week(records, taxonomy: VariantTaxonomy) -> ExclusiveVariantWeek:
    """Turn overlapping RIVM hierarchy counts into mutually exclusive residual counts."""
    dates = {record["Date_of_statistics_week_start"] for record in records}
    if len(dates) != 1:
        raise ValueError("Variant week mixes observation dates")
    date = next(iter(dates))
    records = [
        record for record in records
        if not record.get("May_include_samples_listed_before", False)
        and not taxonomy.rule(record["Variant_code"], date).get("exclude", False)
    ]
    if not records:
        raise ValueError("Variant week contains no usable records")

    sizes = {int(record["Sample_size"]) for record in records}
    if len(sizes) != 1:
        raise ValueError("Variant week mixes sample sizes")
    sample_size = sizes.pop()
    if sample_size <= 0:
        raise ValueError(f"{date}: sample size must be positive")

    nodes = {}
    for record in records:
        code = record["Variant_code"]
        if code in nodes:
            raise ValueError(f"{date}: duplicate variant code {code}")
        rule = taxonomy.rule(code, date)
        nodes[code] = {
            "cases": int(record["Variant_cases"]),
            "parent": rule.get("parent", record.get("Is_subvariant_of", "")),
        }

    children = {code: [] for code in nodes}
    unresolved = []
    for code, node in nodes.items():
        parent = node["parent"]
        if parent in nodes:
            children[parent].append(code)
        elif parent:
            unresolved.append(f"{code}->{parent}")

    counts = {}
    for code, node in nodes.items():
        child_cases = sum(nodes[child]["cases"] for child in children[code])
        residual = node["cases"] - child_cases
        if residual < 0:
            raise ValueError(
                f"{date}: children of {code} contain {child_cases} cases, "
                f"more than parent count {node['cases']}"
            )
        counts[code] = residual

    total = sum(counts.values())
    if total > sample_size:
        raise ValueError(
            f"{date}: exclusive variant total {total} exceeds sample size {sample_size}"
        )
    return ExclusiveVariantWeek(
        date=date,
        sample_size=sample_size,
        counts=counts,
        unresolved_parents=tuple(sorted(unresolved)),
    )
