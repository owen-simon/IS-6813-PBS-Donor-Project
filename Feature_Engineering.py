# ======================================================
# Import libraries
# ======================================================

import re
import pandas as pd


# ======================================================
# Helper functions
# ======================================================

def clean_column_name(value):
    """
    Convert dynamically generated values into clean column names.

    Example:
        "Board Member/Trustee" -> "board_member_trustee"
    """
    value = str(value).strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)

    return value.strip("_")


# ======================================================
# Load datasets
# ======================================================

constit_acquisition_scores = pd.read_csv(
    "Data_Files/constituents_w_acquisition_scores.csv"
)

constit_affiliations = pd.read_csv(
    "Data_Files/constituents_w_affiliations.csv"
)

constit_capacity_ratings = pd.read_csv(
    "Data_Files/constituents_w_capacity_ratings.csv"
)

constit_engagement_scores = pd.read_csv(
    "Data_Files/constituents_w_engagement_scores.csv"
)

constit_involvements = pd.read_csv(
    "Data_Files/constituents_w_involvements.csv"
)

constit_memberships = pd.read_csv(
    "Data_Files/constituents_w_memberships.csv"
)

passport_viewing_data = pd.read_csv(
    "Data_Files/passport_viewing_data.csv"
)

soft_credits_from_orgs = pd.read_csv(
    "Data_Files/soft_credits_from_orgs.csv"
)

#-------------------------------------------------------
# Team Approach contains exact duplicate source rows.
# Remove only completely identical records before
# creating a unique analysis-level payment ID.
team_approach_legacy_payments = pd.read_csv(
    "Data_Files/team_approach_legacy_payments.csv"
)

team_approach_legacy_payments = (
    team_approach_legacy_payments
    .drop_duplicates()
    .reset_index(drop=True)
)

team_approach_legacy_payments["ta_payment_id"] = (
    "TA_"
    + team_approach_legacy_payments.index.astype(str)
)
#-------------------------------------------------------

unite_giftpremiums = pd.read_csv(
    "Data_Files/unite_giftpremiums.csv"
)

unite_payments = pd.read_csv(
    "Data_Files/unite_payments.csv"
)


# ======================================================
# Prepare Unite Payments
# ======================================================

# ------------------------------------------------------
# 1) Clean payment variables
# ------------------------------------------------------

unite_payments["payment_amount"] = pd.to_numeric(
    unite_payments["payment_amount"],
    errors="coerce"
)

unite_payments["credit_date"] = pd.to_datetime(
    unite_payments["credit_date"],
    errors="coerce"
)

unite_payments["donor_id"] = pd.to_numeric(
    unite_payments["donor_id"],
    errors="coerce"
)

assert unite_payments["payment_id"].is_unique


# ------------------------------------------------------
# 2) Standardize Unite payment variables
# ------------------------------------------------------

unite_standardized = pd.DataFrame({
    "Constituent ID":
        unite_payments["donor_id"],

    "payment_record_id":
        unite_payments["payment_id"].astype("string"),

    "payment_source":
        "Unite",

    "payment_date":
        unite_payments["credit_date"],

    "payment_amount":
        unite_payments["payment_amount"],

    "payment_method":
        unite_payments["tender_type"],

    "pledge_gift_type":
        unite_payments["pledge_gift_type"],

    "gift_type":
        unite_payments["gift_type"],

    "campaign_code":
        unite_payments["marketing_code"],

    "campaign_name":
        unite_payments["campaign_name"]
})


# ======================================================
# Prepare Team Approach Legacy Payments
# ======================================================

# ------------------------------------------------------
# 1) Clean Team Approach variables
# ------------------------------------------------------

team_approach_legacy_payments["payment_amount"] = pd.to_numeric(
    team_approach_legacy_payments["payment_amount"],
    errors="coerce"
)

team_approach_legacy_payments["gift_date"] = pd.to_datetime(
    team_approach_legacy_payments["gift_date"],
    errors="coerce"
)


