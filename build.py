"""Inline the font into the page and write the artifact file plus a local preview wrapper."""
import base64, pathlib

here = pathlib.Path(__file__).parent
src = (here / "src.html").read_text(encoding="utf-8")
font_b64 = base64.b64encode((here / "gsf-site.woff2").read_bytes()).decode("ascii")
face = ('@font-face{font-family:"Google Sans Flex";'
        f'src:url(data:font/woff2;base64,{font_b64}) format("woff2");'
        'font-weight:200 700;font-stretch:75% 100%;font-style:normal;font-display:swap}')
assert "/*@FONT@*/" in src
page = src.replace("/*@FONT@*/", face)

# Inline local images (src="img/…") so index.html stays one self-contained file.
import re
MIME = {".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".avif": "image/avif", ".svg": "image/svg+xml"}
def inline_img(m):
    f = here / m.group(1)
    return f'src="data:{MIME[f.suffix.lower()]};base64,{base64.b64encode(f.read_bytes()).decode("ascii")}"'
page = re.sub(r'src="(img/[^"]+)"', inline_img, page)

dist = here
dist.mkdir(exist_ok=True)
# Standards mode when served as a normal site (GitHub Pages); the Artifact host ignores it.
page = "<!doctype html>\n" + page
(here / "index.html").write_text(page, encoding="utf-8")

# Same skeleton the Artifact tool wraps the page in at publish time.
print("page", len(page.encode("utf-8")), "bytes; font", len(font_b64), "base64 chars")
