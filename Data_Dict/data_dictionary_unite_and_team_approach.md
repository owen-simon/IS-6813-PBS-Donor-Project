# Dataset Data Dictionaries

constituents_w_memberships.csv

unite_payments.csv

unite_giftpremiums.csv

team_approach_legacy_payments.csv

campaign_codes.csv

constituents_w_acquisition_scores.csv

constituents_w_affiliations.csv

constituents_w_involvements.csv

constituents_w_capacity_ratings.csv

constituents_w_engagement_scores.csv

passport_viewing_data.csv

Supplement 1: Campaign Codes / Marketing Codes / Source Codes

Supplement 2: Making Team Approach Play Nice with Unite

## constituents_w_memberships.csv

| Order | Field Name | Data Type | Primary Key | Nullable | Values | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Constituent ID | Integer | X | FALSE | Unique | Primary Key |
| 2 | Spouse Constituent ID | Integer |  | TRUE | Unique | Secondary Primary Key - Constituent ID of spouse, who may also be in this dataset |
| 3 | Address City | Character |  | TRUE | Thousands, non-unique | Address city of constituent |
| 4 | Address ZIP | Character |  | TRUE | Thousands, non-unique | Address ZIP code of constituent |
| 5 | Address State | Character |  | TRUE | Dozens, non-unique | Address State of constituent |
| 6 | Age | Integer |  | TRUE | Dozens, non-unique | Age of constituent |
| 7 | Annual Giving Group | Character |  | FALSE | ND \| PD \| LD \| SL \| CD | Unknown |
| 8 | Constituent Type | Character |  | FALSE | Dozens, non-unique | Concatenated list of all Types associated with each constituent, separated with ";" |
| 9 | UofU Degree Count | Integer |  | FALSE | 0-7 | Count of University of Utah Degrees constituents have. (Only University of Utah) |
| 10 | UofU Degree Info | Character |  | TRUE | Thousands, non-unique | Concatenated list of Department, Degree Type, Graduating Year, and School information of each degree. |
| 11 | Latest UofU Degree Year | Integer |  | TRUE | Dozens, non-unique | Graduating year of most recent UofU Degree |
| 12 | UofU Employment Status | Character |  | TRUE | Current \| Former \| Retired \| Emeritus \| Unconfirmed | Current University of Utah employment status |
| 13 | Gender | Character |  | FALSE | Male \| Female \| Unknown | Gender of constituent |
| 14 | Has UofU Legacy Gift | Boolean |  | FALSE | TRUE, FALSE (1, 0) | If the constituent has a Legacy (Planned, Bequest) Gift with any department of the University of Utah on record |
| 15 | Legacy Circle Member PBS Utah | Boolean |  | FALSE | TRUE, FALSE (1, 0) | If the constituent has a Legacy (Planned, Bequest) Gift with PBS Utah on record |
| 16 | Lifetime UofU Fundraising | Currency |  | TRUE | Thousands, non-unique | Estimated total University of Utah giving on record for the constituent |
| 17 | Major Donor Class PBS Utah | Character |  | TRUE | Former \| Director \| Broadcaster \| Lapsed \| Patron | Broadcaster: Gives $1,000-$4,999.99 annually to PBS Utah. Director: Gives $5,000-$9,999.99 annually to PBS Utah. Patron: Gives $10,000+ annually to PBS Utah. Former: Used to be a Broadcaster, Director, or Patron Lapsed: Has not yet renewed this year. |
| 18 | Marital Status | Character |  | TRUE | Married \| Divorces \| Widowed | Marriage noted in database. Many NULL values are likely not the actual status of the constituent. |
| 19 | Previous FY UofU Cash | Currency |  | TRUE | Thousands, non-unique | Estimated total University of Utah giving last Fiscal Year for the constituent |
| 20 | Primary Constituent Type | Character |  | FALSE | Alumni (No Degree) \| Donors \| Staff \| Alumni (Degree) \| Friends \| Faculty \| Former Staff \| Former Faculty \| Emeritus Faculty \| Parents \| Former Students \| Former Trustees \| Trustees | Primary constituent type from column 8 - Constituent Type |
| 21 | Prospect Committed Giving Amount UofU | Currency |  | TRUE | Thousands, non-unique | Unknown |
| 22 | Sustainer PBS Utah | Boolean |  | FALSE | TRUE, FALSE (1, 0) | Constituent is currently a PBS Utah Sustainer (giving a monthly recurring gift) |

