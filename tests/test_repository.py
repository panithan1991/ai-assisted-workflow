"""Public packaging and documentation checks, using isolated synthetic fixtures."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repository_checker", ROOT / "tools/check_blueprint.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def file(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_encoded_and_angle_links_resolve_and_code_examples_are_ignored(self):
        page = self.file("README.md", '[Open](<docs/Study%20notes.md#first-heading>)\n'
                         '`[Not a link](missing.md)`\n```text\n[Example](missing.md)\n```\n')
        self.file("docs/Study notes.md", "# First heading\n")
        self.assertEqual(checker.check_markdown_links(self.root, [page]), [])

    def test_missing_heading_and_escaping_document_link_are_rejected(self):
        page = self.file("README.md", "[Broken](docs/notes.md#missing)\n[Escape](../outside.md)\n")
        self.file("docs/notes.md", "# Present\n")
        errors = checker.check_markdown_links(self.root, [page])
        self.assertTrue(any("missing heading anchor" in error for error in errors))
        self.assertTrue(any("broken local link" in error for error in errors))

    def test_duplicate_heading_reference_definitions_and_explicit_ids(self):
        page = self.file("README.md", "[Guide][guide]\n[guide]: docs/notes.md#topic-1\n"
                         "[Special](docs/notes.md#custom)\n")
        self.file("docs/notes.md", '# Topic\n# Topic\n<a id="custom"></a>\n')
        self.assertEqual(checker.check_markdown_links(self.root, [page]), [])

    def test_text_only_package_rejects_private_dirs_and_real_artifact_types(self):
        self.file("README.md", "# Example\n")
        self.file("private/notes.txt", "Never inspect this source as public material")
        self.file("report.pdf", "Not a public template")
        self.file(".env", "PRIVATE_CONFIG=placeholder")
        paths, errors = checker.public_package_files(self.root)
        self.assertEqual([path.name for path in paths], ["README.md"])
        self.assertEqual(len(errors), 3)

    def test_secret_markers_are_detected_but_generic_placeholders_are_allowed(self):
        page = self.file("README.md", "Set API_KEY in your local environment.\n")
        self.assertEqual(checker.public_package_files(self.root)[1], [])
        page.write_text("sk-" + "X" * 30, encoding="utf-8")
        self.assertTrue(any("possible access token" in error
                            for error in checker.public_package_files(self.root)[1]))
        page.write_text("-----BEGIN " + "PRIVATE KEY-----", encoding="utf-8")
        self.assertTrue(any("private-key material" in error
                            for error in checker.public_package_files(self.root)[1]))

    def test_repository_check_is_read_only(self):
        self.file("README.md", "# Example\n")
        before = {path.relative_to(self.root).as_posix(): path.read_bytes()
                  for path in self.root.rglob("*") if path.is_file()}
        checker.public_package_files(self.root)
        checker.check_markdown_links(self.root, [self.root / "README.md"])
        after = {path.relative_to(self.root).as_posix(): path.read_bytes()
                 for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_nonfinite_numbers_are_not_portable_json_records(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            path = self.file("record.json", '{"value":' + token + '}')
            with self.subTest(token=token), self.assertRaises(ValueError):
                checker.read_json(path)


if __name__ == "__main__":
    unittest.main()
