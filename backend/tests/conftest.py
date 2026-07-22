import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest_asyncio.fixture
async def async_client():
    """
    Provides an asynchronous HTTP client configured with ASGITransport 
    for testing FastAPI endpoints without starting a live web server.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
