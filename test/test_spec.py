import pytest

from atlas.spec import Spec, SpecError, SpecNode, load_spec, save_spec


def test_roots_returns_nodes_with_no_dependencies():
    spec = Spec(
        project_name="x",
        nodes=[
            SpecNode(id="a", name="A"),
            SpecNode(id="b", name="B", depends_on=["a"]),
        ],
    )
    assert [n.id for n in spec.roots()] == ["a"]


def test_ready_nodes_respects_dependencies():
    spec = Spec(
        project_name="x",
        nodes=[
            SpecNode(id="a", name="A"),
            SpecNode(id="b", name="B", depends_on=["a"]),
            SpecNode(id="c", name="C", depends_on=["a", "b"]),
        ],
    )
    assert [n.id for n in spec.ready_nodes(set())] == ["a"]
    assert [n.id for n in spec.ready_nodes({"a"})] == ["b"]
    assert [n.id for n in spec.ready_nodes({"a", "b"})] == ["c"]

def test_validate_rejects_duplicate_ids():
    spec = Spec(
        project_name="x",
        nodes=[SpecNode(id="a", name="A"), SpecNode(id="a", name="A2")],
    )
    with pytest.raises(SpecError, match="Duplicate"):
        spec.validate()


def test_validate_rejects_unknown_dependency():
    spec = Spec(project_name="x", nodes=[SpecNode(id="a", name="A", depends_on=["ghost"])])
    with pytest.raises(SpecError, match="unknown"):
        spec.validate()


def test_validate_rejects_cycles():
    spec = Spec(
        project_name="x",
        nodes=[
            SpecNode(id="a", name="A", depends_on=["b"]),
            SpecNode(id="b", name="B", depends_on=["a"]),
        ],
    )
    with pytest.raises(SpecError, match="Circular"):
        spec.validate()

def test_save_and_load_roundtrip(tmp_path):
    spec = Spec(
        project_name="demo",
        nodes=[
            SpecNode(id="a", name="A", description="desc", paths=["a/**"]),
            SpecNode(id="b", name="B", depends_on=["a"]),
        ],
    )
    path = tmp_path / "spec.yaml"
    save_spec(spec, path)
    reloaded = load_spec(path)

    assert reloaded.project_name == "demo"
    assert [n.id for n in reloaded.nodes] == ["a", "b"]
    assert reloaded.get("a").paths == ["a/**"]
    assert reloaded.get("b").depends_on == ["a"]


def test_load_missing_file_raises():
    with pytest.raises(SpecError, match="not found"):
        load_spec("does_not_exist.yaml")