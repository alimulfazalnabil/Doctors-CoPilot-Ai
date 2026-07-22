# ==========================================
# Azure Cosmos DB NoSQL Ledger & Backup Definitions
# ==========================================

resource "azurerm_cosmosdb_account" "cosmos_ledger" {
  name                = "${local.prefix}-cosmos-ledger-${random_string.suffix.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level       = "Session"
    max_staleness_prefix    = 100
    max_interval_in_seconds = 5
  }

  geo_location {
    location          = azurerm_resource_group.rg.location
    failover_priority = 0
  }

  # Enterprise Backup Policy (Continuous backup mode for compliance and point-in-time restore)
  backup {
    type = "Continuous"
    tier = "Continuous7Days"
  }

  tags = {
    Environment = "Production"
    Compliance  = "HIPAA"
    DataLayer   = "AuditLedger"
  }
}

resource "azurerm_cosmosdb_sql_database" "clinical_db" {
  name                = "ClinicalLedgerDB"
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.cosmos_ledger.name
}

resource "azurerm_cosmosdb_sql_container" "audit_ledger_container" {
  name                = "AppendOnlyLedger"
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.cosmos_ledger.name
  database_name       = azurerm_cosmosdb_sql_database.clinical_db.name
  partition_key_path  = "/consultation_id"
  throughput          = 600

  # Strict indexing policy optimized for consultation ID and timestamp lookups while conserving RU costs
  indexing_policy {
    indexing_mode = "consistent"

    included_path {
      path = "/*"
    }

    excluded_path {
      path = "/payload/_etag/?_id"
    }
  }

  # Unique key policy to enforce versioning uniqueness per consultation
  unique_key {
    paths = ["/consultation_id", "/version"]
  }
}
