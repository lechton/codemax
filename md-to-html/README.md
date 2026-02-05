# md-to-html

A terminal-based Markdown to HTML converter with A4-formatted CSS presets. Zero external dependencies — runs on Python 3.10+ standard library only.

## Features

- Interactive CLI with step-by-step prompts
- Accepts local files or remote URLs as Markdown input
- Three built-in A4 CSS themes embedded directly into the output HTML
- Auto-generates heading IDs for anchor linking
- Supports tables, fenced code blocks, task lists, blockquotes, and more
- Fallback `input_markdown/` and `output_html/` directories when no paths are provided
- Print-ready output with `@page` rules and page-break control

## Folder Structure

```
md-to-html/
├── md-to-html.py              # Main CLI script
├── css/
│   ├── A4_official.css         # Formal serif — Times New Roman, corporate layout
│   ├── A4_github.css           # GitHub-flavored — system sans-serif, subtle borders
│   └── A4_claude.css           # Anthropic/Claude — warm cream tones, dark code blocks
├── input_markdown/
│   └── demo_document.md        # Sample markdown for testing
└── output_html/                # Default output directory
```

## Requirements

- Python 3.10 or later
- No third-party packages needed

## Usage

```bash
cd md-to-html
python3 md-to-html.py
```

The script walks through four interactive steps:

### Step 1 — Select Markdown Source

You have three options:

| Input | Behaviour |
|-------|-----------|
| **File path** | Reads the local `.md` file directly |
| **URL** | Downloads the Markdown content from the web |
| **Empty (Enter)** | Lists `.md` files in `input_markdown/` for selection |

### Step 2 — Output Folder

| Input | Behaviour |
|-------|-----------|
| **Folder path** | Writes the HTML file to that directory (creates it if needed) |
| **Empty (Enter)** | Uses the built-in `output_html/` directory |

### Step 3 — Choose CSS Theme

```
  Select a CSS theme:
    [1] A4 Official — Formal serif document (Times New Roman, corporate layout)
    [2] A4 GitHub  — GitHub-flavored markdown style (system sans-serif)
    [3] A4 Claude  — Anthropic / Claude style (warm tones, modern sans-serif)
```

The selected CSS is embedded inside a `<style>` tag in the final HTML — no external files required.

### Step 4 — Convert

The script converts the Markdown, wraps it in a full HTML5 document, and writes the result.

## Examples

### Convert the bundled demo file with the Claude theme

```bash
$ python3 md-to-html.py
# Step 1: press Enter → select [1] demo_document.md
# Step 2: press Enter → uses output_html/
# Step 3: enter 3     → A4 Claude theme
# Step 4: converts automatically

# Output:
#   ==============================================================
#     DONE!
#     Source : demo_document.md
#     Theme  : A4_claude
#     Output : /path/to/md-to-html/output_html/demo_document.html
#     Size   : 17.1 KB
#   ==============================================================
```

### Convert a local file with the GitHub theme

```bash
$ python3 md-to-html.py
# Step 1: enter /home/user/notes/meeting.md
# Step 2: enter /home/user/Desktop
# Step 3: enter 2 → A4 GitHub theme

# → Creates /home/user/Desktop/meeting.html
```

### Convert from a URL with the Official theme

```bash
$ python3 md-to-html.py
# Step 1: enter https://raw.githubusercontent.com/user/repo/main/README.md
# Step 2: press Enter → uses output_html/
# Step 3: enter 1 → A4 Official theme

# → Creates output_html/README.html
```

## CSS Theme Previews

### A4 Official
Formal document style with **Times New Roman** serif font, centered uppercase `<h1>`, dark table headers (`#2c3e50`), justified text, and conservative spacing. Ideal for reports, memos, and printed documents.

### A4 GitHub
Faithful reproduction of GitHub's markdown renderer. Uses the **system font stack** (`-apple-system, Segoe UI, …`), light grey borders (`#d1d9e0`), `#f6f8fa` code backgrounds, and compact `6px 13px` table cell padding. Best for technical docs and READMEs.

### A4 Claude
Warm, modern aesthetic inspired by Anthropic's design language. Features **cream background** (`#faf9f5`), signature tan accent colour (`#d4a574`), dark code blocks (`#1a1915` background with light text), rounded corners, and gradient horizontal rules. Great for polished presentations.

## Supported Markdown Syntax

| Feature | Example |
|---------|---------|
| Headings | `# H1` through `###### H6` |
| Bold | `**text**` or `__text__` |
| Italic | `*text*` or `_text_` |
| Bold + Italic | `***text***` |
| Strikethrough | `~~text~~` |
| Inline code | `` `code` `` |
| Fenced code blocks | ` ```python ... ``` ` |
| Blockquotes | `> quote` (nested supported) |
| Unordered lists | `- item` / `* item` / `+ item` |
| Ordered lists | `1. item` |
| Task lists | `- [x] done` / `- [ ] todo` |
| Tables | Pipe-delimited with alignment |
| Links | `[text](url)` |
| Images | `![alt](url)` |
| Horizontal rules | `---` / `***` / `___` |
