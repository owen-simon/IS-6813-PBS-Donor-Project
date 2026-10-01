# Data Dictionary for the Soft Credits Table

## Soft Credits from Organizations

This dataset lists soft credits awarded to constituents where the hard credit was awarded to an organization. This includes DAFs (donor-advised funds), matching gifts, fundraising consortia, trusts, foundations, and others. This data is only from Unite, not from the legacy Team Approach database. Gifts date as far back as 1983.

- **Credit ID** is unique.
- **Designation Detail ID** can have multiple instances and will not match any other Designation Detail IDs in other datasets. If the ID appears twice, it is likely a soft credit awarded to two spouses. A household could therefore have two soft credits for one donation.
- **Soft Credit Constituent ID** matches Constituent ID or Spouse Constituent ID in Constituents with Memberships and other related datasets. This is the constituent who received the soft credit.
- **Hard Credit Org ID** is the unique identifier for the organization that received the hard credit for the donation. These IDs are not referenced in any other dataset.
- **Hard Credit Org Type** is the organization classification assigned to the Hard Credit Org ID.
- **Credit Gift Type** describes whether the gift was an Outright Gift, Payment, or Matching Gift.
- **Credit Amount** is the dollar amount of the credit.
- **Credit Date** is the date of the credit.
- **Credit Type** is `Soft` for all rows.
