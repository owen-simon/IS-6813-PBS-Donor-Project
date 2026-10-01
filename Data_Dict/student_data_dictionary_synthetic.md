# Student Data Dictionary for the Synthetic PBS Utah Donor Data

## Purpose and authority

This student-facing dictionary describes the files emitted by the synthetic
donor generator, the conventions that differ from production data, and known
release limitations. No row represents a real person or gift.

PBS Utah's original dictionaries remain authoritative for the meaning of
source-system fields. In particular, use
`data_dictionary_unite_and_team_approach.md`,
and `soft_credits_data_dictionary.md` for production key, crediting, scope,
and field semantics. This document does not amend those originals.

## Public file inventory

| File | Unit | Main key or link | Synthetic use |
|---|---|---|---|
| `constituents_w_memberships.csv` | One row per constituent | `Constituent ID` | Static attributes and current snapshots |
| `unite_payments.csv` | One row per payment | `payment_id`; `donor_id` links to constituent | FY2021 onward payment history |
| `team_approach_legacy_payments.csv` | One row per legacy payment | `ta_account_id`; populated `constituent_id_1` links to constituent | Pre-FY2021 history used for donor features |
| `campaign_codes.csv` | One row per marketing code | `Marketing Code` | Catalog for payment marketing codes and campaign names |
| `soft_credits.csv` | One row per synthetic soft credit | `Credit ID`; `Soft Credit Constituent ID` links to constituent | Recognition credit for a hard-credited organization gift |
| `cultivation.csv` | One donor-year assignment row | `synthetic_id`, `fiscal_year` | Selection, contact, holdout, and program adoption |
| `officer_portfolios.csv` | One row per synthetic portfolio | `portfolio_id` | Officer, capacity, and rollout year |

The first five files reuse the public PBS Utah column descriptions wherever
those columns appear in the original dictionaries. The last two are
synthetic-only teaching tables.

## Synthetic-only columns

### cultivation.csv

| Field | Meaning |
|---|---|
| `synthetic_id` | Fabricated constituent identifier matching `Constituent ID` |
| `fiscal_year` | Fiscal year in which cultivation was assigned |
| `portfolio_id` | Synthetic officer portfolio assignment |
| `selected` | Donor selected for possible cultivation |
| `contacted` | Selected donor assigned contact rather than holdout |
| `holdout` | Randomized selected donor withheld from contact |
| `program_adopted` | Portfolio had adopted the synthetic cultivation program |

### officer_portfolios.csv

| Field | Meaning |
|---|---|
| `portfolio_id` | Fabricated portfolio identifier |
| `officer_id` | Fabricated officer identifier |
| `capacity` | Annual number of donors the portfolio can select |
| `rollout_fy` | Fiscal year of synthetic program adoption; blank for never treated |

## Synthetic conventions

- Fiscal years end June 30. Unite output begins in FY2021; earlier behavioral
  history is represented in Team Approach.
- Output identifiers are fabricated. They preserve only the documented joins
  needed for the student analysis.
- Fiscal-year giving and the $1,200 crossing target use recognition credit.
  A routed organization gift belongs to the soft-credited constituent; do not
  add its hard and soft sides as two gifts.
- A donor's annual giving band is preserved during emission. Large gifts are
  represented only through the published bands and generated values; no rare
  or extreme real amount is copied.
- Passport and solicitation-history tables are later additions and are not in
  this base release.

## Known issues

This section is the home for post-release notes about the synthetic data.

- Second one-time gifts occur in about 18% of eligible donor-years, about
  twice as often as in PBS Utah's records.
- Recurring schedules default to twelve paid months. Unite has 23.69% more
  payment rows than PBS Utah's records for the same years, after unusable rows
  are removed.
- Synthetic legacy history is fully linked for behavioral reconstruction.
  Extra unmatched rows are emitted as orphans, producing 20.64% more legacy
  payment rows than PBS Utah's records for the same years, after unusable rows
  are removed.
- The synthetic system cutover is FY2021 rather than the May 2020 production
  cutover.
- Soft-credit designation IDs intentionally join the corresponding synthetic
  payment. This differs from the production identifier semantics in PBS
  Utah's soft-credit dictionary. The release volume gate covers FY2021 onward.
- University degree, employment, and university-wide legacy fields are not
  modeled. Blank values in those nullable fields mean unavailable, not zero.
- Effect sizes in these data are not PBS Utah's, and which predictors matter
  reflects how the data were generated.
- The CSV files can exceed Excel's worksheet row limit. Use Python, R, a
  database, or Power Query rather than opening and resaving the full files in
  Excel.
- Split train and test data by fiscal year or donor, as appropriate. Randomly
  splitting donor-years can place one donor's history on both sides and leak
  future information.

## Note for the synthetic release: soft credits

The original `soft_credits_data_dictionary.md` describes PBS Utah's records.
This section describes how the synthetic release differs and how to use soft
credits in the major-donor label.

### How this release differs from PBS Utah's records

- **Credit IDs are not all unique.** Some rows are exact duplicates.
- **Designation Detail IDs match designation IDs in the payment table.** In
  PBS Utah's records they do not. Do not write logic that depends on this
  match.
- **The organizations that received hard credits appear in the constituent and
  payment tables.** In PBS Utah's records, Hard Credit Org IDs appear in no
  other table.
- **Hard Credit Org Type has two values,** `DAF Sponsor` and `Other Sponsor`.
  PBS Utah's records use a finer classification of their own.
- **Soft credits begin in fiscal year 2021.** PBS Utah's begin in 1983.
- **Each donation is soft-credited to one person.** The release contains no
  donations credited to both spouses.
- **Unmatched recipients carry the placeholder ID `SYN-ORPHAN`.**
- **Duplicate and unmatched rows occur at lower rates** than in PBS Utah's
  records.

### Using soft credits in the major-donor label

- **Crediting rule.** A donor's fiscal-year giving is the sum of (a) positive
  payments in which the donor, an individual in the constituent table, is the
  payer and (b) positive soft credits assigned to the donor. Remove exact
  duplicate rows before summing. For revenue totals, count payments only;
  soft credits recognize giving, they do not add revenue.
- **Recipients and shared credits.** A recipient may be identified by a
  Constituent ID or by a Spouse Constituent ID. In PBS Utah's records, one
  donation may be soft-credited to both spouses; credit each spouse with their
  own soft credit, and keep spouses together when you split data for training
  and testing.
- **Make the rule a parameter.** PBS Utah's recognition rule will be applied
  when pipelines are run on real data. That includes which organization and
  gift types count, how repeated Credit IDs that differ are treated, and how
  shared credits are handled. Write your pipeline so these can be changed in
  one place.
- **Report what you remove.** Your pipeline should report how many rows each
  cleaning rule removes, by table and fiscal year, rather than removing them
  silently.
- **Known limitation.** The split between direct and soft-credit giving among
  threshold crossers has not been validated against PBS Utah's records. Do not
  draw conclusions about the role of soft credits in major giving.
