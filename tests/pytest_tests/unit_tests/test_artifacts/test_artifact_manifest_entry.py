import base64
import os
from logging import getLogger
from pathlib import Path

from wandb.sdk.artifacts.artifact import Artifact
from wandb.sdk.artifacts.artifact_manifest_entry import ArtifactManifestEntry

logger = getLogger(__name__)


def test_repr():
    entry = ArtifactManifestEntry(
        path="foo",
        digest="",
        ref="baz",
        birth_artifact_id="qux",
        size=123,
        extra={"quux": "corge"},
        local_path="grault",
    )
    assert eval(repr(entry)) == entry

    blank_entry = ArtifactManifestEntry(
        path="foo", digest="bar", ref="", birth_artifact_id="", size=0
    )
    assert (
        repr(blank_entry) == "ArtifactManifestEntry"
        "(path='foo', digest='bar', ref='', birth_artifact_id='', size=0)"
    )
    assert entry != blank_entry
    assert entry != repr(entry)

    short_entry = ArtifactManifestEntry(path="foo", digest="barr")
    assert repr(short_entry) == "ArtifactManifestEntry(path='foo', digest='barr')"
    assert entry != short_entry


def base64_decode(data):
    padding_needed = 4 - (len(data) % 4)
    if padding_needed:
        data += "=" * padding_needed
    return base64.b64decode(data)


def test_manifest_download(monkeypatch):
    artifact = Artifact("mnist", type="dataset")
    short_entry = ArtifactManifestEntry(path="foo", digest="barr")
    assert repr(short_entry) == "ArtifactManifestEntry(path='foo', digest='barr')"
    short_entry._parent_artifact = artifact

    abspath_to_cur_dir = os.path.dirname(os.path.abspath(__file__))
    default_cache = Path("default_cache")

    monkeypatch.setattr(
        short_entry._parent_artifact.manifest.storage_policy,
        "load_reference",
        lambda x, y, **kwargs: default_cache,
    )
    monkeypatch.setattr(
        short_entry._parent_artifact.manifest.storage_policy,
        "load_file",
        lambda x, y, **kwargs: default_cache,
    )

    short_entry.path = default_cache
    fpath = short_entry.download(root=abspath_to_cur_dir, skip_cache=True)
    assert fpath.endswith("unit_tests/test_artifacts/default_cache")
