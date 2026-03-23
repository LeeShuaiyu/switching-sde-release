import os
import tempfile
import unittest
from pathlib import Path

from switching_sde.artifacts.registry import ArtifactRecord, ArtifactRegistry
from switching_sde.artifacts.resolver import ArtifactResolver


class TestArtifactResolverPriority(unittest.TestCase):
    def test_priority_cli_then_link_then_path(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            repo = td_path / "repo"
            repo.mkdir()
            (repo / "assets" / "linked" / "table").mkdir(parents=True)

            direct = td_path / "direct.csv"
            direct.write_text("x", encoding="utf-8")

            linked = repo / "assets" / "linked" / "table" / "direct.csv"
            os.symlink(direct, linked)

            cli_file = td_path / "cli.csv"
            cli_file.write_text("y", encoding="utf-8")

            reg = ArtifactRegistry(
                version=1,
                legacy_root="",
                generated_at="",
                records=[
                    ArtifactRecord(
                        artifact_id="1",
                        kind="table",
                        scenario="",
                        method="",
                        seed=None,
                        data_version="",
                        split_hash="",
                        path=str(direct),
                        sha1="",
                        status="ready",
                    )
                ],
            )
            resolver = ArtifactResolver(registry=reg, repo_root=repo)
            self.assertEqual(resolver.resolve(kind="table", cli_path=str(cli_file)), cli_file.resolve())
            self.assertEqual(resolver.resolve(kind="table"), linked.resolve())


if __name__ == "__main__":
    unittest.main()