## unite_payments.csv

| Order | Field Name | Data Type | Primary Key | Nullable | Values | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | donor_id | Integer |  | FALSE | Thousands, non-unique | Foreign Key |
| 2 | designation_detail_id | Character |  | FALSE | Thousands, non-unique | Foreign Key |
| 3 | credit_date | Date |  | FALSE | Thousands, non-unique | Date of Pledge |
| 4 | tender_type | Character |  | FALSE | Check \| Credit Card \| EFT \| Payroll Deduction \| Third Party \| Cash \| Wire | Payment method of donation |
| 5 | payment_amount | Currency |  | FALSE | Hundreds, non-unique | Amount of donation |
| 6 | pledge_gift_status | Character |  | FALSE | Funded \| Paid \| Terminated \| Active | Current Status of pledge |
| 7 | pledge_gift_type | Character |  | FALSE | Outright \| Standard \| Recurring \| PGIRA (Distribution from IRA) \| Payroll | Type of pledge |
| 8 | opportunity_id | Character |  | FALSE | Thousands, non-unique | Foreign Key |
| 9 | payment_frequency | Character |  | TRUE | Monthly \| Bi-Weekly \| Annual | Frequency of donation |
| 10 | gift_type | Character |  | FALSE | Rejoin \| Renew \| Upgrade \| Additional \| New \| Downgrade \| Unhandled | Gift Type of donation |
| 11 | campaign_name | Character |  | FALSE | Thousands, non-unique | Name of associated campaign |
| 12 | payment_id | Character | X | FALSE | Unique | Unique ID |
| 13 | marketing_code | Character |  | FALSE | Thousands, non-unique | Source Code / Marketing Code / Campaign Code of donation |

## unite_giftpremiums.csv

| Order | Field Name | Data Type | Primary Key | Nullable | Values | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Record ID | Character |  | FALSE | Thousands, non-unique | Foreign Key, single Record IDs can have multiple Premiums and therefore multiple rows |
| 2 | Constituent ID | Integer |  | FALSE | Thousands, non-unique | Foreign Key, single Constituent IDs can have multiple Record IDs and multiple Premiums and therefore multiple rows |
| 3 | Code | Character |  | FALSE | Thousands, non-unique | Premium/Thank-You Gift Code |
| 4 | Name: Benefit | Character |  | FALSE | Thousands, non-unique | Premium/Thank-You Gift Name |
| 5 | Shipping Status | Character |  | FALSE | Shipped \| Returned \| Not Ready for Delivery \| Suspended Delivery \| Delivered \| Pending Fulfillment \| Ready to Pull | Status of Premium Shipment |
| 6 | Minimum Award Amount | Currency |  | TRUE | Dozens, non-unique | Minimum annual donation amount required to receive premium |
| 7 | Minimum Payment Delivery | Currency |  | TRUE | Dozens, non-unique | Minimum payment amount before premium is shipped do constituent |
| 8 | Supplier | Character |  | TRUE | 19 values | Supplier of premium |
| 9 | Shipping Vendor | Character |  | TRUE | FOREST \| KUED \| URBANFORGE \| EVENTVENUE | Shipper of premium |
| 10 | Fair Market Value | Currency |  | TRUE | Hundreds, non-unique | Fair Market Value (FMV) of premium |
| 11 | Unit Cost | Currency |  | TRUE | Hundreds, non-unique | Station Cost / Unit Cost of premium |
| 12 | Item Type | Character |  | TRUE | 18 values | Type category of premium item |

## team_approach_legacy_payments.csv

