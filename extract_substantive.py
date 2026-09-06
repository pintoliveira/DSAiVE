#!/usr/bin/env python3
"""
Extract only substantive body-text paragraphs from the DOCX, using Word's
own paragraph styles (Heading/TOC/Caption/Title) to reliably distinguish
structure from prose -- instead of guessing from word count alone.
"""

import subprocess
import xml.etree.ElementTree as ET
import json

DOCX = "/root/.claude/uploads/6e8f4fa8-a873-5be2-ac5a-d3fa317a1a3e/a715a8a1-Projecto_tese_09072026.docx"

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
ns = {'w': W_NS}

EXCLUDE_STYLES = {
    'Heading1', 'Heading2', 'Heading20', 'Heading3', 'Title',
    'TOC1', 'TOC2', 'TOC3', 'TOCHeading',
    'ImageCaption', 'CaptionedFigure', 'tablecaption',
}

MIN_WORDS = 12


def get_document_xml(docx_path):
    result = subprocess.run(
        ['unzip', '-p', docx_path, 'word/document.xml'],
        capture_output=True, text=True, check=True
    )
    return result.stdout


def extract_all(docx_path):
    """Return list of dicts: index, text, style, substantive (bool)."""
    xml_text = get_document_xml(docx_path)
    root = ET.fromstring(xml_text)

    all_paras = []
    for i, para in enumerate(root.findall('.//w:p', ns)):
        pstyle_el = para.find('.//w:pStyle', ns)
        style = pstyle_el.get(f'{{{W_NS}}}val') if pstyle_el is not None else 'Normal'

        texts = para.findall('.//w:t', ns)
        text = ''.join(t.text for t in texts if t.text).strip()

        if not text:
            continue

        word_count = len(text.split())
        is_caption = text.startswith(('Figure ', 'Table '))
        substantive = (
            style not in EXCLUDE_STYLES
            and word_count >= MIN_WORDS
            and not is_caption
        )

        all_paras.append({
            'index': i,
            'style': style,
            'word_count': word_count,
            'text': text,
            'substantive': substantive,
        })

    return all_paras


if __name__ == '__main__':
    all_paras = extract_all(DOCX)
    substantive = [p for p in all_paras if p['substantive']]
    skipped = [p for p in all_paras if not p['substantive']]

    print(f"Total non-empty paragraphs: {len(all_paras)}")
    print(f"Substantive (to humanize): {len(substantive)}")
    print(f"Skipped (structural/short): {len(skipped)}")

    with open('all_paragraphs_classified.json', 'w', encoding='utf-8') as f:
        json.dump(all_paras, f, ensure_ascii=False, indent=2)

    with open('substantive_paragraphs.json', 'w', encoding='utf-8') as f:
        json.dump(substantive, f, ensure_ascii=False, indent=2)

    print("\nSaved: all_paragraphs_classified.json, substantive_paragraphs.json")

    print("\n--- Sample of SKIPPED (verify these are correctly structural) ---")
    for p in skipped[20:35]:
        print(f"  [{p['index']}] ({p['style']}, {p['word_count']}w): {p['text'][:90]}")

    print("\n--- Sample of SUBSTANTIVE (verify these are correctly real prose) ---")
    for p in substantive[:10]:
        print(f"  [{p['index']}] ({p['style']}, {p['word_count']}w): {p['text'][:90]}")