# ------------------------------------------------------
# 2) Prepare possible Unite constituent matches
# ------------------------------------------------------

ta_constituent_columns = [
    "constituent_id_1",
    "constituent_id_2",
    "constituent_id_3",
    "constituent_id_4",
    "constituent_id_5",
    "constituent_id_6",
    "constituent_id_7"
]

for col in ta_constituent_columns:
    team_approach_legacy_payments[col] = pd.to_numeric(
        team_approach_legacy_payments[col],
        errors="coerce"
    )


# ------------------------------------------------------
# 3) Count possible constituent matches
# ------------------------------------------------------

team_approach_legacy_payments["ta_match_count"] = (
    team_approach_legacy_payments[
        ta_constituent_columns
    ]
    .notna()
    .sum(axis=1)
)


# ------------------------------------------------------
# 4) Separate Team Approach records by match status
# ------------------------------------------------------

# Exactly one possible constituent match
ta_unique_matches = (
    team_approach_legacy_payments[
        team_approach_legacy_payments["ta_match_count"] == 1
    ]
    .copy()
)

# More than one possible constituent match
ta_multiple_matches = (
    team_approach_legacy_payments[
        team_approach_legacy_payments["ta_match_count"] > 1
    ]
    .copy()
)

# No possible constituent match
ta_unmatched = (
    team_approach_legacy_payments[
        team_approach_legacy_payments["ta_match_count"] == 0
    ]
    .copy()
)


# ------------------------------------------------------
# 5) Assign Constituent ID to uniquely matched records
# ------------------------------------------------------
#
# Because the match fields are nested, any record with
# exactly one match has that match in constituent_id_1.
# ------------------------------------------------------

ta_unique_matches["Constituent ID"] = (
    ta_unique_matches["constituent_id_1"]
    .astype("Int64")
)


# ------------------------------------------------------
# 6) Harmonize Team Approach values with Unite
# ------------------------------------------------------

ta_unique_matches["gift_kind_standardized"] = (
    ta_unique_matches["gift_kind"]
    .replace({
        "Sustaining": "Recurring",
        "Installment": "Standard"
    })
)

ta_unique_matches["payment_method_standardized"] = (
    ta_unique_matches["payment_method"]
    .replace({
        "Charge Card": "Credit Card",
        "Payroll Deduct": "Payroll Deduction",
        "Stock": "Stock Gift",
        "Money Order": "Check"
    })
)


# ------------------------------------------------------
# 7) Standardize Team Approach payment variables
# ------------------------------------------------------

ta_standardized = pd.DataFrame({
    "Constituent ID":
        ta_unique_matches["Constituent ID"],

    "payment_record_id":
        ta_unique_matches["ta_payment_id"],

    "payment_source":
        "Team Approach",

    "payment_date":
        ta_unique_matches["gift_date"],

    "payment_amount":
        ta_unique_matches["payment_amount"],

    "payment_method":
        ta_unique_matches[
            "payment_method_standardized"
        ],

    "pledge_gift_type":
        ta_unique_matches[
            "gift_kind_standardized"
        ],

    "gift_type":
        ta_unique_matches["gift_type"],

    "campaign_code":
        ta_unique_matches["source_code"],

    "campaign_name":
        ta_unique_matches["source_description"]
})

# ------------------------------------------------------
# 8) Validate `ta_standardized` creation
# ------------------------------------------------------
assert ta_standardized["payment_record_id"].is_unique

print(
    "Team Approach standardized payments:",
    f"{len(ta_standardized):,}"
)

print(
    "Unique Team Approach payment IDs:",
    f"{ta_standardized['payment_record_id'].nunique():,}"
)

assert (
    len(ta_unique_matches)
    == ta_standardized["payment_record_id"].nunique()
)

# ======================================================
# Combine Unite and Team Approach Payment Histories
# ======================================================

all_payments = pd.concat(
    [
        unite_standardized,
        ta_standardized
    ],
    ignore_index=True
)

# Only records that can be matched to a constituent
all_payments = (
    all_payments
    .dropna(subset=["Constituent ID"])
    .copy()
)