| Order | Field Name | Data Type | Primary Key | Nullable | Values | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ta_account_id | Integer | X | FALSE | Unique | Primary Key from previous Team Approach database |
| 2 | gift_kind | Character |  | FALSE | Installment \| One-Time \| Sustaining | Gift kind is either one-time, installments, or ongoing sustaining (recurring) |
| 3 | gift_type | Character |  | FALSE | Renew \| Rejoin \| Additional \| New \| Upgrade \| Other \| Third-Party | Type of gift |
| 4 | gift_date | Date |  | FALSE | Thousands, non-unique | Date of gift |
| 5 | activity_type | Character |  | FALSE | M \| O \| D \| T \| I \| R | Character #2 in source_code / Marketing Code / Campaign Code |
| 6 | campaign | Character |  | FALSE | G \| P \| A \| Q \| L \| R \| U \| E \| V \| C | Character #3 in source_code / Marketing Code / Campaign Code |
| 7 | initiative | Character |  | FALSE | Hundreds, non-unique | Characters #4-#7 in source_code / Marketing Code / Campaign Code |
| 8 | effort | Character |  | FALSE | Dozens, non-unique | Characters #8-#9 in source_code / Marketing Code / Campaign Code |
| 9 | source_code | Character |  | FALSE | Thousands, non-unique | See supplemental information |
| 10 | source_description | Character |  | FALSE | Thousands, non-unique | Name associated with source_code / Marketing Code / Campaign Code |
| 11 | payment_amount | Currency |  | FALSE | Thousands, non-unique | Amount of donation |
| 12 | payment_method | Character |  | FALSE | Payroll Deduct \| Charge Card \| Check \| EFT \| Cash \| Stock \| Money Order \| In-Kind | Payment method of donation |
| 13 | city | Character |  | TRUE | Thousands, non-unique | Address city of constituent |
| 14 | state | Character |  | TRUE | Dozens, non-unique | Address State of constituent |
| 15 | zip | Character |  | TRUE | Thousands, non-unique | Address ZIP code of constituent |
| 16 | county | Character |  | TRUE | Hundreds, non-unique | Address County code of constituent |
| 17 | program | Character |  | TRUE | Thousands, non-unique | TV Program associated with donation/source_code, if applicable |
| 18 | technique_trans | Character |  | FALSE | 19 values | How the donation got to PBS Utah |
| 19 | pledge_time | Date |  | TRUE | Thousands, non-unique | Datetime of donation |
| 20 | premium_1_code | Character |  | TRUE | Thousands, non-unique | Premium/Thank-You Gift 1 Code |
| 21 | premium_1_name | Character |  | TRUE | Thousands, non-unique | Premium/Thank-You Gift 1 Name |
| 22 | premium_2_code | Character |  | TRUE | Thousands, non-unique | Premium/Thank-You Gift 2 Code |
| 23 | premium_2_name | Character |  | TRUE | Thousands, non-unique | Premium/Thank-You Gift 2 Name |
| 24 | premium_3_code | Character |  | TRUE | Hundreds, non-unique | Premium/Thank-You Gift 3 Code |
| 25 | premium_3_name | Character |  | TRUE | Hundreds, non-unique | Premium/Thank-You Gift 3 Name |
| 26 | premium_4_code | Character |  | TRUE | Hundreds, non-unique | Premium/Thank-You Gift 4 Code |
| 27 | premium_4_name | Character |  | TRUE | Hundreds, non-unique | Premium/Thank-You Gift 4 Name |
| 28 | premium_5_code | Character |  | TRUE | Dozens, non-unique | Premium/Thank-You Gift 5 Code |
| 29 | premium_5_name | Character |  | TRUE | Dozens, non-unique | Premium/Thank-You Gift 5 Name |
| 30 | premium_6_code | Character |  | TRUE | Dozens, non-unique | Premium/Thank-You Gift 6 Code |
| 31 | premium_6_name | Character |  | TRUE | Dozens, non-unique | Premium/Thank-You Gift 6 Name |
| 32 | program_source | Character |  | TRUE | KUED \| PBS \| EPS \| OTHER \| NETA \| APT \| BBC | Where TV Program associated with donation/source_code came from, if applicable |
| 33 | source_category | Character |  | FALSE | 29 Values | How the donation got to PBS Utah, alternative categorization |
| 34 | communication_method | Character |  | FALSE | Miscellaneous \| Digital \| Mail \| Phone \| In-Person \| Email | How PBS Utah solicited the donor |
| 35 | communication_type | Character |  | TRUE | White Mail \| Unknown \| Live/On-Air Media \| Direct Mail \| Paid External Caller \| Paid Internal Staff \| Email \| Paid University Caller \| Giving Day \| Social Media / Digital Advertisement | How PBS Utah solicited the donor, dependent on communication_method |
| 36 | activity | Character |  | FALSE | A | Character #1 in source_code / Marketing Code / Campaign Code |
| 37 | segment | Character |  | FALSE | Hundreds, non-unique | Characters #10-#12 in source_code / Marketing Code / Campaign Code |
| 38 | constituent_id_1 | Integer |  | TRUE | Unique foreign key | Matching Unite Constituent #1 |
| 39 | constituent_id_2 | Integer |  | TRUE | Unique foreign key | Matching Unite Constituent #2 |
| 40 | constituent_id_3 | Integer |  | TRUE | Unique foreign key | Matching Unite Constituent #3 |
| 41 | constituent_id_4 | Integer |  | TRUE | Unique foreign key | Matching Unite Constituent #4 |
| 42 | constituent_id_5 | Integer |  | TRUE | Unique foreign key | Matching Unite Constituent #5 |
| 43 | constituent_id_6 | Integer |  | TRUE | Unique foreign key | Matching Unite Constituent #6 |
| 44 | constituent_id_7 | Integer |  | TRUE | Unique foreign key | Matching Unite Constituent #7 |

