{
  "notification": {"message": "Welcome back. 1 store connected.", "type": "success"},
  "human_action": "Pick a store and proceed.",
  "mcp_server_version": "2026.09.29.1",
  "data": {
    "message": "Welcome back. 1 store connected.",
    "canUseMcp": true,
    "store_refs": ["MYSTORE-US"],
    "ownedStoreInfo": {
      "max_stores": 5,
      "number_of_stores_used": 1,
      "owned_stores": [
        {
          "store_name": "MYSTORE",
          "country_code": "US",
          "region_code": "NA",
          "seller_id": "A1PLACEHOLDER",
          "store_id": "00000000-0000-0000-0000-0000000000a1",
          "store_auth_time": "2026-01-01T00:00:00Z",
          "ads_auth_time": "2026-01-01T00:00:00Z",
          "profile_ids": ["1111111111111111"],
          "sync_status": "active"
        }
      ]
    },
    "sharedStoreInfo": {"number_of_stores_used": 0, "shared_stores": []},
    "userInfo": {"email": "seller@example.com", "name": "Test Seller", "google_user_id": "g-1"},
    "subscriptionInfo": {"plan": "Pro", "max_stores": 5, "max_orders": 100000},
    "workspace_config": {
      "userSettingByFolder": {},
      "userSettingBySpreadsheet": {"fbaSpreadsheetId": ""},
      "sa_folder_access": {"ok": true}
    },
    "mcpAccessInfo": {
      "mcp_mode": "open",
      "mcp_permissions": [
        {"store_id": "00000000-0000-0000-0000-0000000000a1", "store_name": "MYSTORE",
         "marketplace": "US", "sp_access": "write", "ads_access": "write"}
      ]
    },
    "credits": {"balance": 50.0, "rates": {}, "route": "official", "routes": [], "topup_url": "https://sellersheetai.com/billing"}
  }
}
