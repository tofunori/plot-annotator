# Plot Annotator

A lightweight, browser-based tool for annotating matplotlib plots with pan/zoom support. Draw shapes, add text annotations, and export coordinates for programmatic plot modifications.

![Screenshot](screenshot.png)

## Features

- **Pan & Zoom** - Navigate large plots like Google Maps
  - Mouse wheel to zoom in/out
  - Space + drag or Right-click + drag to pan
- **Drawing Tools** - Rectangle, Circle, Line, Freehand, Text
- **Color-coded Zones** - 6 colors to categorize annotations
- **Labels Panel** - Add descriptions per color zone
- **Auto-save** - Annotations saved directly to disk (JSON + annotated PNG)
- **No dependencies** - Pure HTML/JS frontend (Fabric.js via CDN)
- **Cross-platform** - Works on Linux, macOS, Windows

## Quick Start

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/plot-annotator.git
cd plot-annotator

# Start the server
python3 annotate_server.py

# Open in browser
# http://localhost:8888/annotate.html
```

Then drag & drop your plot image onto the canvas.

## Controls

| Action | Control |
|--------|---------|
| **Zoom** | Mouse wheel |
| **Pan** | Space + drag, Right-click + drag, or Pan button |
| **Draw** | Select tool → click & drag |
| **Add Text** | Text tool → click → type in prompt |
| **Labels** | Labels button → side panel |
| **Save** | Save button (auto-saves to disk) |
| **Delete** | Select object → Delete key |

## Output Files

When you save, two files are created in the server directory:

| File | Description |
|------|-------------|
| `current_annotations.json` | Annotation coordinates and metadata |
| `current_annotated.png` | Image with annotations drawn |

### JSON Format

```json
{
  "zones": [
    {
      "id": "blue",
      "color": "#2196F3",
      "type": "circle",
      "center": [500, 300],
      "radius": 50,
      "label": "Increase font size"
    },
    {
      "id": "red",
      "color": "#F44336",
      "type": "text",
      "text": "Change title to French",
      "position": [100, 50],
      "label": null
    }
  ],
  "created": "2026-01-22T10:00:00.000Z",
  "plot_name": "current"
}
```

## Use Cases

### 1. Collaborative Plot Review
Share plots with colleagues, let them annotate feedback, then programmatically apply changes.

### 2. AI-Assisted Plot Modification
Use with LLMs (Claude, GPT) to describe plot modifications visually:
1. Annotate the plot with desired changes
2. Share the JSON with the AI
3. AI modifies the matplotlib code accordingly

### 3. Figure Preparation
Annotate figures for publication review, track needed changes with color-coded zones.

## Installation Options

### Option A: Standalone (recommended)
```bash
python3 annotate_server.py
```
Serves files from current directory on port 8888.

### Option B: Custom directory
```bash
# Edit PLOTS_DIR in annotate_server.py
PLOTS_DIR = Path("/your/custom/path")
```

### Option C: Static file (no server)
Open `annotate.html` directly in browser. Note: auto-save won't work without the server.

## Available Colors

| Color | Hex | Use for |
|-------|-----|---------|
| Blue | #2196F3 | Primary annotations |
| Red | #F44336 | Issues, errors |
| Green | #4CAF50 | Approved, correct |
| Yellow | #FFEB3B | Warnings, attention |
| Orange | #FF9800 | Secondary changes |
| Purple | #9C27B0 | Special notes |

## Requirements

- Python 3.6+ (for server)
- Modern browser (Chrome, Firefox, Safari, Edge)
- No pip dependencies!

## Integration with Claude Code

This tool was designed to work with [Claude Code](https://github.com/anthropics/claude-code) for AI-assisted plot modification:

```bash
# Load a plot
/plot load /path/to/figure.png

# Annotate in browser, save

# Apply changes
/plot apply
# → Claude reads annotations and modifies your matplotlib code
```

## License

MIT License - Feel free to use, modify, and distribute.

## Contributing

PRs welcome! Ideas for improvements:
- [ ] Undo/redo support
- [ ] Arrow tool
- [ ] Export to SVG
- [ ] Multiple pages/plots
- [ ] Annotation templates

## Credits

Built with [Fabric.js](http://fabricjs.com/) for canvas manipulation.
