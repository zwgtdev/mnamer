import json
from typing import Callable
from unittest.mock import MagicMock, patch

import pytest

from mnamer.__version__ import VERSION
from mnamer.settings import Settings
from tests import *


@pytest.mark.parametrize("flag", ("-V", "--version"))
def test_version(flag: str, e2e_run: Callable):
    result = e2e_run(flag)
    assert result.code == 0
    assert result.out == f"mnamer version {VERSION}"


@patch("mnamer.__main__.clear_cache")
def test_directives__cache_clear(
    mock_clear_cache: MagicMock, e2e_run: Callable
):
    result = e2e_run("--no_cache")
    assert result.code == 0
    assert "cache cleared" in result.out
    mock_clear_cache.assert_called_once()


@pytest.mark.parametrize("key", Settings._serializable_fields())
@patch("mnamer.utils.crawl_out")
def test_directives__config_dump(
    mock_crawl_out: MagicMock, key: str, e2e_run: Callable
):
    mock_crawl_out.return_value = None
    result = e2e_run("--config_dump")
    assert result.code == 0
    if key.startswith("api_key"):
        return
    json_out = json.loads(result.out)
    value = DEFAULT_SETTINGS[key]
    expected = getattr(value, "value", value)
    actual = json_out[key]
    assert actual == expected


@pytest.mark.usefixtures("setup_test_path")
def test_id__omdb(e2e_run: Callable):
    result = e2e_run(
        "--batch",
        "--movie_api",
        "omdb",
        "--id-imdb",
        "tt5580390",
        "aladdin.1992.avi",
    )
    assert "Shape of Water" in result.out


@pytest.mark.usefixtures("setup_test_path")
def test_id__tmdb(e2e_run: Callable):
    result = e2e_run(
        "--batch",
        "--movie_api",
        "tmdb",
        "--id-tmdb",
        "475557",
        "Ninja Turtles (1990).mkv",
    )
    assert result.code == 0
    assert "Joker" in result.out


@pytest.mark.usefixtures("setup_test_path")
def test_id__tvdb(e2e_run: Callable):
    result = e2e_run(
        "--batch",
        "--episode_api",
        "tvdb",
        "--id-tvdb",
        "79349",
        "game.of.thrones.01x05-eztv.mp4",
    )
    assert result.code == 0
    assert "Dexter" in result.out


@pytest.mark.usefixtures("setup_test_path")
def test_media__episode_override(e2e_run: Callable):
    result = e2e_run("--batch", "--media", "episode", "aladdin.1992.avi")
    assert result.code == 0
    assert "Processing Episode" in result.out


@pytest.mark.usefixtures("setup_test_path")
def test_media__movie_override(e2e_run: Callable):
    result = e2e_run("--batch", "--media", "movie", "s.w.a.t.2017.s02e01.mkv")
    assert result.code == 0
    assert "Processing Movie" in result.out


# TODO
def test_config_ignore(e2e_run: Callable):
    pass


def test_test(e2e_run: Callable):
    result = e2e_run("--batch", "--test")
    assert result.code == 0
    assert "testing mode" in result.out
