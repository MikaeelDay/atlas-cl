from pathlib import Path

from atlas.state import State, is_initialized, load_state, save_state


def test_state_starts_empty():
    s = State()
    assert not s.is_done("auth")
    assert s.completed_ids() == set()


def test_mark_done_and_undone():
    s = State()
    s.mark_done("auth")
    assert s.is_done("auth")
    assert "auth" in s.completed_ids()

    s.mark_undone("auth")
    assert not s.is_done("auth")


def test_save_and_reload_roundtrip(tmp_path: Path):
    s = State()
    s.mark_done("db_schema")
    s.mark_done("auth")
    save_state(s, tmp_path)

    reloaded = load_state(tmp_path)
    assert reloaded.completed_ids() == {"db_schema", "auth"}


def test_load_state_when_missing_returns_empty(tmp_path: Path):
    s = load_state(tmp_path)
    assert s.completed_ids() == set()


def test_is_initialized(tmp_path: Path):
    assert not is_initialized(tmp_path)
    (tmp_path / ".atlas").mkdir()
    (tmp_path / ".atlas" / "spec.yaml").write_text("project_name: x\nsections: []\n")
    assert is_initialized(tmp_path)