## campaign_codes.csv

| Order | Field Name | Data Type | Primary Key | Nullable | Values | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Marketing Code | Character | X | FALSE | Unique | Unique Primary Key of campaign code |
| 2 | Source Category | Character |  | TRUE | 34 values | Category of marketing code |
| 3 | Campaign Name | Character |  | TRUE | Thousands, non-unique | Name of marketing code |
| 4 | Campaign ID | Character |  | FALSE | Unique | Ignore |
| 5 | Activity | Character |  | FALSE | A - Annual \| G - Matching Gifts \| P - Legacy Giving \| U - Underwriting | Character #1 in source_code / Marketing Code / Campaign Code |
| 6 | Activity Type | Character |  | FALSE | M - Membership \| D - Major Gift \| I - Mid Level \| O - On-Air \| T - Sustainers \| F - Foundation/Grant \| B - Business/Sponsorship | Character #2 in source_code / Marketing Code / Campaign Code |
| 7 | Campaign Type | Character |  | FALSE | Q - New/Aquisition \| L - Lapsed \| A - Add Gift \| G - General \| R - Renewal \| U - Upgrade \| C - Complimentary \| V - Canvassing \| E - Event \| P - Pledge \| D - Specific Underwriting \| F - Program Fund \| H - Local Projects \| X - Challenge Grant \| W - Endowment | Character #3 in source_code / Marketing Code / Campaign Code.<br>(Acquisition is indeed spelled incorrectly.) |
| 8 | Initiative Year | Character |  | FALSE | 32 values | Characters #4-#5 in source_code / Marketing Code / Campaign Code |
| 9 | Initiative Month | Character |  | FALSE | 14 values | Characters #6-#7 in source_code / Marketing Code / Campaign Code |
| 10 | Effort | Character |  | FALSE | Dozens of values, non-unique | Characters #8-#9 in source_code / Marketing Code / Campaign Code |
| 11 | Segment | Character |  | FALSE | Hundreds of values, non-unique | Characters #10-#12 in source_code / Marketing Code / Campaign Code |
| 12 | Communication Method | Character |  | FALSE | Mail \| In-Person \| Phone \| Miscellaneous \| Email \| Digital | Method of communication of solicitation |
| 13 | Communication Type | Character |  | FALSE | Direct Mail \| Paid Internal Staff \| Paid External Caller \| Unknown \| White Mail \| Email \| Social Media / Digital Advertisement \| Live/On-Air Media \| Giving Day \| Paid University Caller \| On-Demand Media \| Virtual Event \| Event \| Invitation / Save the Date \| Peer / Volunteer \| Publication / Newsletter \| Crowdfunding | Type of communication, depends on Method |
| 14 | Active | Boolean |  | FALSE | TRUE, FALSE (1, 0) | Whether campaign is Active or not - Active means the campaign happened |
| 15 | Campaign Description | Character |  | TRUE | Thousands, non-unique | Description of campaign, usually the same as the Campaign Name |
| 16 | Gift Type | Character |  | TRUE | Lapsed/Rejoin \| Additional Gift \| Renewal \| New \| Upgrade Sustainer \| Donation \| Upgrade/Reset \| New Sustainer \| Matching Gift \| Upgrade | Gift type associated with campaign code |
| 17 | Solicitation | Boolean |  | FALSE | TRUE, FALSE (1, 0) | Whether campaign was a solicitation or not |

