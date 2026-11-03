"""Reject drift between the source pin, bootstrap receipt and installed wheel."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def bootstrap():
    path = Path(__file__).resolve().parents[1] / 'scripts/install-core-candidate.py'
    spec = importlib.util.spec_from_file_location('core_candidate_install', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('drift', ['none', 'source_commit', 'distribution', 'version', 'installed_version', 'artifact_hash'])
def test_installed_core_provenance(bootstrap, monkeypatch, tmp_path, drift):
    pin = {'commit': 'a' * 40, 'distribution': 'townlight-core', 'version': '1.3.0.dev2'}
    receipt = {'source_commit': pin['commit'], 'distribution': pin['distribution'],
               'version': pin['version'], 'sha256': 'b' * 64}
    installed_version = pin['version']
    artifact_hash = receipt['sha256']
    if drift in receipt:
        receipt[drift] = 'wrong'
    elif drift == 'installed_version':
        installed_version = '1.2.0'
    elif drift == 'artifact_hash':
        artifact_hash = 'c' * 64
    installed = SimpleNamespace(version=installed_version, read_text=lambda _: json.dumps(
        {'archive_info': {'hashes': {'sha256': artifact_hash}}}))
    monkeypatch.setattr(bootstrap.metadata, 'distribution', lambda _: installed)
    path = tmp_path / 'receipt.json'
    path.write_text(json.dumps(receipt))
    if drift == 'none':
        bootstrap.verify_installed(pin, path)
    else:
        with pytest.raises(ValueError, match='Core'):
            bootstrap.verify_installed(pin, path)


def test_missing_receipt_fails_closed(bootstrap, tmp_path):
    with pytest.raises(FileNotFoundError):
        bootstrap.verify_installed({}, tmp_path / 'missing.json')