all_payments["Constituent ID"] = (
    pd.to_numeric(
        all_payments["Constituent ID"],
        errors="coerce"
    )
    .astype("Int64")
)


# ------------------------------------------------------
# Create calendar year
# ------------------------------------------------------

all_payments["year"] = (
    all_payments["payment_date"]
    .dt.year
    .astype("Int64")
)

# ------------------------------------------------------
# Validate combined payment sources
# ------------------------------------------------------

print("\nPayment source validation")

print(
    all_payments
    .groupby("payment_source")
    .agg(
        records=("payment_record_id", "count"),
        unique_records=("payment_record_id", "nunique"),
        first_date=("payment_date", "min"),
        last_date=("payment_date", "max"),
        total_amount=("payment_amount", "sum")
    )
)

# ======================================================
# Aggregate Combined Payment History by Constituent
# ======================================================

# ------------------------------------------------------
# 1) Overall payment features
# ------------------------------------------------------

payment_features = (
    all_payments
    .groupby("Constituent ID")
    .agg(
        total_giving=(
            "payment_amount",
            "sum"
        ),
        number_of_payments=(
            "payment_record_id",
            "nunique"
        ),
        average_payment=(
            "payment_amount",
            "mean"
        ),
        median_payment=(
            "payment_amount",
            "median"
        ),
        largest_payment=(
            "payment_amount",
            "max"
        ),
        first_gift_date=(
            "payment_date",
            "min"
        ),
        most_recent_gift_date=(
            "payment_date",
            "max"
        ),
        unique_campaigns=(
            "campaign_code",
            "nunique"
        )
    )
    .reset_index()
)


# ------------------------------------------------------
# 2) Giving by source
# ------------------------------------------------------

giving_by_source = (
    all_payments
    .pivot_table(
        index="Constituent ID",
        columns="payment_source",
        values="payment_amount",
        aggfunc="sum",
        fill_value=0
    )
)

giving_by_source.columns = [
    "total_giving_" + clean_column_name(col)
    for col in giving_by_source.columns
]

giving_by_source = giving_by_source.reset_index()


# ------------------------------------------------------
# 3) Payment count by source
# ------------------------------------------------------

payments_by_source = (
    all_payments
    .pivot_table(
        index="Constituent ID",
        columns="payment_source",
        values="payment_record_id",
        aggfunc="nunique",
        fill_value=0
    )
)

payments_by_source.columns = [
    "payment_count_" + clean_column_name(col)
    for col in payments_by_source.columns
]

payments_by_source = payments_by_source.reset_index()


# ------------------------------------------------------
# 4) Annual giving
# ------------------------------------------------------

annual_giving = (
    all_payments
    .pivot_table(
        index="Constituent ID",
        columns="year",
        values="payment_amount",
        aggfunc="sum",
        fill_value=0
    )
)

annual_giving.columns = [
    f"total_giving_{int(col)}"
    for col in annual_giving.columns
]

annual_giving = annual_giving.reset_index()

# ------------------------------------------------------
# 5) Annual payment count
# ------------------------------------------------------

annual_payment_counts = (
    all_payments
    .pivot_table(
        index="Constituent ID",
        columns="year",
        values="payment_record_id",
        aggfunc="nunique",
        fill_value=0
    )
)

annual_payment_counts.columns = [
    f"payment_count_{int(col)}"
    for col in annual_payment_counts.columns
]

annual_payment_counts = annual_payment_counts.reset_index()


# ------------------------------------------------------
# 6) Combine payment features
# ------------------------------------------------------

payment_features = (
    payment_features
    .merge(
        giving_by_source,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )
    .merge(
        payments_by_source,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )
    .merge(
        annual_giving,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )
    .merge(
        annual_payment_counts,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )
)


# ======================================================
# Aggregate Unite Gift Premiums
# ======================================================

premium_numeric_columns = [
    "Fair Market Value",
    "Unit Cost"
]