## constituents_w_acquisition_scores.csv

| Order | Field Name | Data Type | Primary Key | Nullable | Values | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Constituent ID | Integer |  | FALSE | Unique | Foreign Key |
| 2 | Record ID | Character | X | FALSE | Unique | Primary Key beginning with "WR-" |
| 3 | Acquisition Score | Decimal |  | FALSE | Dozens, non-unique | Score ranges from 0.00-1.00 and correlates to potential to acquire as a donor to the University of Utah. Not PBS Utah-specific. |
| 4 | Record Type | Character |  | FALSE | Contact G2G Rating Score | Record Type, kept in case all "WR-" tables are combined. |

## constituents_w_affiliations.csv

| Order | Field Name | Data Type | Primary Key | Nullable | Values | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Constituent ID | Integer |  | FALSE | Unique | Foreign Key. Single Constituent can have multiple Affiliations. |
| 2 | Record ID | Character | X | FALSE | Unique | Primary Key beginning with "AF-" |
| 3 | Constituent Role | Character |  | TRUE | Employee \| Board Member/Trustee \| Owner \| Volunteer / Member \| Board Member/Officer \| Estate Donor | Employment role with affiliation |
| 4 | Active | Boolean |  | FALSE | TRUE, FALSE (1, 0) | If Constituent Role is listed as Active or Current in database. |

## constituents_w_involvements.csv

| Order | Field Name | Data Type | Primary Key | Nullable | Values | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Constituent ID | Integer |  | FALSE | Unique | Foreign Key. Single Constituent can have multiple Involvements. |
| 2 | Record ID | Character | X | FALSE | Unique | Primary Key beginning with "WR-" |
| 3 | Involvement: Type | Character |  | FALSE | 22 non-unique values | Type of involvement associated with constituent |

## constituents_w_capacity_ratings.csv

| Order | Field Name | Data Type | Primary Key | Nullable | Values | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Constituent ID | Integer |  | FALSE | Unique | Foreign Key |
| 2 | Record ID | Character | X | FALSE | Unique | Primary Key beginning with "WR-" |
| 3 | Rating Number | Integer |  | FALSE | 0-10 | Rating assigned based on Est. Total Capacity |
| 4 | Adjusted Total Giving | Currency |  | FALSE | Thousands, non-unique | Adjusted total giving to University of Utah |
| 5 | Created Date | Date |  | FALSE | Dozens, non-unique | Date of Capacity Rating |
| 6 | Est. Total Capacity | Currency |  | FALSE | Thousands, non-unique | Estimated giving capacity |
| 7 | Level | Character |  | FALSE | $25K - $50K \| $1 - $10K \| $100K - $250K \| $10K - $25K \| $50K - $100K \| $250K - $500K \| $10M - $25M \| $500K - $1M \| $5M - $10M \| Unrated \| $1M - $5M | Named capacity based on Rating Number |
| 8 | Record Type | Character |  | FALSE | Constituent Capacity Rating | Record Type, kept in case all "WR-" tables are combined. |
| 9 | Source Date | Date |  | FALSE | Dozens, non-unique | Date of Source |
| 10 | Last Modified Date | Date |  | FALSE | Dozens, non-unique | Date record last modified |

## constituents_w_engagement_scores.csv

