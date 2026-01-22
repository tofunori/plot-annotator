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
