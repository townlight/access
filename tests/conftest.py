import pytest

import townlight_access.main as main_module


TEST_WRITE_TOKEN = "test-write-token"


@pytest.fixture(autouse=True)
def isolated_default_data_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("TOWNLIGHT_ACCESS_DATA_DIR", str(tmp_path / "townlight_access-data"))
    # Keep the default SQLite path hermetic: do not pick up a shell DATABASE_URL.
    monkeypatch.delenv("DATABASE_URL", raising=False)
    # Configure the durable-write guard so persistence tests can authorize writes.
    monkeypatch.setenv("TOWNLIGHT_ACCESS_TRUSTED_WRITE_TOKEN", TEST_WRITE_TOKEN)
    yield
    main_module._dispose_review_repository()
    main_module._review_db_url = None
