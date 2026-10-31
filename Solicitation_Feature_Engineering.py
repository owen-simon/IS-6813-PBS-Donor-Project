"""Build the 15 solicitation predictors used in the PBS Utah XGBoost plot.

Run from the repository root:
    python Solicitation_Feature_Engineering.py

Required files in Data_Files/:
    constituents_w_memberships.csv
    campaign_codes.csv
    campaign_members.csv

Output:
    Data_Files/solicitation_features.csv

One row per constituent and fiscal year (FY2021 through FY2026), with exactly
15 solicitation predictors plus constituent_id and fiscal_year. Source files
are not modified. This is a feature table, not a complete modeling panel.

Interpretation: 'responded' is a payment-based proxy linked by constituent,
marketing code, and fiscal year, not evidence that a solicitation caused a gift.
Campaign start dates are fiscal-year markers rather than actual contact dates.
"""

from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "Data_Files"
OUTPUT = DATA / "solicitation_features.csv"
CHUNK_SIZE = 250_000
START_FY = 2021
END_FY = 2026

FEATURES = [
    "trailing_3_fy_solicitations",
    "campaign_response_rate",
    "solicitations_digital",
    "prior_fy_solicitations",
    "solicitations",
    "trailing_3_fy_response_rate",
    "solicitations_miscellaneous",
    "trailing_3_fy_campaign_responses",
    "unique_campaigns_solicited",
    "campaign_codes_linked",
    "responses_miscellaneous",
    "solicitations_mail",
    "solicitations_email",
    "prior_fy_campaign_responses",
    "campaign_responses",
]


def require_columns(frame: pd.DataFrame, required: set[str], filename: str) -> None:
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{filename}: missing required columns {sorted(missing)}")


def fiscal_year(dates: pd.Series) -> pd.Series:
    """July-June fiscal year, labeled by the ending calendar year."""
    return (dates.dt.year + (dates.dt.month >= 7).astype("int64")).astype("Int64")


def clean_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def as_bool(values: pd.Series) -> pd.Series:
    return values.astype("string").str.strip().str.lower().isin(["true", "1", "yes"])


def load_constituents() -> set[str]:
    path = DATA / "constituents_w_memberships.csv"
    constituents = pd.read_csv(path, usecols=["Constituent ID"], dtype="string")
    require_columns(constituents, {"Constituent ID"}, path.name)
    return set(constituents["Constituent ID"].dropna().unique())


def load_campaign_codes() -> pd.DataFrame:
    path = DATA / "campaign_codes.csv"
    codes = pd.read_csv(path, dtype="string", low_memory=False)
    require_columns(codes, {"Marketing Code", "Communication Method"}, path.name)
    return (
        codes.rename(columns={
            "Marketing Code": "marketing_code",
            "Communication Method": "communication_method",
        })[["marketing_code", "communication_method"]]
        .drop_duplicates("marketing_code")
    )