for col in premium_numeric_columns:
    unite_giftpremiums[col] = pd.to_numeric(
        unite_giftpremiums[col],
        errors="coerce"
    )


premium_features = (
    unite_giftpremiums
    .groupby("Constituent ID")
    .agg(
        number_of_premiums=(
            "Code",
            "count"
        ),
        unique_premiums=(
            "Code",
            "nunique"
        ),
        premium_record_count=(
            "Record ID",
            "nunique"
        ),
        total_premium_fmv=(
            "Fair Market Value",
            "sum"
        ),
        average_premium_fmv=(
            "Fair Market Value",
            "mean"
        ),
        total_premium_cost=(
            "Unit Cost",
            "sum"
        ),
        average_premium_cost=(
            "Unit Cost",
            "mean"
        )
    )
    .reset_index()
)


# ======================================================
# Combine Payments and Gift Premiums
# ======================================================

constit_payments_and_gifts = (
    payment_features
    .merge(
        premium_features,
        on="Constituent ID",
        how="outer",
        validate="one_to_one"
    )
)

# ======================================================
# Aggregate Organization Soft Credits by Constituent
# ======================================================

# ------------------------------------------------------
# 1) Prepare soft credit variables
# ------------------------------------------------------

soft_credits_from_orgs["Soft Credit Constituent ID"] = (
    pd.to_numeric(
        soft_credits_from_orgs["Soft Credit Constituent ID"],
        errors="coerce"
    )
    .astype("Int64")
)

soft_credits_from_orgs["Hard Credit Org ID"] = (
    pd.to_numeric(
        soft_credits_from_orgs["Hard Credit Org ID"],
        errors="coerce"
    )
    .astype("Int64")
)

soft_credits_from_orgs["Credit Amount"] = (
    pd.to_numeric(
        soft_credits_from_orgs["Credit Amount"],
        errors="coerce"
    )
)

soft_credits_from_orgs["Credit Date"] = (
    pd.to_datetime(
        soft_credits_from_orgs["Credit Date"],
        errors="coerce"
    )
)

# ------------------------------------------------------
# 2) Keep linked records and collapse duplicate
#    soft-credit rows
# ------------------------------------------------------

soft_credit_linked = (
    soft_credits_from_orgs
    .dropna(
        subset=["Soft Credit Constituent ID"]
    )
    .copy()
)


# One Credit ID may appear on multiple source rows.
# Treat each Credit ID + soft-credit constituent
# combination as one soft-credit event.
soft_credit_linked = (
    soft_credit_linked
    .sort_values(
        "Credit Amount",
        ascending=False
    )
    .drop_duplicates(
        subset=[
            "Credit ID",
            "Soft Credit Constituent ID"
        ],
        keep="first"
    )
    .reset_index(drop=True)
)

assert not soft_credit_linked.duplicated(
    subset=[
        "Credit ID",
        "Soft Credit Constituent ID"
    ]
).any()


# ------------------------------------------------------
# 3) Aggregate overall soft credit features
# ------------------------------------------------------

soft_credit_features = (
    soft_credit_linked
    .groupby("Soft Credit Constituent ID")
    .agg(
        number_of_soft_credits=(
            "Credit ID",
            "nunique"
        ),

        total_soft_credit_amount=(
            "Credit Amount",
            "sum"
        ),

        average_soft_credit_amount=(
            "Credit Amount",
            "mean"
        ),

        median_soft_credit_amount=(
            "Credit Amount",
            "median"
        ),

        largest_soft_credit_amount=(
            "Credit Amount",
            "max"
        ),

        unique_hard_credit_orgs=(
            "Hard Credit Org ID",
            "nunique"
        ),

        unique_soft_credit_gift_types=(
            "Credit Gift Type",
            "nunique"
        ),

        first_soft_credit_date=(
            "Credit Date",
            "min"
        ),

        most_recent_soft_credit_date=(
            "Credit Date",
            "max"
        )
    )
    .reset_index()
    .rename(
        columns={
            "Soft Credit Constituent ID":
                "Constituent ID"
        }
    )
)