| Order | Field Name | Data Type | Primary Key | Nullable | Values | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Constituent ID | Integer |  | FALSE | Unique | Foreign Key |
| 2 | Record ID | Character | X | FALSE | Unique | Primary Key beginning with "WR-" |
| 3 | Engagement Score Total | Integer |  | FALSE | 0-36 | Sum of columns 4-9: Max of 36 points: Indicator of the level of connection the constituent has with the University, including communication, event participation, volunteer activity, student involvement, and philanthropy |
| 4 | Additional Affiliation Score | Integer |  | FALSE | 0-8 | Max of 8 points: Indicator of a constituent’s points of engagement beyond alum, donor, or volunteer; includes U employment, family connections, and memberships. |
| 5 | Constituent Behavior Score | Integer |  | FALSE | 0-6 | Max of 6 points: Indicator of a constituent’s engagement through event attendance, communication channels, and marketing campaigns. |
| 6 | Donor Score | Integer |  | FALSE | 0-7 | Max of 7 points: Indicator of a constituent’s recent and significant U giving behavior and their personal relationship to major donors. |
| 7 | Relationship Building Score | Integer |  | FALSE | 0-5 | Max of 5 points: Indicator of activity initiated by U advancement staff, such as contact reports, plans, and award recognition. |
| 8 | Student Score | Integer |  | FALSE | 0-6 | Max of 6 points: Indicator of a constituent’s engagement while they were a U student, including degrees received and activities (e.g. student government, scholarships, honor societies, Greek life, sports, etc.). |
| 9 | Volunteer Score | Integer |  | FALSE | 0-4 | Max of 4 points: Indicator of constituent’s participation in board, committee, and other volunteer activities. |
| 10 | Record Type | Character |  | FALSE | Contact UA Engagement Score | Record Type, kept in case all "WR-" tables are combined. |

## passport_viewing_data.csv

| Order | Field Name | Data Type | Primary Key | Nullable | Values | Meaning |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Content.Channel | Character |  | FALSE | Thousands, non-unique | Grouping to which the piece of media belongs |
| 2 | TP.Media.ID | Integer |  | FALSE | Thousands, non-unique | Foreign Key |
| 3 | UID | Character | X | FALSE | Thousands, non-unique | Primary Key |
| 4 | Membership.ID | Character |  | FALSE | Thousands, non-unique | Foreign Key |
| 5 | Title | Character |  | FALSE | Thousands, non-unique | Title of media |
| 6 | Device | Character |  | FALSE | IOS \| AppleTV App \| TVOS App \| Video Portal \| Player \| Samsung TV \| PartnerPlayer \| GA Roku \| GA Android TV \| Android \| Vizio TV \| GA Fire TV \| comcastx1 \| LG TV \| KIDS AppleTV App \| Kids Roku \| Windows \| KIDS Android TV \| Kids Xbox One \| Amazon OS TV | Device OS the media was watched on |
| 7 | Date.Watched | Date |  | FALSE | Thousands, non-unique | Date of viewing |
| 8 | Time.Watched | Integer |  | FALSE | Thousands, non-unique | Time of viewing |
| 9 | Total.Run.Time.of.the.Video | Integer |  | FALSE | Thousands, non-unique | Total run time of media in seconds |
| 10 | CID | Character |  | TRUE | Thousands, non-unique | Foreign Key |
| 11 | Genre | Character |  | FALSE | Drama \| Other \| Science and Nature \| History \| Culture \| News and Public Affairs \| Home and How To \| Arts and Music \| Food \| Indie Films | Genre of media |
| 12 | Percent.Watched | Decimal |  | FALSE | Thousands, non-unique | Percent of media watched |
| 13 | Constituent.ID | Integer |  | TRUE | Thousands, non-unique | Foreign Key |

## Supplement 1: Campaign Codes / Marketing Codes / Source Codes:

Breaking down campaign codes into more helpful categories:

- A campaign code that starts with "AD" = "Major Gifts"

- A campaign w/code that starts with "AMR”, “AIR”, or “ATR") and does not have “Recapture” in the campaign name = "Renewal"

- A campaign code that starts with "AMA”, “AIA” or “ATA" = "Additional Gift"

- A campaign code that starts with "AMQ”, “AIQ”, or “ATQ" = "Acquisition"

- A campaign w/code that starts with "AMV" and has “Canvass” in the campaign name = "Canvassing"

- A campaign code that starts with "AOP” or “AMP" = "Pledge"

- A campaign code that starts with "AML” or “AIL" = "Lapsed"

