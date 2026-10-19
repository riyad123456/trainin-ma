"""Build the single web font file for the trainin.ma site.

Source: Google Sans Flex (SIL OFL 1.1, no reserved font name), from google/fonts.
1. Pin ROND = 0 (the brief sets roundness to 0 everywhere) and slnt = 0 (no italics);
   keep wght, wdth and opsz variable, within the ranges the site uses.
2. Add U+2192 RIGHTWARDS ARROW, which the font lacks, as a composite of the font's own
   minus (shaft) and greater-than (head), so it follows weight and width like the text.
3. Subset to the characters French copy needs, keep kerning, tabular figures and marks,
   drop discretionary ligatures (the font turns "Google" into a logo with dlig).
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent

SRC = "GoogleSansFlex.ttf"
OUT = sys.argv[1] if len(sys.argv) > 1 else "gsf-site.woff2"
SHAFT_SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 1.32
HEAD_SHIFT = int(sys.argv[3]) if len(sys.argv) > 3 else 330

font = TTFont(SRC)
vf = instancer.instantiateVariableFont(
    font,
    {"ROND": 0, "slnt": 0, "wght": (200, 700), "wdth": (75, 100)},
    inplace=False,
)

glyf = vf["glyf"]
hmtx = vf["hmtx"]

# --- arrow: shaft = minus stretched horizontally, head = greater shifted right ---------
# minus  bbox x 123..993, y 543..697 (stroke 154, axis y=620)
# greater bbox x 144..990, tip at (990, ~620)
shaft = GlyphComponent()
shaft.glyphName = "minus"
shaft.x = round(110 - 123 * SHAFT_SCALE)   # left end of the shaft lands at x=110
shaft.y = 0
shaft.flags = 0x0004 | 0x0400              # ROUND_XY_TO_GRID | OVERLAP_COMPOUND
shaft.transform = [[SHAFT_SCALE, 0], [0, 1]]

head = GlyphComponent()
head.glyphName = "greater"
head.x = HEAD_SHIFT
head.y = 0
head.flags = 0x0004

arrow = Glyph()
arrow.numberOfContours = -1
arrow.components = [shaft, head]
glyf.glyphs["arrowright"] = arrow
order = vf.getGlyphOrder() + ["arrowright"]
vf.setGlyphOrder(order)
glyf.glyphOrder = order
arrow.recalcBounds(glyf)
tip = 990 + HEAD_SHIFT
shaft_end = 110 + (993 - 123) * SHAFT_SCALE
advance = tip + 120
hmtx.metrics["arrowright"] = (advance, arrow.xMin)
vf["gvar"].variations["arrowright"] = []
hvar = vf["HVAR"].table
if hvar.AdvWidthMap is not None:
    hvar.AdvWidthMap.mapping["arrowright"] = hvar.AdvWidthMap.mapping["minus"]
if "GDEF" in vf and vf["GDEF"].table.GlyphClassDef is not None:
    vf["GDEF"].table.GlyphClassDef.classDefs["arrowright"] = 1
for table in vf["cmap"].tables:
    if table.isUnicode():
        table.cmap[0x2192] = "arrowright"
print(f"arrow: advance {advance}, shaft end {shaft_end:.0f}, tip {tip}, inner vertex ~{tip-339}, "
      f"head fully covers shaft if shaft end <= {tip-151}")

tmp = OUT.replace(".woff2", ".tmp.ttf")
vf.save(tmp)

unicodes = (
    list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) +
    [0x152, 0x153, 0x178, 0x2BC, 0x2C6, 0x2DC] +
    [0x2009, 0x200A, 0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2018, 0x2019, 0x201A,
     0x201C, 0x201D, 0x201E, 0x2022, 0x2026, 0x202F, 0x2039, 0x203A, 0x20AC, 0x2122,
     0x2192, 0x2212, 0x2248, 0x2260, 0x2264, 0x2265]
)
opts = subset.Options()
opts.flavor = "woff2"
opts.layout_features = ["kern", "mark", "mkmk", "ccmp", "locl", "liga", "calt", "rvrn",
                        "tnum", "lnum", "pnum", "frac", "numr", "dnom"]
opts.name_IDs = ["*"]
opts.name_languages = ["*"]
opts.notdef_outline = True
opts.hinting = False
sub_font = TTFont(tmp)
s = subset.Subsetter(opts)
s.populate(unicodes=unicodes)
s.subset(sub_font)
sub_font.flavor = "woff2"
sub_font.save(OUT)
import os
print(OUT, os.path.getsize(OUT), "bytes;", "axes:",
      [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in sub_font["fvar"].axes])
os.remove(tmp)
