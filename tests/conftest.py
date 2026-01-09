# tests/conftest.py
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import engine
from app.models import Base

@pytest.fixture
def client():

    Base.metadata.create_all(bind=engine)

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=engine)
