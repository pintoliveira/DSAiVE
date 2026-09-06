#!/usr/bin/env python3
"""
Extract paragraphs from DOCX and apply prompts sequentially.
Approach 1: Simple paragraph-by-paragraph extraction.
"""

import subprocess
import xml.etree.ElementTree as ET
import json
from pathlib import Path
from typing import List, Dict


def extract_paragraphs(docx_path: str) -> List[str]:
    """
    Extract all non-empty paragraphs from DOCX file.

    Args:
        docx_path: Path to .docx file

    Returns:
        List of paragraph strings
    """
    result = subprocess.run(
        ['unzip', '-p', docx_path, 'word/document.xml'],
        capture_output=True, text=True, check=True
    )

    root = ET.fromstring(result.stdout)
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    paragraphs = []
    for para in root.findall('.//w:p', ns):
        texts = para.findall('.//w:t', ns)
        para_text = ''.join([t.text for t in texts if t.text]).strip()

        # Skip empty paragraphs
        if para_text:
            paragraphs.append(para_text)

    return paragraphs


def save_paragraphs_json(paragraphs: List[str], output_path: str = "paragraphs.json"):
    """Save extracted paragraphs to JSON file."""
    data = {
        "total_paragraphs": len(paragraphs),
        "paragraphs": [
            {
                "index": i,
                "text": para
            }
            for i, para in enumerate(paragraphs)
        ]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ Saved {len(paragraphs)} paragraphs to {output_path}")


def save_paragraphs_csv(paragraphs: List[str], output_path: str = "paragraphs.csv"):
    """Save extracted paragraphs to CSV file."""
    import csv

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['index', 'text'])
        for i, para in enumerate(paragraphs):
            writer.writerow([i, para])

    print(f"✓ Saved {len(paragraphs)} paragraphs to {output_path}")


def print_stats(paragraphs: List[str]):
    """Print document statistics."""
    total_chars = sum(len(p) for p in paragraphs)
    avg_length = total_chars / len(paragraphs) if paragraphs else 0

    print("\n" + "="*70)
    print("DOCUMENT STATISTICS")
    print("="*70)
    print(f"Total paragraphs:     {len(paragraphs)}")
    print(f"Total characters:     {total_chars:,}")
    print(f"Avg chars/paragraph:  {avg_length:.0f}")
    print(f"Longest paragraph:    {max(len(p) for p in paragraphs) if paragraphs else 0} chars")
    print(f"Shortest paragraph:   {min(len(p) for p in paragraphs) if paragraphs else 0} chars")
    print("="*70 + "\n")


def process_paragraphs_template(paragraphs: List[str], user_prompt: str):
    """
    Template for processing paragraphs sequentially.

    Args:
        paragraphs: List of paragraph texts
        user_prompt: Your prompt template (use {paragraph} as placeholder)
    """
    results = []

    for i, para in enumerate(paragraphs, 1):
        print(f"[{i}/{len(paragraphs)}] Processing paragraph...")

        # Build the full prompt
        full_prompt = user_prompt.format(paragraph=para)

        # TODO: Replace with your Claude API call
        # response = client.messages.create(
        #     model="claude-opus-4-1",
        #     max_tokens=1024,
        #     messages=[{"role": "user", "content": full_prompt}]
        # )
        # result_text = response.content[0].text

        # For now, just a placeholder
        result_text = f"[Placeholder: Process with your prompt]\n{para[:100]}..."

        results.append({
            "index": i - 1,
            "original": para,
            "result": result_text
        })

    return results


if __name__ == "__main__":
    # Extract paragraphs
    docx_file = "/root/.claude/uploads/6e8f4fa8-a873-5be2-ac5a-d3fa317a1a3e/a715a8a1-Projecto_tese_09072026.docx"

    print("Extracting paragraphs from DOCX...")
    paragraphs = extract_paragraphs(docx_file)

    # Display statistics
    print_stats(paragraphs)

    # Show first 5 paragraphs
    print("FIRST 5 PARAGRAPHS:")
    print("-" * 70)
    for i, para in enumerate(paragraphs[:5]):
        print(f"\n[{i}] {para[:120]}{'...' if len(para) > 120 else ''}")
    print("\n")

    # Save to both formats
    save_paragraphs_json(paragraphs, "paragraphs.json")
    save_paragraphs_csv(paragraphs, "paragraphs.csv")

    # Example: Show how to use with a prompt
    print("\nEXAMPLE USAGE:")
    print("-" * 70)
    sample_prompt = """Summarize the following paragraph in 2-3 sentences:

{paragraph}"""
    print(f"Sample prompt template:\n{sample_prompt}\n")
    print("To process all paragraphs with Claude:")
    print("""
    from anthropic import Anthropic

    client = Anthropic()

    # Uncomment in process_paragraphs_template() and replace with actual call:
    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=1024,
        messages=[{"role": "user", "content": full_prompt}]
    )
    """)
