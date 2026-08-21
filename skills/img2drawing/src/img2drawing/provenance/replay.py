from pathlib import Path
from ..core.session import DrawingSession
from ..render.pillow_pencil_contact import render

def render_session_at(session_path: str|Path, cursor: int, out: str|Path, *, supersample=3) -> Path:
    session=DrawingSession.load(session_path,verify=True)
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True)
    render(session.history.state_at(cursor),p,supersample=supersample)
    return p