# ------------------------------------------------------
# 4) Soft credit counts by Credit Type
# ------------------------------------------------------

soft_credit_type_counts = (
    soft_credit_linked
    .pivot_table(
        index="Soft Credit Constituent ID",
        columns="Credit Type",
        values="Credit ID",
        aggfunc="nunique",
        fill_value=0
    )
)

soft_credit_type_counts.columns = [
    "soft_credit_type_" + clean_column_name(col)
    for col in soft_credit_type_counts.columns
]

soft_credit_type_counts = (
    soft_credit_type_counts
    .reset_index()
    .rename(
        columns={
            "Soft Credit Constituent ID":
                "Constituent ID"
        }
    )
)


# ------------------------------------------------------
# 5) Soft credit counts by Gift Type
# ------------------------------------------------------

soft_credit_gift_type_counts = (
    soft_credit_linked
    .pivot_table(
        index="Soft Credit Constituent ID",
        columns="Credit Gift Type",
        values="Credit ID",
        aggfunc="nunique",
        fill_value=0
    )
)

soft_credit_gift_type_counts.columns = [
    "soft_credit_gift_type_" + clean_column_name(col)
    for col in soft_credit_gift_type_counts.columns
]

soft_credit_gift_type_counts = (
    soft_credit_gift_type_counts
    .reset_index()
    .rename(
        columns={
            "Soft Credit Constituent ID":
                "Constituent ID"
        }
    )
)


# ------------------------------------------------------
# 6) Combine soft credit features
# ------------------------------------------------------

soft_credit_features = (
    soft_credit_features
    .merge(
        soft_credit_type_counts,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )
    .merge(
        soft_credit_gift_type_counts,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )
)

# ======================================================
# Aggregate Affiliations by Constituent
# ======================================================

constit_affiliations["Active"] = (
    constit_affiliations["Active"]
    .replace({
        "TRUE": True,
        "FALSE": False,
        "True": True,
        "False": False,
        1: True,
        0: False
    })
    .astype("boolean")
)


affiliation_features = (
    constit_affiliations
    .groupby("Constituent ID")
    .agg(
        number_of_affiliations=(
            "Record ID",
            "nunique"
        ),
        number_of_active_affiliations=(
            "Active",
            "sum"
        )
    )
    .reset_index()
)


affiliation_role_counts = (
    constit_affiliations
    .pivot_table(
        index="Constituent ID",
        columns="Constituent Role",
        values="Record ID",
        aggfunc="nunique",
        fill_value=0
    )
)

affiliation_role_counts.columns = [
    "affiliation_" + clean_column_name(col)
    for col in affiliation_role_counts.columns
]

affiliation_role_counts = (
    affiliation_role_counts
    .reset_index()
)


affiliation_features = (
    affiliation_features
    .merge(
        affiliation_role_counts,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )
)


# ======================================================
# Aggregate Involvements by Constituent
# ======================================================

involvement_features = (
    constit_involvements
    .groupby("Constituent ID")
    .agg(
        number_of_involvements=(
            "Record ID",
            "nunique"
        ),
        unique_involvement_types=(
            "Involvement: Type",
            "nunique"
        )
    )
    .reset_index()
)


involvement_type_counts = (
    constit_involvements
    .pivot_table(
        index="Constituent ID",
        columns="Involvement: Type",
        values="Record ID",
        aggfunc="nunique",
        fill_value=0
    )
)

involvement_type_counts.columns = [
    "involvement_" + clean_column_name(col)
    for col in involvement_type_counts.columns
]

involvement_type_counts = (
    involvement_type_counts
    .reset_index()
)


involvement_features = (
    involvement_features
    .merge(
        involvement_type_counts,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )
)


# ======================================================
# Aggregate Passport Viewing Data by Constituent
# ======================================================

# ------------------------------------------------------
# 1) Prepare Passport variables
# ------------------------------------------------------

passport_viewing_data["Constituent.ID"] = pd.to_numeric(
    passport_viewing_data["Constituent.ID"],
    errors="coerce"
)

