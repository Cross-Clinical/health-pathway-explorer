"""Health Pathway Explorer — Cross Clinical educational Space."""

from __future__ import annotations

import json
from pathlib import Path

import gradio as gr

from input_guard import DISCLAIMER, guard_input

DATA = json.loads((Path(__file__).parent / "data" / "pathways.json").read_text())
BY_ID = {p["id"]: p for p in DATA}
TITLES = [f"{p['title']} ({p['id']})" for p in DATA]


def _resolve(label: str):
    pid = label.rsplit("(", 1)[-1].rstrip(")")
    return BY_ID[pid]


def search(query: str) -> str:
    blocked = guard_input(query)
    if blocked:
        return blocked
    q = (query or "").strip().lower()
    if not q:
        return "Enter a keyword (e.g. nursing, surgery, rehab, imaging)."
    hits = [
        p
        for p in DATA
        if q in p["title"].lower()
        or q in p["discipline"].lower()
        or q in p["summary"].lower()
        or q in p["typical_shadowing"].lower()
    ]
    if not hits:
        return "No pathways matched. Try: nursing, PA, physician, PT, pharmacy, emergency."
    lines = []
    for p in hits:
        lines.append(
            f"### {p['title']}\n"
            f"{p['summary']}\n\n"
            f"**Education:** {p['education']}\n\n"
            f"**Typical shadowing:** {p['typical_shadowing']}\n\n"
            f"**Sources:** " + ", ".join(p["sources"])
        )
    return "\n\n---\n\n".join(lines)


def compare(a_label: str, b_label: str) -> str:
    a, b = _resolve(a_label), _resolve(b_label)
    return (
        f"## {a['title']} vs {b['title']}\n\n"
        f"| | {a['title']} | {b['title']} |\n|---|---|---|\n"
        f"| Discipline | {a['discipline']} | {b['discipline']} |\n"
        f"| Education | {a['education']} | {b['education']} |\n"
        f"| Shadowing focus | {a['typical_shadowing']} | {b['typical_shadowing']} |\n"
        f"| Outlook note | {a['outlook_note']} | {b['outlook_note']} |\n\n"
        f"**{a['title']} summary:** {a['summary']}\n\n"
        f"**{b['title']} summary:** {b['summary']}\n\n"
        f"*Sources are public career pages — verify locally. Educational use only.*"
    )


def detail(label: str) -> str:
    p = _resolve(label)
    src = "\n".join(f"- {s}" for s in p["sources"])
    return (
        f"# {p['title']}\n\n"
        f"**Discipline:** `{p['discipline']}`\n\n"
        f"{p['summary']}\n\n"
        f"## Education\n{p['education']}\n\n"
        f"## Typical shadowing\n{p['typical_shadowing']}\n\n"
        f"## Outlook\n{p['outlook_note']}\n\n"
        f"## Sources\n{src}"
    )


with gr.Blocks(title="Health Pathway Explorer") as demo:
    gr.Markdown(
        f"# Health Pathway Explorer\n\n"
        f"**{DISCLAIMER}**\n\n"
        f"Part of [Cross Clinical OSS](https://github.com/Cross-Clinical/suite-index) · "
        f"[ProMedNet](https://crossclinical.com)"
    )
    with gr.Tab("Search"):
        q = gr.Textbox(label="Keyword")
        out_s = gr.Markdown()
        q.submit(search, q, out_s)
        gr.Button("Search").click(search, q, out_s)
    with gr.Tab("Browse"):
        pick = gr.Dropdown(TITLES, label="Pathway", value=TITLES[0])
        out_d = gr.Markdown()
        pick.change(detail, pick, out_d)
        demo.load(detail, pick, out_d)
    with gr.Tab("Compare"):
        a = gr.Dropdown(TITLES, label="A", value=TITLES[0])
        b = gr.Dropdown(TITLES, label="B", value=TITLES[2])
        out_c = gr.Markdown()
        gr.Button("Compare").click(compare, [a, b], out_c)

if __name__ == "__main__":
    demo.launch()
