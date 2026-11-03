"""Offline checks for the YouTube page, using fakes instead of the network."""

import ast
import re
import types
import unittest
from pathlib import Path

PAGE = Path(__file__).parents[1] / "vita" / "pages" / "📥 YouTube Downloader.py"


def load_functions(names, namespace):
    tree = ast.parse(PAGE.read_text(encoding="utf-8"))
    definitions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in names
    ]
    module = ast.Module(body=definitions, type_ignores=[])
    exec(compile(module, str(PAGE), "exec"), namespace)
    return namespace


class FakeProgress:
    def progress(self, *args, **kwargs):
        pass

    def empty(self):
        pass


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.check = load_functions({"check_youtube_link"}, {"re": re})[
            "check_youtube_link"
        ]

    def test_watch_and_shorts_links_are_accepted(self):
        for link in (
            "https://www.youtube.com/watch?v=abc",
            "https://youtube.com/watch?v=abc",
            "https://m.youtube.com/watch?v=abc",
            "https://www.youtube.com/shorts/abc",
        ):
            with self.subTest(link=link):
                self.assertTrue(self.check(link))

    def test_other_links_are_rejected(self):
        for link in (
            "",
            "https://wwwXyoutube.com/watch?v=abc",
            "https://www.youtubeXcom/watch?v=abc",
            "https://www.youtube.com/channel/abc",
            "https://example.com/?u=https://www.youtube.com/watch",
        ):
            with self.subTest(link=link):
                self.assertFalse(self.check(link))


class DownloadTests(unittest.TestCase):
    def test_missing_stream_shows_an_error(self):
        errors = []
        streams = types.SimpleNamespace(
            filter=lambda **kwargs: types.SimpleNamespace(first=lambda: None)
        )
        st = types.SimpleNamespace(
            session_state=types.SimpleNamespace(),
            progress=lambda *args, **kwargs: FakeProgress(),
            error=errors.append,
            balloons=lambda: None,
            write=lambda *args: None,
        )
        download = load_functions(
            {"download_video"},
            {
                "st": st,
                "YouTube": lambda *args, **kwargs: types.SimpleNamespace(
                    streams=streams
                ),
                "show_percent_progress": None,
            },
        )["download_video"]
        download("https://www.youtube.com/watch?v=abc")
        self.assertEqual(
            errors, ["No downloadable stream was found for this video."]
        )


if __name__ == "__main__":
    unittest.main()
