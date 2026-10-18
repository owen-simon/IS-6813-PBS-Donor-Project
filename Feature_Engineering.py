"""Build a constituent-by-fiscal-year analytical dataset for the PBS Utah project.

Run from the repository root:
    python Feature_Engineering.py

Inputs are never modified. The script writes:
  * Data_Files/constituent_fiscal_year_analytic.csv
  * Data_Files/feature_engineering_quality_report.csv

Each output row is one constituent in one fiscal year. Feature columns use
information available in that year or before. `next_fy_*` columns are future
outcomes for model training/evaluation and must not be model inputs.
"""

from __future__ import annotations

from pathlib import Path
import re
import gc

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "Data_Files"
OUTPUT = DATA / "constituent_fiscal_year_analytic.csv"
QUALITY_REPORT = DATA / "feature_engineering_quality_report.csv"
CHUNK_SIZE = 250_000
ANALYTIC_START_FY = 2021
HISTORY_YEARS_NEEDED = 2


def fiscal_year(dates: pd.Series) -> pd.Series:
    """Return the July--June fiscal year labelled by its ending calendar year."""
    return (dates.dt.year + (dates.dt.month >= 7).astype("int64")).astype("Int64")


def clean_name(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")


def as_bool(values: pd.Series) -> pd.Series:
    return values.astype("string").str.strip().str.lower().isin(["true", "1", "yes"])


def report(rows: list[dict], table: str, check: str, affected: int, decision: str) -> None:
    rows.append({"table": table, "check": check, "affected_rows": int(affected), "decision": decision})


def require_columns(frame: pd.DataFrame, columns: set[str], filename: str) -> None:
    missing = columns - set(frame.columns)
    if missing:
        raise ValueError(f"{filename} is missing required columns: {sorted(missing)}")


def read_csv(name: str, **kwargs) -> pd.DataFrame:
    path = DATA / name
    if not path.exists():
        raise FileNotFoundError(f"Required input is missing: {path}")
    return pd.read_csv(path, low_memory=False, **kwargs)


def aggregate_campaign_members(valid_ids: set[str], campaign_codes: pd.DataFrame, quality: list[dict]) -> pd.DataFrame:
    """Aggregate solicitation exposure/responses in chunks to keep memory bounded."""
    path = DATA / "campaign_members.csv"
    required = {"constituent_id", "marketing_code", "responded", "campaign_start_date"}
    pieces = []
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, dtype="string", low_memory=False):
        require_columns(chunk, required, path.name)
        chunk["campaign_start_date"] = pd.to_datetime(chunk["campaign_start_date"], errors="coerce")
        chunk["fiscal_year"] = fiscal_year(chunk["campaign_start_date"])
        linked = chunk["constituent_id"].isin(valid_ids)
        usable = linked & chunk["fiscal_year"].notna()
        report(quality, "campaign_members", "unlinked constituent IDs", (~linked).sum(), "Excluded from constituent features")
        report(quality, "campaign_members", "invalid/missing fiscal-year marker", (linked & chunk["fiscal_year"].isna()).sum(), "Excluded from annual features")
        part = chunk.loc[usable, ["constituent_id", "marketing_code", "responded", "fiscal_year"]].copy()
        part["responded"] = as_bool(part["responded"])
        part = part.merge(campaign_codes, on="marketing_code", how="left")
        part["campaign_code_linked"] = part["communication_method"].notna()
        pieces.append(part.groupby(["constituent_id", "fiscal_year"], as_index=False).agg(
            solicitations=("marketing_code", "size"),
            unique_campaigns_solicited=("marketing_code", "nunique"),
            campaign_responses=("responded", "sum"),
            campaign_code_link_rate=("campaign_code_linked", "mean"),
        ))
    combined = pd.concat(pieces, ignore_index=True)
    return combined.groupby(["constituent_id", "fiscal_year"], as_index=False).sum()


