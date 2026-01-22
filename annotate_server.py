#!/usr/bin/env python3
"""
Simple HTTP server for the Plot Annotator.
Serves files AND accepts POST to save annotations.
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PLOTS_DIR = Path.home() / ".claude" / "plots"
PORT = 8888


class AnnotateHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PLOTS_DIR), **kwargs)

    def do_POST(self):
        if self.path == "/save":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode("utf-8"))

                # Save JSON
                json_path = PLOTS_DIR / "current_annotations.json"
                with open(json_path, "w") as f:
                    json.dump(data, f, indent=2)

                # Response
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"success": True, "path": str(json_path)}).encode()
                )
                print(f"✅ Annotations saved to {json_path}")

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif self.path == "/save-image":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)

            try:
                import base64

                # Expect base64 PNG data
                if post_data.startswith(b"data:image/png;base64,"):
                    post_data = post_data[22:]

                img_data = base64.b64decode(post_data)
                img_path = PLOTS_DIR / "current_annotated.png"

                with open(img_path, "wb") as f:
                    f.write(img_data)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"success": True, "path": str(img_path)}).encode()
                )
                print(f"✅ Image saved to {img_path}")

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif self.path == "/save-background":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)

            try:
                import base64

                # Expect base64 PNG data
                if post_data.startswith(b"data:image/png;base64,"):
                    post_data = post_data[22:]

                img_data = base64.b64decode(post_data)
                img_path = PLOTS_DIR / "current.png"

                with open(img_path, "wb") as f:
                    f.write(img_data)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"success": True, "path": str(img_path)}).encode()
                )
                print(f"✅ Background saved to {img_path}")

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif self.path == "/search-script":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)

            try:
                import subprocess
                import glob

                data = json.loads(post_data.decode("utf-8"))
                filename = data.get("filename", "")
                basename = Path(filename).stem  # Remove extension

                # Get known project roots from existing metadata
                project_roots = set()
                for meta_file in PLOTS_DIR.glob("*_meta.json"):
                    try:
                        with open(meta_file) as f:
                            meta = json.load(f)
                            if "regen_cwd" in meta:
                                project_roots.add(meta["regen_cwd"])
                            if "source" in meta:
                                # Add parent directories as potential roots
                                src_path = Path(meta["source"])
                                for parent in src_path.parents:
                                    if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
                                        project_roots.add(str(parent))
                                        break
                    except:
                        pass

                # Also add common locations
                home = Path.home()
                for common in ["Github", "Projects", "Code", "Dev"]:
                    common_path = home / common
                    if common_path.exists():
                        project_roots.add(str(common_path))
                    data_path = Path("/media/tofunori/Data") / common
                    if data_path.exists():
                        project_roots.add(str(data_path))

                found_script = None
                for root in project_roots:
                    try:
                        # Search for Python files containing the basename
                        result = subprocess.run(
                            ["grep", "-r", "-l", basename, "--include=*.py", root],
                            capture_output=True, text=True, timeout=10
                        )
                        if result.stdout.strip():
                            # Filter out venv directories
                            scripts = [s for s in result.stdout.strip().split("\n")
                                       if ".venv" not in s and "venv" not in s and "__pycache__" not in s]
                            if scripts:
                                found_script = scripts[0]
                                break
                    except:
                        pass

                if found_script:
                    # Update metadata
                    meta_path = PLOTS_DIR / "current_meta.json"
                    meta = {}
                    if meta_path.exists():
                        with open(meta_path) as f:
                            meta = json.load(f)

                    meta["name"] = basename
                    meta["source_script"] = found_script
                    # Find project root
                    script_path = Path(found_script)
                    for parent in script_path.parents:
                        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
                            meta["regen_cwd"] = str(parent)
                            break

                    with open(meta_path, "w") as f:
                        json.dump(meta, f, indent=2)

                    print(f"✅ Script found: {found_script}")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "found": found_script is not None,
                    "script": found_script,
                    "filename": filename
                }).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        elif self.path == "/refresh-from-source":
            try:
                import shutil

                meta_path = PLOTS_DIR / "current_meta.json"

                if not meta_path.exists():
                    raise Exception("No metadata file")

                with open(meta_path) as f:
                    meta = json.load(f)

                source = meta.get("source")
                if not source or not Path(source).exists():
                    raise Exception(f"Source not found: {source}")

                # Copier source → current.png
                shutil.copy2(source, PLOTS_DIR / "current.png")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"success": True, "source": source}).encode()
                )
                print(f"✅ Refreshed from {source}")

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

        elif self.path == "/refresh-by-filename":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"

            try:
                import shutil
                import subprocess

                data = json.loads(post_data.decode("utf-8"))
                filename = data.get("filename", "")

                if not filename:
                    raise Exception("No filename provided")

                # Search for the file - prioritize Data drive, then home
                search_roots = [
                    Path("/media/tofunori/Data"),
                    Path.home(),
                ]

                found_path = None

                # Use find command with longer timeout
                for search_root in search_roots:
                    if not search_root.exists():
                        continue
                    try:
                        result = subprocess.run(
                            ["find", str(search_root), "-name", filename, "-type", "f", "-print", "-quit"],
                            capture_output=True, text=True, timeout=30
                        )
                        if result.stdout.strip():
                            found_path = result.stdout.strip().split("\n")[0]
                            break
                    except subprocess.TimeoutExpired:
                        print(f"⚠️ Search timeout in {search_root}")
                    except Exception as e:
                        print(f"⚠️ Search error: {e}")

                if not found_path or not Path(found_path).exists():
                    raise Exception(f"File not found: {filename}")

                # Copy to current.png
                shutil.copy2(found_path, PLOTS_DIR / "current.png")

                # Update metadata
                meta_path = PLOTS_DIR / "current_meta.json"
                meta = {"source": found_path, "name": filename}
                with open(meta_path, "w") as f:
                    json.dump(meta, f, indent=2)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"success": True, "source": found_path}).encode()
                )
                print(f"✅ Found and refreshed from {found_path}")

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

        elif self.path == "/set-source-path":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"

            try:
                import shutil

                data = json.loads(post_data.decode("utf-8"))
                source = data.get("source", "")
                name = data.get("name", "")

                if not source:
                    raise Exception("No source path provided")

                # Verify the file exists
                if not Path(source).exists():
                    raise Exception(f"File not found: {source}")

                # Copy to current.png
                shutil.copy2(source, PLOTS_DIR / "current.png")

                # Save metadata
                meta_path = PLOTS_DIR / "current_meta.json"
                meta = {"source": source, "name": name}
                with open(meta_path, "w") as f:
                    json.dump(meta, f, indent=2)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(
                    json.dumps({"success": True, "source": source}).encode()
                )
                print(f"✅ Source path set: {source}")

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


def main():
    # Ensure plots dir exists
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Link HTML file
    html_src = Path.home() / ".claude" / "tools" / "annotate.html"
    html_dst = PLOTS_DIR / "annotate.html"
    if html_src.exists() and not html_dst.exists():
        html_dst.symlink_to(html_src)

    server = HTTPServer(("", PORT), AnnotateHandler)
    print(f"🎨 Plot Annotator Server")
    print(f"   http://localhost:{PORT}/annotate.html")
    print(f"   Plots: {PLOTS_DIR}")
    print(f"   Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
