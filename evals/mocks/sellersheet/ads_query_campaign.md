{
  "notification": {"message": "Fetched 2 campaigns.", "type": "success"},
  "human_action": "Review the campaigns below.",
  "data": {
    "campaigns": [
      {"campaignId": "c-123", "name": "Evergreen - Auto", "state": "ENABLED",
       "adProduct": "SPONSORED_PRODUCTS",
       "budget": {"budgetType": "DAILY", "budgetValue": 25.0},
       "startDate": "2026-08-01"},
      {"campaignId": "c-456", "name": "Evergreen - Manual Exact", "state": "PAUSED",
       "adProduct": "SPONSORED_PRODUCTS",
       "budget": {"budgetType": "DAILY", "budgetValue": 15.0},
       "startDate": "2026-08-15"}
    ],
    "store": "{{input.store}}",
    "countryCode": "{{input.countryCode}}"
  }
}