def aggregate_campaigns(valid_ids: set[str], codes: pd.DataFrame) -> pd.DataFrame:
    """Aggregate campaign-member exposures in bounded-size chunks."""
    path = DATA / "campaign_members.csv"
    required = {
        "constituent_id", "marketing_code", "responded",
        "campaign_start_date", "responded_date",
    }
    pieces = []

    for chunk in pd.read_csv(
        path, dtype="string", usecols=list(required), chunksize=CHUNK_SIZE
    ):
        chunk["campaign_start_date"] = pd.to_datetime(
            chunk["campaign_start_date"], errors="coerce"
        )
        chunk["fiscal_year"] = fiscal_year(chunk["campaign_start_date"])
        usable = chunk["constituent_id"].isin(valid_ids) & chunk["fiscal_year"].notna()
        part = chunk.loc[usable, [
            "constituent_id", "fiscal_year", "marketing_code",
            "responded", "responded_date",
        ]].copy()
        if part.empty:
            continue

        response_date = pd.to_datetime(part["responded_date"], errors="coerce")
        response = as_bool(part["responded"])
        valid_response = (
            response & response_date.notna()
            & fiscal_year(response_date).eq(part["fiscal_year"]).fillna(False)
        )
        part["responded"] = valid_response.astype("int64")

        part = part.merge(codes, on="marketing_code", how="left", validate="many_to_one", indicator=True)
        part["campaign_code_linked"] = part["_merge"].eq("both").astype("int64")

        for method in ["digital", "miscellaneous", "mail", "email"]:
            mask = part["communication_method"].str.lower().eq(method).fillna(False)
            suffix = clean_name(method)
            part[f"solicitations_{suffix}"] = mask.astype("int64")
            if method == "miscellaneous":
                part["responses_miscellaneous"] = (mask & valid_response.to_numpy()).astype("int64")

        # Group by marketing code first, preserving the source's exposure semantics.
        # Each campaign-member row counts as one solicitation; responses count
        # qualifying rows rather than distinct payment events.
        pieces.append(
            part.groupby(
                ["constituent_id", "fiscal_year", "marketing_code"],
                as_index=False, dropna=False,
            ).agg(
                solicitations=("marketing_code", "size"),
                campaign_responses=("responded", "sum"),
                campaign_codes_linked=("campaign_code_linked", "sum"),
                solicitations_digital=("solicitations_digital", "sum"),
                solicitations_miscellaneous=("solicitations_miscellaneous", "sum"),
                responses_miscellaneous=("responses_miscellaneous", "sum"),
                solicitations_mail=("solicitations_mail", "sum"),
                solicitations_email=("solicitations_email", "sum"),
            )
        )

    columns = [
        "constituent_id", "fiscal_year", "solicitations", "campaign_responses",
        "campaign_codes_linked", "solicitations_digital", "solicitations_miscellaneous",
        "responses_miscellaneous", "solicitations_mail", "solicitations_email",
        "unique_campaigns_solicited",
    ]
    if not pieces:
        return pd.DataFrame(columns=columns)

    combined = pd.concat(pieces, ignore_index=True)
    numeric = [c for c in combined.columns if c not in {"constituent_id", "fiscal_year", "marketing_code"}]
    combined = combined.groupby(
        ["constituent_id", "fiscal_year", "marketing_code"],
        as_index=False, dropna=False,
    )[numeric].sum()
    combined["unique_campaigns_solicited"] = combined["marketing_code"].notna().astype("int64")
    return (
        combined.drop(columns="marketing_code")
        .groupby(["constituent_id", "fiscal_year"], as_index=False)
        .sum()
    )


def main() -> None:
    valid_ids = load_constituents()
    codes = load_campaign_codes()
    campaign = aggregate_campaigns(valid_ids, codes)

    # Build a complete panel, including two preceding years for lag calculations.
    # Missing campaign observations are zero-filled, as in the original pipeline.
    years = range(START_FY - 2, END_FY + 1)
    panel = pd.MultiIndex.from_product(
        [sorted(valid_ids), years], names=["constituent_id", "fiscal_year"]
    ).to_frame(index=False)
    panel = panel.merge(campaign, on=["constituent_id", "fiscal_year"], how="left", validate="one_to_one")

    count_columns = [
        "solicitations", "campaign_responses", "campaign_codes_linked",
        "solicitations_digital", "solicitations_miscellaneous",
        "responses_miscellaneous", "solicitations_mail", "solicitations_email",
        "unique_campaigns_solicited",
    ]
    panel[count_columns] = panel[count_columns].fillna(0).astype("int64")

    panel["campaign_response_rate"] = panel["campaign_responses"].div(
        panel["solicitations"].where(panel["solicitations"] > 0)
    )

    panel = panel.sort_values(["constituent_id", "fiscal_year"])
    grouped = panel.groupby("constituent_id", sort=False)
    for column in ["solicitations", "campaign_responses"]:
        panel[f"prior_fy_{column}"] = grouped[column].shift(1).fillna(0)
        panel[f"trailing_3_fy_{column}"] = (
            panel[column] + grouped[column].shift(1).fillna(0)
            + grouped[column].shift(2).fillna(0)
        )

    panel["trailing_3_fy_response_rate"] = panel["trailing_3_fy_campaign_responses"].div(
        panel["trailing_3_fy_solicitations"].where(panel["trailing_3_fy_solicitations"] > 0)
    )

    output = panel.loc[
        panel["fiscal_year"].between(START_FY, END_FY),
        ["constituent_id", "fiscal_year", *FEATURES],
    ].copy()
    assert not output.duplicated(["constituent_id", "fiscal_year"]).any()
    assert len(output) == len(valid_ids) * (END_FY - START_FY + 1)
    assert (output["campaign_responses"] <= output["solicitations"]).all()
    assert len(FEATURES) == 15 and len(set(FEATURES)) == 15
    assert list(output.columns) == ["constituent_id", "fiscal_year", *FEATURES]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(output):,} rows and {len(FEATURES)} predictors to {OUTPUT}")
    print("Note: FY2021 trailing values depend on source coverage before FY2021.")


if __name__ == "__main__":
    main()
