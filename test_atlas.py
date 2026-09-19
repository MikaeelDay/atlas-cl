from pathlib import Path
from atlas.spec import Spec, SpecNode, save_spec, load_spec
from atlas.state import load_state, save_state
from atlas.matcher import sections_touched

# یه پروژه‌ی نمونه بساز
spec = Spec(
    project_name="my-shop",
    nodes=[
        SpecNode(id="db", name="Database Schema", paths=["db/**"]),
        SpecNode(id="auth", name="User Auth", paths=["auth/**"], depends_on=["db"]),
    ],
)
save_spec(spec, Path("demo_spec.yaml"))
print("Spec saved. Ready to start:", [n.id for n in spec.roots()])

# فرض کن کاربر روی auth کار کرده
touched = sections_touched(spec, ["auth/views.py", "auth/models.py"])
print("Sections touched:", touched)

# وضعیت رو تکمیل کن
state = load_state(Path("."))
state.mark_done("db")
save_state(state, Path("."))
print("Ready now:", [n.id for n in spec.ready_nodes(state.completed_ids())])