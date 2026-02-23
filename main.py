from __future__ import annotations

import json
import os
import re
import zipfile
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional, List, Iterator, Tuple
import pandas as pd 
import streamlit as st 
from workflow.graph import create_app  



graph_app = create_app()
# -----------------------------
# Helpers
# -----------------------------
def safe_slug(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9 _-]+", "", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return s or "blog"


def bundle_zip(md_text: str, md_filename: str) -> bytes:
    
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(md_filename, md_text.encode("utf-8"))
    return buf.getvalue()


def try_stream(graph_app, inputs: Dict[str, Any]) -> Iterator[Tuple[str, Any]]:
    try:
        for step in graph_app.stream(inputs, stream_mode="updates"):
            yield ("updates", step)
        out = graph_app.invoke(inputs)
        yield ("final", out)
        return
    except Exception:
        pass

    try:
        for step in graph_app.stream(inputs, stream_mode="values"):
            yield ("values", step)
        out = graph_app.invoke(inputs)
        yield ("final", out)
        return
    except Exception:
        pass

    out = graph_app.invoke(inputs)
    yield ("final", out)


def extract_latest_state(current_state: Dict[str, Any], step_payload: Any) -> Dict[str, Any]:
    if isinstance(step_payload, dict):
        if len(step_payload) == 1 and isinstance(next(iter(step_payload.values())), dict):
            inner = next(iter(step_payload.values()))
            current_state.update(inner)
        else:
            current_state.update(step_payload)
    return current_state


