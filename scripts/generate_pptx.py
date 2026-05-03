#!/usr/bin/env python3
"""
Generate a .pptx from a Reveal.js HTML deck using a PowerPoint template.

Usage:
  python3 scripts/generate_pptx.py --html /path/to/docs/presentation_ready.html \
    --template "/home/freeman/Downloads/AWS User Group Slide Template.pptx" \
    --output /tmp/workshop_deck.pptx

The script looks for <section> tags and extracts a title (h1-h3) and body text.
It also captures <aside class="notes"> for speaker notes when present.
"""
import argparse
import sys
import os
from pptx import Presentation
from pptx.util import Pt
from bs4 import BeautifulSoup


def parse_slides_from_html(html_path: str):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    # Find top-level sections. If Reveal uses nested sections, collect leaf sections.
    sections = soup.find_all("section")
    slides = []

    for sec in sections:
        # Skip sections that contain other section tags (these are stacks)
        if sec.find("section"):
            continue

        title = None
        for tag in ("h1", "h2", "h3"):
            h = sec.find(tag)
            if h and h.get_text(strip=True):
                title = h.get_text(strip=True)
                break

        # body: capture content in order (paragraphs and list items) as structured parts
        from bs4 import Tag
        body_parts = []
        for child in sec.children:
            if not isinstance(child, Tag):
                continue
            if child.name in ("h1", "h2", "h3"):
                continue
            if child.name == "p":
                txt = child.get_text(" ", strip=True)
                if txt:
                    body_parts.append(("p", txt))
            elif child.name in ("ul", "ol"):
                for li in child.find_all("li", recursive=False):
                    txt = li.get_text(" ", strip=True)
                    if txt:
                        body_parts.append(("li", txt))
            elif child.name == "div":
                # panels often contain headings and paragraphs or lists
                for p in child.find_all(["p"], recursive=False):
                    txt = p.get_text(" ", strip=True)
                    if txt:
                        body_parts.append(("p", txt))
                for ul in child.find_all(["ul", "ol"], recursive=False):
                    for li in ul.find_all("li", recursive=False):
                        txt = li.get_text(" ", strip=True)
                        if txt:
                            body_parts.append(("li", txt))

        # Fallback: if we found nothing, attempt the old heuristic
        if not body_parts:
            parts = []
            for p in sec.find_all(["p", "li", "div"]):
                txt = p.get_text(" ", strip=True)
                if txt:
                    parts.append(("p", txt))
            body_parts = parts

        # speaker notes
        notes_tag = sec.find("aside", class_="notes")
        notes = notes_tag.get_text(" ", strip=True) if notes_tag else ""

        # If no explicit title, try first line of body
        if not title and body:
            title, *rest = body.split("\n", 1)
            body = rest[0] if rest else ""

        slides.append({"title": title or "", "body_parts": body_parts, "notes": notes})

    return slides


def choose_layout(prs: Presentation):
    # Prefer a layout with a title placeholder and a content placeholder
    for layout in prs.slide_layouts:
        try:
            ph_types = [ph.type for ph in layout.placeholders]
        except Exception:
            ph_types = []
        if any(pt in (1,) for pt in ph_types):
            return layout
    return prs.slide_layouts[0]


def add_slide_from_content(prs: Presentation, layout, slide_data: dict):
    slide = prs.slides.add_slide(layout)
    # Set title if available
    try:
        if slide_data.get("title"):
            slide.shapes.title.text = slide_data["title"]
    except Exception:
        pass

    # Find a body placeholder and add text
    for shape in slide.placeholders:
        if getattr(shape, 'is_placeholder', False) and getattr(shape.placeholder_format, 'idx', 0) != 0:
            try:
                tf = shape.text_frame
                tf.clear()
                body_parts = slide_data.get("body_parts", [])
                if body_parts:
                    for i, (kind, line) in enumerate(body_parts):
                        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
                        if kind == 'li':
                            p.text = f"• {line}"
                        else:
                            p.text = line
                        p.level = 0
                        p.font.size = Pt(20)
                break
            except Exception:
                continue

    # Add speaker notes if present
    notes_text = slide_data.get("notes") or ""
    if notes_text:
        try:
            notes_slide = slide.notes_slide
            notes_tf = notes_slide.notes_text_frame
            notes_tf.clear()
            notes_tf.text = notes_text
        except Exception:
            pass


def create_pptx_from_html(html_path: str, template_path: str, output_path: str):
    if not os.path.exists(html_path):
        print(f"ERROR: HTML file not found: {html_path}")
        sys.exit(2)
    if not os.path.exists(template_path):
        print(f"ERROR: PowerPoint template not found: {template_path}")
        sys.exit(2)

    slides = parse_slides_from_html(html_path)
    prs = Presentation(template_path)
    layout = choose_layout(prs)

    for s in slides:
        add_slide_from_content(prs, layout, s)

    prs.save(output_path)
    print(f"Wrote PPTX: {output_path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--html", required=True, help="Path to Reveal HTML file")
    p.add_argument("--template", required=True, help="Path to PPTX template file")
    p.add_argument("--output", required=True, help="Output PPTX path")
    args = p.parse_args()

    create_pptx_from_html(args.html, args.template, args.output)


if __name__ == "__main__":
    main()
