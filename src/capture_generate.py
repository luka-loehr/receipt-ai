#!/usr/bin/env python3
"""
Entry point to generate To-Do capture receipt from manual input.
Input via environment variables or CLI args: TEXT and/or IMAGE_URL (path allowed).
Outputs PNG at outputs/png/todo_capture.png (under current working project root).
"""

import os
import sys
from urllib.parse import urljoin
from urllib.request import pathname2url

from .capture_ai import CaptureAI
from .todo_receipt import save_todo_receipt


def path_to_file_url(path: str) -> str:
    return urljoin('file:', pathname2url(os.path.abspath(path)))


def main():
    text = os.getenv('TEXT')
    image = os.getenv('IMAGE')
    image_url = None
    if image:
        if image.startswith('http://') or image.startswith('https://') or image.startswith('file:'):
            image_url = image
        else:
            image_url = path_to_file_url(image)

    ai = CaptureAI()
    content = ai.analyze(text, image_url)
    out_path = save_todo_receipt(content)
    print(out_path)


if __name__ == '__main__':
    main()


