from atlas.matcher import match_file, path_matches_pattern, sections_touched
from atlas.spec import Spec, SpecNode


def make_spec() -> Spec:
    return Spec(
        project_name="demo-shop",
        nodes=[
            SpecNode(id="auth", name="Auth", paths=["auth/**"]),
            SpecNode(id="catalog", name="Catalog", paths=["catalog/**", "shared/search.py"]),
        ],
    )


def test_glob_star_star_matches_nested_files():
    assert path_matches_pattern("auth/views.py", "auth/**")
    assert path_matches_pattern("auth/sub/deep.py", "auth/**")
    assert not path_matches_pattern("users/views.py", "auth/**")


def test_glob_star_star_matches_directory_itself():
    assert path_matches_pattern("auth", "auth/**")


def test_exact_file_pattern():
    assert path_matches_pattern("shared/search.py", "shared/search.py")
    assert not path_matches_pattern("shared/other.py", "shared/search.py")


def test_windows_style_paths_are_normalized():
    assert path_matches_pattern("auth\\views.py", "auth/**")


def test_match_file_returns_matching_nodes():
    spec = make_spec()
    result = match_file(spec, "auth/views.py")
    assert [n.id for n in result.matched_nodes] == ["auth"]
    assert not result.is_unmatched


def test_match_file_unmatched_when_no_pattern_fits():
    spec = make_spec()
    result = match_file(spec, "docs/readme.md")
    assert result.is_unmatched
    assert result.matched_nodes == []


def test_file_can_match_multiple_sections():
    spec = Spec(
        project_name="x",
        nodes=[
            SpecNode(id="a", name="A", paths=["shared/**"]),
            SpecNode(id="b", name="B", paths=["shared/utils.py"]),
        ],
    )
    result = match_file(spec, "shared/utils.py")
    assert {n.id for n in result.matched_nodes} == {"a", "b"}


def test_sections_touched_groups_by_section():
    spec = make_spec()
    touched = sections_touched(
        spec, ["auth/views.py", "auth/models.py", "catalog/list.py", "docs/x.md"]
    )
    assert touched == {
        "auth": ["auth/views.py", "auth/models.py"],
        "catalog": ["catalog/list.py"],
    }