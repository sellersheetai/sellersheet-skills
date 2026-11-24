# When an A+ call fails

Amazon names the failing field in the error's `details`, one entry per field, as
`Request failed validation: <operation>.<field path>: <rule>`. Fix every entry, then retry.

## Reading the answer

| What came back | What it means |
|---|---|
| 400 `InvalidInput`, "The request is not valid…" | a field breaks a rule (required, length, pattern, minimum size); `details` names each |
| 400 `InvalidInput`, "The request syntax is malformed…" | the JSON does not fit the model (a property misnamed or in the wrong place); `details` lists what is allowed there. Nothing else was checked yet |
| 200 with `errors` on a dry run | the call worked but the document has problems: read `errors` and `warnings` on every 200 |
| 403 `Unauthorized` | the message gives the reason: no access, a document of another marketplace, an ASIN outside the brand |
| 404 with `NOT_FOUND` | the content reference key does not exist |

## Writing the document

| Message | Fix |
|---|---|
| "cannot contain both premium and standard module types" | keep one family per document |
| "cannot have more than 7 modules" | a Premium document holds seven at most |
| "Content missing for given content module type!" | the module's own key is missing or does not match `contentModuleType` (see its section in `schema/`) |
| a JSON shape error naming a property | a list item without its wrapper, `body` where a Premium module wants `description`, or the ASIN set inside the document: use the names `details` lists |
| "contentType: must not be null" | `EBC` (seller), `EMC` (vendor) or `BrandStory` |
| "locale: must match …" | hyphenated: `en-US`, never `en_US` |
| "`imageCropSpecification.size.width.value`: must be greater than or equal to N" (or height) | the image is smaller than the module's minimum: use a bigger image |
| "hotspot placement out of bounds", "overlaps with hotspot", "invalid coordinate format" | move the marker inside the image and away from the others |
| "`buttonText.value`: length must be between 0 and 12" | a carousel button label is at most 12 characters |
| "Duplicate position found: N" | every card or column needs its own position |
| "Total text items … exceeds maximum", "Total text length … exceeds maximum", "length must be between …" | shorten to the module's limit in `schema/` |
| `CONTENT_FAILED_VALIDATION`, "We can't read one of the images…" | the image was not uploaded: give an image URL the server can download |

## Linking ASINs and publishing

| What happened | Fix |
|---|---|
| a Brand Story create fails with "shouldn't be using project type: [BrandStory]" although the dry run was clean | the account cannot use Brand Story yet; the dry run does not check entitlements |
| ASINs were linked without complaint but some are unusable | linking accepts any ASIN, even none: read the links with `includedDataSet` `METADATA` and look for `BRAND_NOT_ELIGIBLE` or `CATALOG_NOT_FOUND` |
| submit refused: "does not recognize this ASIN as part of your brand" | link the set again without those ASINs, then submit |
| submit refused: "an existing retail contribution on this ASIN" | Amazon's own content owns the ASIN; the seller asks Selling Partner Support (a vendor, their vendor manager) |
| an approved document is `DRAFT` again | updating it or posting its ASINs resets it; submit again (the approved version stays live meanwhile) |
| an approved document no longer shows on the ASIN | another document of the same family was approved on that ASIN and took it over; check `aplusContent_searchContentPublishRecords` before submitting |
| reading a document is refused although the key is right | the document belongs to another marketplace: use that store ref |
| a document is `APPROVED` seconds after submitting | some accounts are approved automatically: poll for `APPROVED` or `REJECTED`, not for `SUBMITTED` |
| a publish record says `EBC` for a Premium document | publish records give the family, not the tier; the tier is the document's badge |