passport_viewing_data["Date.Watched"] = pd.to_datetime(
    passport_viewing_data["Date.Watched"],
    errors="coerce"
)

passport_viewing_data["Percent.Watched"] = pd.to_numeric(
    passport_viewing_data["Percent.Watched"],
    errors="coerce"
)

# ------------------------------------------------------
# 2) Keep linkable records
# ------------------------------------------------------

passport_linked = (
    passport_viewing_data
    .dropna(subset=["Constituent.ID"])
    .copy()
)

passport_linked["Constituent.ID"] = (
    passport_linked["Constituent.ID"]
    .astype("Int64")
)


# ------------------------------------------------------
# 3) Overall Passport features
# ------------------------------------------------------

passport_features = (
    passport_linked
    .groupby("Constituent.ID")
    .agg(
        number_of_viewing_records=(
            "UID",
            "nunique"
        ),
        unique_titles_watched=(
            "Title",
            "nunique"
        ),
        unique_genres_watched=(
            "Genre",
            "nunique"
        ),
        unique_devices_used=(
            "Device",
            "nunique"
        ),
        average_percent_watched=(
            "Percent.Watched",
            "mean"
        ),
        first_viewing_date=(
            "Date.Watched",
            "min"
        ),
        most_recent_viewing_date=(
            "Date.Watched",
            "max"
        )
    )
    .reset_index()
    .rename(
        columns={
            "Constituent.ID": "Constituent ID"
        }
    )
)


# ------------------------------------------------------
# 4) Genre counts
# ------------------------------------------------------

passport_genre_counts = (
    passport_linked
    .pivot_table(
        index="Constituent.ID",
        columns="Genre",
        values="UID",
        aggfunc="nunique",
        fill_value=0
    )
)

passport_genre_counts.columns = [
    "passport_genre_" + clean_column_name(col)
    for col in passport_genre_counts.columns
]

passport_genre_counts = (
    passport_genre_counts
    .reset_index()
    .rename(
        columns={
            "Constituent.ID": "Constituent ID"
        }
    )
)


# ------------------------------------------------------
# 5) Device counts
# ------------------------------------------------------

passport_device_counts = (
    passport_linked
    .pivot_table(
        index="Constituent.ID",
        columns="Device",
        values="UID",
        aggfunc="nunique",
        fill_value=0
    )
)

passport_device_counts.columns = [
    "passport_device_" + clean_column_name(col)
    for col in passport_device_counts.columns
]

passport_device_counts = (
    passport_device_counts
    .reset_index()
    .rename(
        columns={
            "Constituent.ID": "Constituent ID"
        }
    )
)


# ------------------------------------------------------
# 6) Combine Passport features
# ------------------------------------------------------

passport_features = (
    passport_features
    .merge(
        passport_genre_counts,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )
    .merge(
        passport_device_counts,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )
)


# ======================================================
# Validate Constituent-Level Feature Tables
# ======================================================

datasets_expected_unique = {
    "memberships":
        constit_memberships,

    "acquisition_scores":
        constit_acquisition_scores,

    "capacity_ratings":
        constit_capacity_ratings,

    "engagement_scores":
        constit_engagement_scores,

    "payments_and_gifts":
        constit_payments_and_gifts,

    "soft_credits":
        soft_credit_features,

    "affiliations":
        affiliation_features,

    "involvements":
        involvement_features,

    "passport":
        passport_features
}


for name, df in datasets_expected_unique.items():

    duplicate_count = (
        df["Constituent ID"]
        .duplicated()
        .sum()
    )

    print(
        f"{name}: "
        f"{len(df):,} rows, "
        f"{df['Constituent ID'].nunique():,} unique constituents, "
        f"{duplicate_count:,} duplicate IDs"
    )

# ======================================================
# Join Constituent-Level Datasets
# ======================================================

