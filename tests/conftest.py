"""Isolate all automated tests from private COVEX documents and user data."""
import hashlib
import pytest
from synthetic_fixtures import generate

@pytest.fixture(scope='session')
def synthetic_resources(tmp_path_factory):
    return generate(tmp_path_factory.mktemp('synthetic-resources'))

@pytest.fixture(autouse=True)
def private_test_instance(monkeypatch,synthetic_resources,tmp_path,request):
    import covex_label_manager.storage as storage
    import covex_label_manager.integrity as integrity
    monkeypatch.setattr(storage,'resource_dir',lambda:synthetic_resources)
    monkeypatch.setattr(integrity,'KNOWN_OVERFLOW_PDF',hashlib.sha256((synthetic_resources/'EDROFONIO_MASTER_00.pdf').read_bytes()).hexdigest())
    monkeypatch.setenv('COVEX_LABEL_DATA',str(tmp_path/'isolated-user-data'))

    if hasattr(request.module,'RESOURCE'):monkeypatch.setattr(request.module,'RESOURCE',synthetic_resources)