def main() -> None:
    quality: list[dict] = []

    constituents = read_csv("constituents_w_memberships.csv", dtype="string")
    require_columns(constituents, {"Constituent ID"}, "constituents_w_memberships.csv")
    constituents = constituents.rename(columns={"Constituent ID": "constituent_id"})
    duplicate_constituents = constituents.duplicated("constituent_id", keep="first").sum()
    constituents = constituents.dropna(subset=["constituent_id"]).drop_duplicates("constituent_id").copy()
    valid_ids = set(constituents["constituent_id"])
    report(quality, "constituents", "duplicate constituent IDs", duplicate_constituents, "Kept one row per constituent")

    # These fields describe the end of the release, per the dictionary. They
    # remain useful dashboard context but are visibly marked as snapshots.
    snapshot_keep = [
        "constituent_id", "Address State", "Gender", "Age", "Sustainer PBS Utah",
        "Major Donor Class PBS Utah", "Annual Giving Group", "Primary Constituent Type",
        "Has UofU Legacy Gift", "Legacy Circle Member PBS Utah",
        "Lifetime UofU Fundraising", "Previous FY UofU Cash",
        "Prospect Committed Giving Amount UofU",
    ]
    snapshot = constituents[[c for c in snapshot_keep if c in constituents]].copy()
    snapshot = snapshot.rename(columns={c: f"{clean_name(c)}_snapshot" for c in snapshot.columns if c != "constituent_id"})

    campaign_codes = read_csv("campaign_codes.csv", dtype="string")
    require_columns(campaign_codes, {"Marketing Code", "Communication Method"}, "campaign_codes.csv")
    campaign_codes = (campaign_codes.rename(columns={"Marketing Code": "marketing_code", "Communication Method": "communication_method"})
                      [["marketing_code", "communication_method"]].drop_duplicates("marketing_code"))

    # Unite: repeated opportunity IDs are copy candidates in this synthetic
    # release. Validity is determined from link, amount, and date--never ID text.
    unite = read_csv(
        "unite_payments.csv",
        dtype="string",
        usecols=["donor_id", "credit_date", "payment_amount", "payment_id", "opportunity_id", "pledge_gift_type"],
    )
    require_columns(unite, {"donor_id", "credit_date", "payment_amount", "payment_id", "opportunity_id"}, "unite_payments.csv")
    unite["payment_amount"] = pd.to_numeric(unite["payment_amount"], errors="coerce")
    unite["payment_date"] = pd.to_datetime(unite["credit_date"], errors="coerce")
    unite["linked_constituent"] = unite["donor_id"].isin(valid_ids)
    unite["usable"] = unite["linked_constituent"] & unite["payment_amount"].gt(0) & unite["payment_date"].notna()
    report(quality, "unite_payments", "unlinked donor IDs", (~unite["linked_constituent"]).sum(), "Excluded from giving")
    report(quality, "unite_payments", "nonpositive/missing payment amounts", (~unite["payment_amount"].gt(0)).sum(), "Excluded from giving")
    report(quality, "unite_payments", "invalid/missing payment dates", unite["payment_date"].isna().sum(), "Excluded from giving")
    unite = unite.sort_values(["opportunity_id", "usable", "payment_amount"], ascending=[True, False, False])
    copy_candidates = unite.duplicated("opportunity_id", keep="first")
    report(quality, "unite_payments", "repeated opportunity IDs", copy_candidates.sum(), "Kept best valid record per opportunity ID")
    unite = unite.loc[~copy_candidates & unite["usable"]].copy()
    unite_events = pd.DataFrame({
        "constituent_id": unite["donor_id"], "fiscal_year": fiscal_year(unite["payment_date"]),
        "direct_payment_amount": unite["payment_amount"], "direct_payment_count": 1,
        "soft_credit_amount": 0.0, "soft_credit_count": 0,
        "recurring_payment_count": unite.get("pledge_gift_type", pd.Series("", index=unite.index)).eq("Recurring").astype(int),
    })
    del unite
    gc.collect()

    # Legacy rows are household gifts. Credit the full historical household gift
    # to each linked household member; do not use resulting totals as station revenue.
    id_columns = [f"constituent_id_{n}" for n in range(1, 8)]
    legacy = read_csv(
        "team_approach_legacy_payments.csv",
        dtype="string",
        usecols=["source_code", "gift_date", "payment_amount", *id_columns],
    )
    require_columns(legacy, {"source_code", "gift_date", "payment_amount", *id_columns}, "team_approach_legacy_payments.csv")
    legacy["payment_amount"] = pd.to_numeric(legacy["payment_amount"], errors="coerce")
    legacy["payment_date"] = pd.to_datetime(legacy["gift_date"], errors="coerce")
    # `melt` would materialize seven rows per household, most of them blank.
    # Build only populated member links instead.
    legacy_parts = []
    for member_column in id_columns:
        part = legacy.loc[legacy[member_column].notna(), ["source_code", "payment_amount", "payment_date", member_column]].copy()
        part = part.rename(columns={member_column: "constituent_id"})
        legacy_parts.append(part)
    long_legacy = pd.concat(legacy_parts, ignore_index=True)
    del legacy_parts
    long_legacy["linked_constituent"] = long_legacy["constituent_id"].isin(valid_ids)
    long_legacy["usable"] = long_legacy["linked_constituent"] & long_legacy["payment_amount"].gt(0) & long_legacy["payment_date"].notna()
    report(quality, "team_approach_legacy_payments", "unlinked household member IDs", (~long_legacy["linked_constituent"]).sum(), "Excluded from giving")
    report(quality, "team_approach_legacy_payments", "nonpositive/missing payment amounts", (~long_legacy["payment_amount"].gt(0)).sum(), "Excluded from giving")
    # Only for this synthetic release: the dictionary says source_code maps to a
    # single payment, so repeats are documented copy candidates.
    source_quality = long_legacy.groupby("source_code", as_index=False)["usable"].max()
    report(quality, "team_approach_legacy_payments", "repeated source codes", legacy["source_code"].duplicated(keep="first").sum(), "Synthetic-release copy check; kept one source-code event")
    keep_sources = set(source_quality.loc[source_quality["usable"], "source_code"])
    long_legacy = long_legacy.loc[long_legacy["usable"] & long_legacy["source_code"].isin(keep_sources)].drop_duplicates(["source_code", "constituent_id"])
    legacy_events = pd.DataFrame({
        "constituent_id": long_legacy["constituent_id"], "fiscal_year": fiscal_year(long_legacy["payment_date"]),
        "direct_payment_amount": long_legacy["payment_amount"], "direct_payment_count": 1,
        "soft_credit_amount": 0.0, "soft_credit_count": 0, "recurring_payment_count": 0,
    })
    del legacy, long_legacy, source_quality
    gc.collect()

    soft = read_csv("soft_credits.csv", dtype="string")
    require_columns(soft, {"Credit ID", "Soft Credit Constituent ID", "Credit Amount", "Credit Date"}, "soft_credits.csv")
    soft["Credit Amount"] = pd.to_numeric(soft["Credit Amount"], errors="coerce")
    soft["Credit Date"] = pd.to_datetime(soft["Credit Date"], errors="coerce")
    soft["linked_constituent"] = soft["Soft Credit Constituent ID"].isin(valid_ids)
    soft["usable"] = soft["linked_constituent"] & soft["Credit Amount"].gt(0) & soft["Credit Date"].notna()
    report(quality, "soft_credits", "unlinked recipient IDs", (~soft["linked_constituent"]).sum(), "Excluded from giving")
    report(quality, "soft_credits", "nonpositive/missing credit amounts", (~soft["Credit Amount"].gt(0)).sum(), "Excluded from giving")
    duplicate_soft = soft.loc[soft["usable"]].duplicated().sum()
    soft = soft.loc[soft["usable"]].drop_duplicates().copy()
    report(quality, "soft_credits", "exact duplicate usable rows", duplicate_soft, "Exact duplicates removed")
    soft_events = pd.DataFrame({
        "constituent_id": soft["Soft Credit Constituent ID"], "fiscal_year": fiscal_year(soft["Credit Date"]),
        "direct_payment_amount": 0.0, "direct_payment_count": 0,
        "soft_credit_amount": soft["Credit Amount"], "soft_credit_count": 1, "recurring_payment_count": 0,
    })

    events = pd.concat([unite_events, legacy_events, soft_events], ignore_index=True)
    giving = events.groupby(["constituent_id", "fiscal_year"], as_index=False).sum()
    giving["annual_giving"] = giving["direct_payment_amount"] + giving["soft_credit_amount"]
    del events, unite_events, legacy_events, soft_events, soft
    gc.collect()

    campaign = aggregate_campaign_members(valid_ids, campaign_codes, quality)

    passport_name = "passport_engagement_by_genre.csv" if (DATA / "passport_engagement_by_genre.csv").exists() else "passport_viewing.txt"
    passport = read_csv(passport_name, dtype={"constituent_id": "string"})
    require_columns(passport, {"constituent_id", "fiscal_year", "genre", "titles_viewed", "mean_percent_watched"}, passport_name)
    passport["fiscal_year"] = pd.to_numeric(passport["fiscal_year"], errors="coerce").astype("Int64")
    passport["titles_viewed"] = pd.to_numeric(passport["titles_viewed"], errors="coerce")
    passport["mean_percent_watched"] = pd.to_numeric(passport["mean_percent_watched"], errors="coerce")
    passport = passport.loc[passport["constituent_id"].isin(valid_ids) & passport["fiscal_year"].notna()]
    viewing = passport.groupby(["constituent_id", "fiscal_year"], as_index=False).agg(
        passport_titles_viewed=("titles_viewed", "sum"), passport_genres_viewed=("genre", "nunique"),
        passport_mean_percent_watched=("mean_percent_watched", "mean"),
    )

    cultivation = read_csv("cultivation.csv", dtype="string")
    require_columns(cultivation, {"synthetic_id", "fiscal_year", "selected", "contacted", "holdout", "program_adopted"}, "cultivation.csv")
    cultivation["fiscal_year"] = pd.to_numeric(cultivation["fiscal_year"], errors="coerce").astype("Int64")
    cultivation = cultivation.rename(columns={"synthetic_id": "constituent_id"})
    cultivation = cultivation.loc[cultivation["constituent_id"].isin(valid_ids) & cultivation["fiscal_year"].notna()].copy()
    for column in ["selected", "contacted", "holdout", "program_adopted"]:
        cultivation[column] = as_bool(cultivation[column]).astype("int8")
    cultivation = cultivation.groupby(["constituent_id", "fiscal_year"], as_index=False)[["selected", "contacted", "holdout", "program_adopted"]].max()
    cultivation = cultivation.rename(columns={c: f"cultivation_{c}" for c in cultivation.columns if c not in {"constituent_id", "fiscal_year"}})

    # Unite/campaign data begin in FY2021.  Retain two earlier years only to
    # calculate time-safe trailing features, then remove them from the output.
    earliest_panel_fy = ANALYTIC_START_FY - HISTORY_YEARS_NEEDED
    years = [year for year in sorted(set(giving["fiscal_year"].dropna()) | set(campaign["fiscal_year"].dropna()) | set(viewing["fiscal_year"].dropna())) if year >= earliest_panel_fy]
    panel = pd.MultiIndex.from_product([sorted(valid_ids), years], names=["constituent_id", "fiscal_year"]).to_frame(index=False)
    for frame in [giving, campaign, viewing, cultivation]:
        panel = panel.merge(frame, on=["constituent_id", "fiscal_year"], how="left", validate="one_to_one")
    panel = panel.merge(snapshot, on="constituent_id", how="left", validate="many_to_one")

    for column in ["direct_payment_amount", "direct_payment_count", "soft_credit_amount", "soft_credit_count", "recurring_payment_count", "solicitations", "unique_campaigns_solicited", "campaign_responses", "passport_titles_viewed", "passport_genres_viewed"]:
        if column in panel:
            panel[column] = panel[column].fillna(0)
    panel["annual_giving"] = panel["direct_payment_amount"] + panel["soft_credit_amount"]
    panel["gave_this_fy"] = (panel["annual_giving"] > 0).astype("int8")
    panel["campaign_response_rate"] = panel["campaign_responses"].div(panel["solicitations"].where(panel["solicitations"] > 0))
    panel["passport_data_present"] = panel["passport_mean_percent_watched"].notna().astype("int8")

    panel = panel.sort_values(["constituent_id", "fiscal_year"])
    grouped = panel.groupby("constituent_id", sort=False)
    panel["prior_fy_giving"] = grouped["annual_giving"].shift(1).fillna(0)
    panel["two_fy_prior_giving"] = grouped["annual_giving"].shift(2).fillna(0)
    panel["giving_trend_vs_prior_fy"] = panel["annual_giving"] - panel["prior_fy_giving"]
    panel["trailing_3_fy_giving"] = grouped["annual_giving"].transform(lambda s: s.rolling(3, min_periods=1).sum())
    panel["trailing_3_fy_gift_count"] = grouped["direct_payment_count"].transform(lambda s: s.rolling(3, min_periods=1).sum())
    panel["next_fy_giving"] = grouped["annual_giving"].shift(-1)
    panel["next_fy_reached_2000"] = (panel["next_fy_giving"] >= 2000).astype("Int64")
    panel.loc[panel["next_fy_giving"].isna(), "next_fy_reached_2000"] = pd.NA
    panel["next_fy_giving_growth"] = panel["next_fy_giving"] - panel["annual_giving"]

    panel = panel.loc[panel["fiscal_year"] >= ANALYTIC_START_FY].copy()

    panel.to_csv(OUTPUT, index=False)
    pd.DataFrame(quality).groupby(["table", "check", "decision"], as_index=False)["affected_rows"].sum().to_csv(QUALITY_REPORT, index=False)
    print(f"Wrote {len(panel):,} rows to {OUTPUT}")
    print(f"Wrote data-quality report to {QUALITY_REPORT}")


if __name__ == "__main__":
    main()