df_combined = (
    constit_memberships

    .merge(
        constit_acquisition_scores,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )

    .merge(
        constit_capacity_ratings,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )

    .merge(
        constit_engagement_scores,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )

    .merge(
        constit_payments_and_gifts,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )

    .merge(
        soft_credit_features,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )

    .merge(
        affiliation_features,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )

    .merge(
        involvement_features,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )

    .merge(
        passport_features,
        on="Constituent ID",
        how="left",
        validate="one_to_one"
    )
)


zero_fill_columns = [
    "total_giving",
    "number_of_payments",
    "unique_campaigns",

    "number_of_premiums",
    "unique_premiums",
    "premium_record_count",
    "total_premium_fmv",
    "total_premium_cost",

    "number_of_soft_credits",
    "total_soft_credit_amount",
    "unique_hard_credit_orgs",
    "unique_soft_credit_gift_types",

    "number_of_affiliations",
    "number_of_active_affiliations",

    "number_of_involvements",
    "unique_involvement_types",

    "number_of_viewing_records",
    "unique_titles_watched",
    "unique_genres_watched",
    "unique_devices_used"
]


# Dynamically generated count / total columns
dynamic_zero_columns = [
    col
    for col in df_combined.columns
    if (
        col.startswith("total_giving_")
        or col.startswith("payment_count_")
        or col.startswith("soft_credit_type_")
        or col.startswith("soft_credit_gift_type_")
        or col.startswith("affiliation_")
        or col.startswith("involvement_")
        or col.startswith("passport_genre_")
        or col.startswith("passport_device_")
    )
]


zero_fill_columns = (
    zero_fill_columns
    + dynamic_zero_columns
)

zero_fill_columns = list(
    dict.fromkeys(zero_fill_columns)
)


# Only keep columns that actually exist
zero_fill_columns = [
    col
    for col in zero_fill_columns
    if col in df_combined.columns
]


df_combined[zero_fill_columns] = (
    df_combined[zero_fill_columns]
    .fillna(0)
)


# ======================================================
# Final Validation
# ======================================================

assert df_combined["Constituent ID"].is_unique


print("\nFinal combined dataset")

print(
    f"Rows: "
    f"{len(df_combined):,}"
)

print(
    f"Unique constituents: "
    f"{df_combined['Constituent ID'].nunique():,}"
)

print(
    f"Columns: "
    f"{len(df_combined.columns):,}"
)


# ======================================================
# Team Approach Matching Diagnostics
# ======================================================

print("\nTeam Approach matching")

print(
    "Total Team Approach records: "
    f"{len(team_approach_legacy_payments):,}"
)

print(
    "Unique-match records used: "
    f"{len(ta_unique_matches):,}"
)

print(
    "Multiple-match records excluded: "
    f"{len(ta_multiple_matches):,}"
)

print(
    "Unmatched records excluded: "
    f"{len(ta_unmatched):,}"
)

# ======================================================
# Soft Credit Matching Diagnostics
# ======================================================

print("\nSoft credit matching")

print(
    "Total source soft credit rows: "
    f"{len(soft_credits_from_orgs):,}"
)

print(
    "Linked source rows: "
    f"{soft_credits_from_orgs['Soft Credit Constituent ID'].notna().sum():,}"
)

print(
    "Unlinked source rows: "
    f"{soft_credits_from_orgs['Soft Credit Constituent ID'].isna().sum():,}"
)

print(
    "Soft credit events after deduplication: "
    f"{len(soft_credit_linked):,}"
)

print(
    "Constituents with soft credits: "
    f"{soft_credit_features['Constituent ID'].nunique():,}"
)

print(
    "Duplicate source rows collapsed: "
    f"{soft_credits_from_orgs['Soft Credit Constituent ID'].notna().sum() - len(soft_credit_linked):,}"
)

# ======================================================
# Passport Matching Diagnostics
# ======================================================

print("\nPassport matching")

print(
    "Total Passport records: "
    f"{len(passport_viewing_data):,}"
)

print(
    "Linked Passport records: "
    f"{len(passport_linked):,}"
)

print(
    "Unlinked Passport records: "
    f"{passport_viewing_data['Constituent.ID'].isna().sum():,}"
)