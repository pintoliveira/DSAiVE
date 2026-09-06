#!/usr/bin/env python3
"""
Process document paragraphs sequentially with Claude API.
"""

import subprocess
import xml.etree.ElementTree as ET
import json
from pathlib import Path
from typing import List, Dict
from anthropic import Anthropic

client = Anthropic()


def extract_paragraphs(docx_path: str) -> List[str]:
    """Extract all non-empty paragraphs from DOCX file."""
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

        if para_text:
            paragraphs.append(para_text)

    return paragraphs


def process_paragraph(para: str, prompt_template: str, model: str = "claude-opus-4-1") -> str:
    """
    Send a single paragraph to Claude with your prompt.

    Args:
        para: Paragraph text
        prompt_template: Prompt with {paragraph} placeholder
        model: Claude model to use

    Returns:
        Claude's response text
    """
    full_prompt = prompt_template.format(paragraph=para)

    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {"role": "user", "content": full_prompt}
        ]
    )

    return message.content[0].text


def process_all_paragraphs(
    paragraphs: List[str],
    prompt_template: str,
    output_file: str = "results.json",
    model: str = "claude-opus-4-1"
) -> List[Dict]:
    """
    Process all paragraphs sequentially.

    Args:
        paragraphs: List of paragraph texts
        prompt_template: Prompt with {paragraph} placeholder
        output_file: Where to save results
        model: Claude model to use

    Returns:
        List of results
    """
    results = []

    for i, para in enumerate(paragraphs, 1):
        print(f"[{i}/{len(paragraphs)}] Processing paragraph...")

        try:
            result_text = process_paragraph(para, prompt_template, model)

            result = {
                "index": i - 1,
                "original_length": len(para),
                "result": result_text
            }
            results.append(result)

            # Save incrementally (in case of interruption)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "total_processed": len(results),
                    "total_paragraphs": len(paragraphs),
                    "results": results
                }, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                "index": i - 1,
                "original_length": len(para),
                "error": str(e)
            })

    return results


def main():
    """Main entry point."""
    # Configuration
    docx_file = "/root/.claude/uploads/6e8f4fa8-a873-5be2-ac5a-d3fa317a1a3e/a715a8a1-Projecto_tese_09072026.docx"

    # YOUR PROMPT - Customize this!
    prompt_template = """Analyze the following paragraph from a thesis about sustainable transportation and AI:

{paragraph}

Provide:
1. Key concepts
2. Main arguments
3. One-sentence summary"""

    print("="*70)
    print("DOCUMENT PARAGRAPH PROCESSOR")
    print("="*70)

    # Extract paragraphs
    print("\nExtracting paragraphs...")
    paragraphs = extract_paragraphs(docx_file)
    print(f"✓ Found {len(paragraphs)} paragraphs")

    # Show sample
    print("\nSample paragraph to process:")
    print("-" * 70)
    print(paragraphs[20][:300] + "...")
    print("\nWith prompt:")
    print("-" * 70)
    print(prompt_template)
    print("-" * 70)

    # Ask for confirmation
    response = input("\nProceed with processing? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return

    # Process all paragraphs
    print("\nStarting processing...\n")
    results = process_all_paragraphs(
        paragraphs,
        prompt_template,
        output_file="results.json",
        model="claude-opus-4-1"
    )

    print(f"\n✓ Completed! Processed {len(results)} paragraphs")
    print(f"✓ Results saved to results.json")


if __name__ == "__main__":
    main()
