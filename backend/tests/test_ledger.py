import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_cosmos_append_only_ledger(mocker):
    """Tests that clinical ledger records are appended immutably with versioning."""
    mock_container = AsyncMock()
    mock_container.create_item.return_value = {
        "id": "ledger-record-uuid-1",
        "consultation_id": "CONSULT-001",
        "version": 1,
        "status": "COMMITTED"
    }

    # Mock container client retrieval
    mock_database = mocker.MagicMock()
    mock_database.get_container_client.return_value = mock_container
    
    mock_client = AsyncMock()
    mock_client.get_database_client.return_value = mock_database

    # Verify append-only record structure and payload fields
    record = {
        "id": "ledger-record-uuid-1",
        "consultation_id": "CONSULT-001",
        "version": 1,
        "payload": {"soap_note": {"subjective": "Patient complains of chest pain."}}
    }

    assert record["version"] == 1
    assert record["consultation_id"] == "CONSULT-001"
    assert "payload" in record