# -----------------------------
# Past blogs helpers
# -----------------------------
def list_past_blogs() -> List[Path]:
    cwd = Path(".")
    files = [p for p in cwd.glob("*.md") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def read_md_file(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def extract_title_from_md(md: str, fallback: str) -> str:
    for line in md.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or fallback
    return fallback


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Blog Writer", layout="wide")

st.markdown("""
<style>
/* Streamlit Top Header Bar */
header[data-testid="stHeader"] {
    background: #0d1117 !important;   /* change to any color */
}

          

/* Main App Background */
.stApp {
    
    background: #111827;        
    color: white;
    font-family: "Inter", sans-serif;
} 

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid #1e293b;
}
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3 {
    color: #38bdf8;
}

/* Title Styling */
h1 {
    font-size: 2.2rem !important;
    font-weight: 700;
    color: #38bdf8;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #9333ea);
    color: white;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    border: none;
    font-weight: 600;
    transition: 0.3s;
}
.stButton > button:hover {
    transform: scale(1.03);
    background: linear-gradient(135deg, #1d4ed8, #7e22ce);
}

/* Tabs UI */
button[data-baseweb="tab"] {
    background: #020617 !important;
    color: white !important;
    border-radius: 10px !important;
    margin-right: 6px !important;
    padding: 8px 16px !important;
    border: 1px solid #1e293b !important;
}
button[data-baseweb="tab"]:hover {
    background: #1e293b !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: #2563eb !important;
    color: white !important;
}

/* Text Area & Inputs */
textarea, input {
    background: #020617 !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid #1e293b !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    border: 1px solid #1e293b;
}

/* Download Buttons */
.stDownloadButton > button {
    background: #22c55e !important;
    border-radius: 10px !important;
    font-weight: bold;
}

/* Mobile Responsive */
@media (max-width: 768px) {
    h1 {
        font-size: 1.6rem !important;
    }
    section[data-testid="stSidebar"] {
        width: 100% !important;
    }
}

</style>
""", unsafe_allow_html=True)



st.title("🧠 AI Blog Writing Multi Agent System")


# Sidebar
with st.sidebar:
    st.header("Generate New Blog")
    topic = st.text_area("Enter the Topic", height=120)
    as_of = st.date_input("As-of date", value=date.today())
    run_btn = st.button("🚀 Generate Blog", type="primary")

    # Past blogs
    st.divider()
    st.subheader("Past Blogs")

    past_files = list_past_blogs()
    if not past_files:
        st.caption("No saved blogs found.")
        selected_md_file = None
    else:
        options = []
        file_by_label = {}
        for p in past_files[:50]:
            try:
                md_text = read_md_file(p)
                title = extract_title_from_md(md_text, p.stem)
            except Exception:
                title = p.stem
            label = f"{title} · {p.name}"
            options.append(label)
            file_by_label[label] = p

        selected_label = st.radio("Select blog", options=options)
        selected_md_file = file_by_label[selected_label]

        if st.button("📂 Load Blog"):
            md_text = read_md_file(selected_md_file)
            st.session_state["last_out"] = {
                "plan": None,
                "evidence": [],
                "final": md_text,
            }


# Storage
if "last_out" not in st.session_state:
    st.session_state["last_out"] = None


# Tabs (NO IMAGES TAB)
tab_plan, tab_evidence, tab_preview, tab_logs = st.tabs(
    ["🧩 Plan", "🔎 Evidence", "📝 Markdown Preview", "🧾 Logs"]
)

logs = []


def log(msg: str):
    logs.append(msg)


# Run Agent
if run_btn:
    if not topic.strip():
        st.warning("Enter topic")
        st.stop()

    inputs = {
        "topic": topic.strip(),
        "mode": "",
        "needs_research": False,
        "queries": [],
        "evidence": [],
        "plan": None,
        "as_of": as_of.isoformat(),
        "recency_days": 7,
        "sections": [],
        "final": "",
    }

    status = st.status("Running graph...", expanded=True)
    progress_area = st.empty()
    current_state = {}
    last_node = None

    for kind, payload in try_stream(graph_app, inputs):
        if kind in ("updates", "values"):
            node_name = None
            if isinstance(payload, dict) and len(payload) == 1:
                node_name = list(payload.keys())[0]

            if node_name and node_name != last_node:
                status.write(f"➡️ Node: `{node_name}`")
                last_node = node_name

            current_state = extract_latest_state(current_state, payload)

            summary = {
                "mode": current_state.get("mode"),
                "needs_research": current_state.get("needs_research"),
                "queries": current_state.get("queries", [])[:3],
                "evidence_count": len(current_state.get("evidence", []) or []),
            }
            progress_area.json(summary)
            log(json.dumps(payload, default=str)[:1000])

        elif kind == "final":
            st.session_state["last_out"] = payload
            status.update(label="✅ Done", state="complete", expanded=False)


# Render Output
out = st.session_state.get("last_out")

if out:
    # PLAN TAB
    with tab_plan:
        st.subheader("Plan")
        plan = out.get("plan")
        if plan:
            if hasattr(plan, "model_dump"):
                plan = plan.model_dump()
            st.json(plan)
        else:
            st.info("No plan data.")

    # EVIDENCE TAB
    with tab_evidence:
        st.subheader("Evidence")
        evidence = out.get("evidence") or []
        if evidence:
            st.dataframe(pd.DataFrame(evidence), use_container_width=True)
        else:
            st.info("No evidence returned.")

   

    # PREVIEW TAB
    with tab_preview:
        st.subheader("Markdown Preview")
        final_md = out.get("final", "")
        st.markdown(final_md)

        blog_title = extract_title_from_md(final_md, "blog")
        filename = f"{safe_slug(blog_title)}.md"
        zip_filename = f"{safe_slug(blog_title)}.zip"

    # ===============================
    # FIX: SAVE FILE TO DISK
    # ===============================
        os.makedirs("downloads", exist_ok=True)
        md_path = os.path.join("downloads", filename)
        zip_path = os.path.join("downloads", zip_filename)

    # Save markdown file
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(final_md)

    # Save zip file
    zip_data = bundle_zip(final_md, filename)
    with open(zip_path, "wb") as f:
        f.write(zip_data)

    # Download buttons (file-based)
    with open(md_path, "rb") as f:
        st.download_button("⬇️ Download Markdown", f, file_name=filename)

    with open(zip_path, "rb") as f:
        st.download_button("📦 Download ZIP", f, file_name=zip_filename)

    # LOGS TAB
    with tab_logs:
        st.subheader("Logs")
        st.text_area("Logs", "\n".join(logs[-100:]), height=500)

else:
    st.info("Enter topic and generate blog.")