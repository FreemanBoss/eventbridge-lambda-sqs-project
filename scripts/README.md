PPTX generation helper
======================

This folder contains a small script to convert a Reveal.js HTML deck into a PowerPoint `.pptx` using your provided template.

Quick start
-----------

1. Install dependencies (preferably in a venv):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r scripts/requirements.txt
```

2. Run the generator (adjust paths as needed):

```bash
python3 scripts/generate_pptx.py \
  --html /home/freeman/eventbridge-lambda-sqs-project/docs/presentation_ready.html \
  --template "/home/freeman/Downloads/AWS User Group Slide Template.pptx" \
  --output /home/freeman/eventbridge-lambda-sqs-project/docs/output_workshop_deck.pptx
```

3. Open the generated PPTX in PowerPoint (or LibreOffice Impress) and review slides. If you want visual tweaks (fonts, spacing, images), tell me which slide numbers need changes and I'll update the script or the slide content extraction rules.

Notes
-----
- The script extracts text from `<section>` tags and looks for `h1`/`h2`/`h3` as titles and `aside.notes` for speaker notes.
- The script intentionally places speaker notes into the slide notes area so the visible slide stays clean.
- If your template has bespoke master layouts, we pick a reasonable layout automatically. If you want a specific layout per slide (two-column, diagram style), tell me and I will adapt the generator to map slides to template layouts.
