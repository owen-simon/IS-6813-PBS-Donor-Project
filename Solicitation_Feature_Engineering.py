"""Create four solicitation predictors for the PBS Utah group model.

Run from the folder containing Data_Files:
    python Solicitation_Feature_Engineering.py

Output: Data_Files/solicitation_features.csv
One row per constituent per FY2021–FY2026.
This script does not create targets or use future-year information.
"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parent / "Data_Files"
OUTPUT = DATA / "solicitation_features.csv"
CHUNK_SIZE = 250_000
FIRST_YEAR = 2021
LAST_YEAR = 2026


def fiscal_year(dates):
    """July–June fiscal year, labeled by its ending calendar year."""
    return (dates.dt.year + (dates.dt.month >= 7).astype("int64")).astype("Int64")


def main():
    # Match the constituent universe in the existing analytic dataset.
    constituents = pd.read_csv(
        DATA / "constituents_w_memberships.csv",
        usecols=["Constituent ID"],
        dtype="string",
    )
    ids = constituents["Constituent ID"].dropna().drop_duplicates()
    valid_ids = set(ids)

    # Preserve the original definition: every campaign_members row is
    # one solicitation. A response counts only if its date falls within
    # the fiscal year marked by campaign_start_date.
    parts = []
    for chunk in pd.read_csv(
        DATA / "campaign_members.csv",
        usecols=["constituent_id", "campaign_start_date",
                 "responded", "responded_date"],
        dtype="string",
        chunksize=CHUNK_SIZE,
    ):
        marker = pd.to_datetime(chunk["campaign_start_date"], errors="coerce")
        response_date = pd.to_datetime(chunk["responded_date"], errors="coerce")
        chunk["fiscal_year"] = fiscal_year(marker)

        chunk = chunk.loc[
            chunk["constituent_id"].isin(valid_ids)
            & chunk["fiscal_year"].between(FIRST_YEAR - 2, LAST_YEAR)
        ].copy()

        response_flag = chunk["responded"].str.strip().str.lower().isin(
            ["true", "1", "yes"]
        )
        response_fy = fiscal_year(response_date.loc[chunk.index])
        chunk["valid_response"] = (
            response_flag
            & response_date.loc[chunk.index].notna()
            & response_fy.eq(chunk["fiscal_year"]).fillna(False)
        ).astype("int64")

        parts.append(
            chunk.groupby(["constituent_id", "fiscal_year"], as_index=False)
            .agg(
                solicitations=("valid_response", "size"),
                campaign_responses=("valid_response", "sum"),
            )
        )

    if parts:
        annual = (
            pd.concat(parts, ignore_index=True)
            .groupby(["constituent_id", "fiscal_year"], as_index=False)[
                ["solicitations", "campaign_responses"]
            ]
            .sum()
        )
    else:
        annual = pd.DataFrame(
            columns=["constituent_id", "fiscal_year",
                     "solicitations", "campaign_responses"]
        )

    # Include two history years for correct FY2021 trailing features.
    years = range(FIRST_YEAR - 2, LAST_YEAR + 1)
    panel = pd.MultiIndex.from_product(
        [ids.sort_values(), years],
        names=["constituent_id", "fiscal_year"],
    ).to_frame(index=False)
    panel = panel.merge(
        annual, on=["constituent_id", "fiscal_year"],
        how="left", validate="one_to_one",
    )
    panel[["solicitations", "campaign_responses"]] = (
        panel[["solicitations", "campaign_responses"]].fillna(0).astype("int64")
    )
    panel = panel.sort_values(["constituent_id", "fiscal_year"])
    by_constituent = panel.groupby("constituent_id", sort=False)

    panel["prior_fy_solicitations"] = (
        by_constituent["solicitations"].shift(1).fillna(0).astype("int64")
    )
    panel["trailing_3_fy_solicitations"] = (
        panel["solicitations"]
        + by_constituent["solicitations"].shift(1).fillna(0)
        + by_constituent["solicitations"].shift(2).fillna(0)
    ).astype("int64")
    trailing_responses = (
        panel["campaign_responses"]
        + by_constituent["campaign_responses"].shift(1).fillna(0)
        + by_constituent["campaign_responses"].shift(2).fillna(0)
    )
    panel["trailing_3_fy_response_rate"] = trailing_responses.div(
        panel["trailing_3_fy_solicitations"].where(
            panel["trailing_3_fy_solicitations"] > 0
        )
    )

    result = panel.loc[
        panel["fiscal_year"].between(FIRST_YEAR, LAST_YEAR),
        [
            "constituent_id", "fiscal_year", "trailing_3_fy_solicitations",
            "prior_fy_solicitations", "trailing_3_fy_response_rate",
            "solicitations",
        ],
    ].copy()

    assert not result.duplicated(["constituent_id", "fiscal_year"]).any()
    assert len(result) == len(ids) * (LAST_YEAR - FIRST_YEAR + 1)
    assert (result["prior_fy_solicitations"] >= 0).all()
    assert (result["trailing_3_fy_solicitations"] >= result["solicitations"]).all()
    assert result["trailing_3_fy_response_rate"].dropna().between(0, 1).all()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)
    print(f"Saved {len(result):,} constituent-year rows to {OUTPUT}")


if __name__ == "__main__":
    main()
