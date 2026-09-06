#!/usr/bin/env python3
"""
Rebuild the IEEE workshop paper DOCX with humanized paragraph text
substituted in place, preserving formatting. Leaves title, authors,
index terms, section headings, figure captions, direct manager-quote
paragraphs, the generative-AI declaration, and the bibliography untouched.
"""

import json
import os
import shutil
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import copy

SRC_DOCX = "/root/.claude/uploads/6e8f4fa8-a873-5be2-ac5a-d3fa317a1a3e/e54bdaba-IEEE_W02_workshopdocx_v12.docx"
OUT_DOCX = "IEEE_W02_workshopdocx_v12_humanized.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# Register the same namespace prefixes the source document declares
result = subprocess.run(["unzip", "-p", SRC_DOCX, "word/document.xml"], capture_output=True, check=True)
xml_bytes = result.stdout
header = xml_bytes[:3000].decode("utf-8", errors="ignore")
import re
for m in re.finditer(r'xmlns:([\w]+)="([^"]+)"', header):
    ET.register_namespace(m.group(1), m.group(2))
ET.register_namespace("w", W_NS)


def w(tag):
    return f"{{{W_NS}}}{tag}"


def load_humanized_map():
    with open("paper_humanized.json", encoding="utf-8") as f:
        data = json.load(f)
    return {int(k): v for k, v in data.items()}


def replace_paragraph_text(p_elem, new_text):
    runs = p_elem.findall(w("r"))
    rpr = None
    for run in runs:
        candidate = run.find(w("rPr"))
        if candidate is not None:
            rpr = candidate
            break

    for run in runs:
        p_elem.remove(run)
    for hl in p_elem.findall(w("hyperlink")):
        p_elem.remove(hl)

    new_run = ET.Element(w("r"))
    if rpr is not None:
        new_run.append(copy.deepcopy(rpr))
    t_elem = ET.SubElement(new_run, w("t"))
    t_elem.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t_elem.text = new_text

    ppr = p_elem.find(w("pPr"))
    idx = list(p_elem).index(ppr) + 1 if ppr is not None else 0
    p_elem.insert(idx, new_run)


def main():
    humanized = load_humanized_map()
    print(f"Loaded {len(humanized)} humanized paragraphs")

    root = ET.fromstring(xml_bytes)
    paragraphs = root.findall(".//" + w("p"))
    print(f"Found {len(paragraphs)} paragraphs in document")

    replaced = 0
    remaining = set(humanized.keys())
    for i, p in enumerate(paragraphs):
        if i in humanized:
            replace_paragraph_text(p, humanized[i])
            replaced += 1
            remaining.discard(i)

    print(f"Replaced {replaced} paragraphs")
    if remaining:
        print(f"WARNING: indices not found: {sorted(remaining)}")

    new_xml = ET.tostring(root, encoding="UTF-8", xml_declaration=True)

    shutil.copyfile(SRC_DOCX, OUT_DOCX)
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
