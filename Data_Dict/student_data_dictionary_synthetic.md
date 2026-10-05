# Data Dictionary: Synthetic Donor Data
 
Every row in these tables is synthetic. Identifiers are fabricated, and no row describes a real person, gift, solicitation or viewing record.
 
The tables follow the structure of --- without reproducing --- PBS Utah's donor systems. Column definitions for the constituent, payment, legacy and campaign-code tables are in `data_dictionary_unite_and_team_approach.md`, and soft-credit columns are in `soft_credits_data_dictionary.md`. This dictionary covers the files, the columns those documents do not, and conventions specific to this dataset.
 
## Files
 
| File | One row per | Key or link |
|---|---|---|
| `constituents_w_memberships.csv` | Constituent: people and organizations, including people who never gave | `Constituent ID` |
| `unite_payments.csv` | Payment, FY2021–FY2026 | `payment_id`; `donor_id` links to `Constituent ID` |
| `team_approach_legacy_payments.csv` | Legacy gift, before FY2021 | `ta_account_id` (household); `constituent_id_1`…`constituent_id_7` link to `Constituent ID` |
| `soft_credits.csv` | Soft credit | `Credit ID`; `Soft Credit Constituent ID` links to `Constituent ID` |
| `campaign_codes.csv` | Marketing code | `Marketing Code` |
| `campaign_members.csv` | Solicitation, FY2021–FY2026 | No unique key; `constituent_id` and `marketing_code` are links |
| `passport_engagement_by_genre.csv` | Constituent, fiscal year and genre, for years with viewing | `constituent_id`, `fiscal_year`, `genre` (unique together) |
| `cultivation.csv` | Donor-year assignment | `synthetic_id`, `fiscal_year` |
| `officer_portfolios.csv` | Officer portfolio | `portfolio_id` |
 
Every link above matches a row in the table it points to, with two exceptions: some legacy rows link to no constituent, and soft credits whose recipient could not be matched carry the ID `SYN-ORPHAN`.
 
## Conventions
 
- **Fiscal years** run July through June; FY2026 is July 2025 to June 2026. Payments in `unite_payments.csv` begin in FY2021; earlier giving is in `team_approach_legacy_payments.csv`.
- **Fiscal-year giving** for a constituent is the sum of positive payments the constituent made, plus positive soft credits assigned to the constituent, after exact duplicate rows are removed. A gift paid by an organization, such as a donor-advised fund, and soft-credited to a person counts once, as that person's giving.
- **Legacy households.** A legacy row can list up to seven constituent IDs for one household gift.
- **Recurring gifts** pay in all twelve months of each fiscal year a schedule is active.
- **Snapshot fields** in the constituents table, such as the sustainer flag, major-donor class and age, describe each constituent as of the end of the data, not in earlier years.
- **Blank fields.** Degree, employment and university-wide legacy fields are blank throughout.
## Soft credits
 
- Each soft credit is assigned to one person. No gift is credited to both spouses.
- Some `Credit ID` values repeat as exact duplicate rows.
- `Designation Detail ID` matches the designation ID of the corresponding payment in `unite_payments.csv`.
- The organizations that hold hard credits appear in the constituent and payment tables.
- `Hard Credit Org Type` has two values: `DAF Sponsor` and `Other Sponsor`.
- Soft credits begin in FY2021.
- Recipients with no matching constituent carry the ID `SYN-ORPHAN`.
## campaign_members.csv
 
| Field | Meaning |
|---|---|
| `constituent_id` | Solicited constituent; links to `Constituent ID` |
| `marketing_code` | Solicitation's marketing code; links to `Marketing Code` |
| `campaign_name` | Campaign name from the matching `campaign_codes.csv` row |
| `campaign_start_date` | First day of the solicitation's fiscal year; a fiscal-year marker, not a contact date |
| `responded` | `TRUE` when the constituent made a payment on the same marketing code in the same fiscal year |
| `responded_date` | Date of the earliest such payment; blank otherwise |
| `response_type` | `Payment` for responses; blank otherwise |
| `indirect_response` | Always `FALSE` |
 
A constituent can appear more than once with the same marketing code and fiscal year when none of those solicitations drew a response; a solicitation that drew a response appears once. One response can correspond to several payments with the same constituent, marketing code and fiscal year.
 
## passport_engagement_by_genre.csv
 
| Field | Meaning |
|---|---|
| `constituent_id` | Viewing constituent; links to `Constituent ID` |
| `fiscal_year` | Fiscal year of viewing |
| `genre` | Program genre; uncommon genres are grouped as `Other` |
| `titles_viewed` | Number of distinct titles viewed in the genre that year |
| `mean_percent_watched` | Average share of each title watched, from 0 to 1 |
 
A constituent-year has rows only if the constituent viewed something that year. A year without rows can mean no linked Passport account, no consent to share viewing, or no viewing; the table does not distinguish these. The table records viewing by year; it does not record when an account was created.
 
## cultivation.csv
 
| Field | Meaning |
|---|---|
| `synthetic_id` | Constituent; matches `Constituent ID` |
| `fiscal_year` | Fiscal year of the assignment |
| `portfolio_id` | Officer portfolio assignment |
| `selected` | Donor selected for possible cultivation |
| `contacted` | Selected donor assigned to contact |
| `holdout` | Selected donor randomly withheld from contact |
| `program_adopted` | The portfolio had adopted the cultivation program |
 
## officer_portfolios.csv
 
| Field | Meaning |
|---|---|
| `portfolio_id` | Portfolio identifier |
| `officer_id` | Officer identifier |
| `capacity` | Number of donors the portfolio can select each year |
| `rollout_fy` | Fiscal year the portfolio adopted the cultivation program; blank if never |
 
## Known issues
 
None at release. Issues found after release will be listed here; the data files will not change.
 
