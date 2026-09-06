#!/usr/bin/env python3
"""
Rebuild the thesis DOCX with humanized paragraph text substituted in place,
preserving paragraph formatting (run properties) and leaving every other
paragraph (headings, TOC, captions, tables, bibliography) untouched.
"""

import json
import shutil
import subprocess
import zipfile
import xml.etree.ElementTree as ET

SRC_DOCX = "/root/.claude/uploads/6e8f4fa8-a873-5be2-ac5a-d3fa317a1a3e/a715a8a1-Projecto_tese_09072026.docx"
OUT_DOCX = "Projecto_tese_09072026_humanized.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ns = {"w": W_NS}

NAMESPACES = {
    "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
    "cx": "http://schemas.microsoft.com/office/drawing/2014/chartex",
    "cx1": "http://schemas.microsoft.com/office/drawing/2015/9/8/chartex",
    "cx2": "http://schemas.microsoft.com/office/drawing/2015/10/21/chartex",
    "cx3": "http://schemas.microsoft.com/office/drawing/2016/5/9/chartex",
    "cx4": "http://schemas.microsoft.com/office/drawing/2016/5/10/chartex",
    "cx5": "http://schemas.microsoft.com/office/drawing/2016/5/11/chartex",
    "cx6": "http://schemas.microsoft.com/office/drawing/2016/5/12/chartex",
    "cx7": "http://schemas.microsoft.com/office/drawing/2016/5/13/chartex",
    "cx8": "http://schemas.microsoft.com/office/drawing/2016/5/14/chartex",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "aink": "http://schemas.microsoft.com/office/drawing/2016/ink",
    "am3d": "http://schemas.microsoft.com/office/drawing/2017/model3d",
    "o": "urn:schemas-microsoft-com:office:office",
    "oel": "http://schemas.microsoft.com/office/2019/extlst",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "v": "urn:schemas-microsoft-com:vml",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "w10": "urn:schemas-microsoft-com:office:word",
    "w": W_NS,
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16cex": "http://schemas.microsoft.com/office/word/2018/wordml/cex",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
    "w16": "http://schemas.microsoft.com/office/word/2018/wordml",
    "w16du": "http://schemas.microsoft.com/office/word/2023/wordml/word16du",
    "w16sdtdh": "http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash",
    "w16sdtfl": "http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock",
    "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "wpi": "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
    "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
}

for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


def load_humanized_map():
    merged = {}
    for fname in ("humanized_batch1.json", "humanized_batch2.json", "humanized_batch3.json"):
        with open(fname, encoding="utf-8") as f:
            data = json.load(f)
        for k, v in data.items():
            if v == "SKIP_UNCHANGED":
                continue
            merged[int(k)] = v
    return merged


def replace_paragraph_text(p_elem, new_text):
    """Replace all runs in a <w:p> with a single run carrying the new text,
    preserving the first run's formatting (rPr) and any non-run children
    (pPr, bookmarks, etc.) in their original order/position."""
    w = lambda tag: f"{{{W_NS}}}{tag}"

    runs = p_elem.findall(w("r"))
    rpr = None
    for run in runs:
        candidate = run.find(w("rPr"))
        if candidate is not None:
            rpr = candidate
            break

    # Remove all existing runs and hyperlinks (hyperlinks wrap runs; none
    # expected in these body paragraphs, but drop defensively if present)
    for run in runs:
        p_elem.remove(run)
    for hl in p_elem.findall(w("hyperlink")):
        p_elem.remove(hl)

    new_run = ET.Element(w("r"))
    if rpr is not None:
        import copy
        new_run.append(copy.deepcopy(rpr))
    t_elem = ET.SubElement(new_run, w("t"))
    t_elem.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t_elem.text = new_text

    # Insert after pPr if present, else at the start
    ppr = p_elem.find(w("pPr"))
    if ppr is not None:
        idx = list(p_elem).index(ppr) + 1
    else:
        idx = 0
    p_elem.insert(idx, new_run)


def main():
    humanized = load_humanized_map()
    print(f"Loaded {len(humanized)} humanized paragraphs")

    result = subprocess.run(
        ["unzip", "-p", SRC_DOCX, "word/document.xml"],
        capture_output=True, check=True
    )
    xml_bytes = result.stdout

    root = ET.fromstring(xml_bytes)
    w = lambda tag: f"{{{W_NS}}}{tag}"

    paragraphs = root.findall(".//" + w("p"))
    print(f"Found {len(paragraphs)} paragraphs in document")

    replaced = 0
    missing = []
    remaining = set(humanized.keys())
    for i, p in enumerate(paragraphs):
        if i in humanized:
            replace_paragraph_text(p, humanized[i])
            replaced += 1
            remaining.discard(i)

    print(f"Replaced {replaced} paragraphs")
    if remaining:
        print(f"WARNING: {len(remaining)} indices not found: {sorted(remaining)}")

    new_xml = ET.tostring(root, encoding="UTF-8", xml_declaration=True)

    # Standalone attribute: match common Word output (not strictly required)
    shutil.copyfile(SRC_DOCX, OUT_DOCX)

    # Rewrite word/document.xml inside the copied docx (zip) in place
    import os
    tmp_out = OUT_DOCX + ".tmp"
    with zipfile.ZipFile(SRC_DOCX, "r") as zin:
        with zipfile.ZipFile(tmp_out, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    data = new_xml
                zout.writestr(item, data)
    os.replace(tmp_out, OUT_DOCX)
    print(f"\nWrote {OUT_DOCX}")


if __name__ == "__main__":
    main()