- A campaign code that starts with "AIU”, “AMU”, or “ATU" = "Upgrade"

- A campaign code that starts with "UBD”, “UBF”, or “UFF" = "Underwriting"

- A campaign name that includes either "Recapture” or “Reinstate" and whose campaign code matches the following format "AMR\\d{4}99000") = "Recapture"

- A campaign name that includes the keywords "Passport”, “Xfinity”, “Android” or “Amazon" = "Passport"

- A campaign name that includes the keywords "EOY” or “End of Year" = "End of Year"

- A campaign name that includes the keywords "Giving Tuesday” “GT” “PMGD” or “Public Media Giving Day" = "Giving Day"

- Other donations not matching any of the above criteria are considered "Generic"

More Details on the Structure of a code:

- The campaign code is 12 characters long and is meant to give you nearly all the important information about the campaign within those characters.

- Character 1 = Activity: A - Annual | G - Matching Gifts | P - Legacy Giving | U – Underwriting

- Character 2 = Activity Type: M - Membership | D - Major Gift | I - Mid Level | O - On-Air | T - Sustainers | F - Foundation/Grant | B - Business/Sponsorship

- Character 3 = Campaign Type: Q - New/Aquisition | L - Lapsed | A - Add Gift | G - General | R - Renewal | U - Upgrade | C - Complimentary | V - Canvassing | E - Event | P - Pledge | D - Specific Underwriting | F - Program Fund | H - Local Projects | X - Challenge Grant | W – Endowment

- Characters 4-5 = Initiative Year: Final 2 digits of year. If in the 1990s, the Initiative Year will be like 98 or 99, then we have 00-09, 10-19, 20-27, so far. The year can be either the actual Calendar Year, if the next two characters are not “00”, or the Fiscal Year, if the next two characters (Initiative Month) are “00”.

- Characters 6-7 = Initiative Month: 01-12 or 00, if a Fiscal-Year based campaign code. If it is an FY-based code, the code is used for the entire FY, not just a single month.

- Characters 8-9 = Effort: In a typical solicitation under Q - New/Aquisition | L - Lapsed | A - Add Gift | R - Renewal | or U – Upgrade, the effort will symbolize the solicitation attempt number within the campaign and they will either be in format 10, 20, 30, or 01, 02, 03. If 1#, 2#, 3#, etc., the “#” is a test segment number within the effort.

- Characters 10-12 = Segment: Individual segmentations of the donors within the efforts. Sometimes segments receive different copy in solicitations, or sometimes we’re just holding them in a segment to see how it performs separate from the rest of the segments.

Examples:

- AMA240310005: This is an Add Gift campaign (Under Annual, Membership), conducted in March 2024, First Effort, Fifth Segment

- AMR180104001: This is a Renewal Gift campaign (Under Annual, Membership) conducted in January 2018, Fourth Effort, First Segment

- AMG270001001: This is a Fiscal Year-based campaign code under Annual, Membership, General, FY27, Effort 01, Segment 001. Here, effort and segment do not have the same definitions as it is a General code.

## Supplement 2: Making Team Approach Play Nice with Unite

- Payment_Method (Team Approach) is equivalent to Tender_Type (Unite)

- Premium_Code (Team Approach) is equivalent to Code on the Gift Premiums object (Unite)

- Pledge_Gift_Type (Unite) is equivalent to gift_kind (Team Approach)

- Credit_Date (Unite) is equivalent to gift_date (Team Approach)

- Campaign_Code (Unite) is equivalent to source_code (Team Approach)

- Campaign_Name (Unite) is equivalent to source_description (Team Approach)

- A Pledge_Gift_Type of "Sustaining" (TA) is equivalent to "Recurring" (Unite)

- A Payment_Method of "Charge Card" (TA) is equivalent to "Credit Card" (Unite)

- A Payment_Method of "Payroll Deduct" (TA) is equivalent to "Payroll Deduction" (Unite)

- A Payment_Method of "Stock" (TA) = "Stock Gift" (Unite)

- A Payment_Method of "Money Order" (TA) = "Check" (Unite)

- A Pledge_Gift_Type of "Installment" can be changed to "Standard" for simplicity


