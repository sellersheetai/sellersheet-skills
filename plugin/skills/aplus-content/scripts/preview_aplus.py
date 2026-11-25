#!/usr/bin/env python3
"""Preview an Amazon A+ content or Brand Story document as one local HTML page.

Reads a contentDocument (the JSON the A+ tools take, or the envelope a document read
returns) and writes one self-contained HTML file with a desktop and a mobile view, plus a
list of checks against the limits in reference/schema/. The layout is an approximation for
review: Amazon's own rendering decides the final look. Python 3.9+, standard library only.
"""

import argparse
import html
import json
import os
import re
import sys
import webbrowser

MEDIA_HOST = "https://m.media-amazon.com/images/S/"
PREMIUM_MAX_MODULES = 7


# ---------------------------------------------------------------- small helpers

def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def g(o, *path):
    """Nested get that tolerates any shape: returns None on a missing or wrong-typed step."""
    for k in path:
        if isinstance(k, int):
            o = o[k] if isinstance(o, list) and -len(o) <= k < len(o) else None
        else:
            o = o.get(k) if isinstance(o, dict) else None
        if o is None:
            return None
    return o


def items(o, *path):
    v = g(o, *path)
    return [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []


def num(v):
    try:
        f = float(str(v).strip())
    except (TypeError, ValueError):
        return None
    return f if f == f else None  # drop NaN


def by_pos(lst, key=None):
    """Sort a list by its `position` (inside `key` when given); items without one keep order, last."""
    def pos(it):
        p = num(g(it, key, "position") if key else g(it, "position"))
        return (0, p) if p is not None else (1, 0)
    return sorted(lst, key=pos)


def safe_url(u):
    if isinstance(u, str) and re.match(r"^https?://[^\s\"'<>]+$", u.strip(), re.I):
        return u.strip()
    return None


def text_of(tc):
    if isinstance(tc, dict):
        v = tc.get("value")
        return "" if v is None else str(v)
    return "" if tc is None else str(tc)


def para_texts(pc):
    return [text_of(t) for t in items(pc, "textList")]


# ---------------------------------------------------------------- rich text

INLINE = {"STYLE_BOLD": "b", "STYLE_ITALIC": "i", "STYLE_UNDERLINE": "u"}
BLOCK = {"LIST_ORDERED": ("ol", 0), "LIST_UNORDERED": ("ul", 0), "LIST_ITEM": ("li", 1),
         "STYLE_PARAGRAPH": ("p", 2)}


def rich(tc):
    """A TextComponent as escaped HTML, decoratorSet applied by offset and length."""
    if not isinstance(tc, dict):
        return esc(tc) if isinstance(tc, str) else ""
    text = text_of(tc)
    n = len(text)
    inline, blocks, breaks, cuts = [], [], set(), {0, n}
    for d in tc.get("decoratorSet") or []:
        if not isinstance(d, dict):
            continue
        off, ln = num(d.get("offset")), num(d.get("length"))
        off = int(max(0, min(off or 0, n)))
        end = int(max(off, min(off + (ln or 0), n)))
        t = d.get("type")
        if t == "STYLE_LINEBREAK":
            breaks.add(off)
            cuts.add(off)
        elif t in INLINE and end > off:
            inline.append((off, end, INLINE[t]))
            cuts |= {off, end}
        elif t in BLOCK and end > off:
            blocks.append((off, end) + BLOCK[t])
            cuts |= {off, end}
    blocks.sort(key=lambda b: (b[0], -(b[1] - b[0]), b[3]))
    pts, out, stack, bi = sorted(cuts), [], [], 0
    for idx, a in enumerate(pts):
        while stack and stack[-1][0] <= a:
            out.append("</%s>" % stack.pop()[1])
        if a in breaks:
            out.append("<br>")
        while bi < len(blocks) and blocks[bi][0] == a:
            b = blocks[bi]
            bi += 1
            out.append("<%s>" % b[2])
            stack.append((b[1], b[2]))
        if idx + 1 < len(pts):
            z = pts[idx + 1]
            seg = esc(text[a:z])
            for s, e, tag in inline:
                if s <= a and e >= z:
                    seg = "<%s>%s</%s>" % (tag, seg, tag)
            out.append(seg)
    while stack:
        out.append("</%s>" % stack.pop()[1])
    return "".join(out)


def T(tc, cls="tx", tag="div"):
    """TextComponent in a block; empty string when there is no text."""
    if not text_of(tc).strip():
        return ""
    return '<%s class="%s">%s</%s>' % (tag, cls, rich(tc), tag)


def P(pc, cls="body"):
    """ParagraphComponent: one paragraph per textList entry."""
    rows = [rich(t) for t in items(pc, "textList") if text_of(t).strip()]
    return '<div class="%s">%s</div>' % (cls, "".join("<p>%s</p>" % r for r in rows)) if rows else ""


def bullets(text_items):
    lis = [rich(g(it, "text")) for it in by_pos(text_items) if text_of(g(it, "text")).strip()]
    return '<ul class="bul">%s</ul>' % "".join("<li>%s</li>" % x for x in lis) if lis else ""


# ---------------------------------------------------------------- render context, images, video

class Ctx:
    def __init__(self, mobile, media, warnings):
        self.mobile = mobile
        self.media = media
        self.warnings = warnings  # shared dict used as an ordered set

    def warn(self, msg):
        self.warnings.setdefault(msg, None)

    def pick(self, m, desk="desktopImage", mob="mobileImage"):
        return (mob, g(m, mob)) if self.mobile else (desk, g(m, desk))


def image_url(comp):
    """(kind, url): 'url' a usable URL, 'id' an id that cannot be shown, 'none' no image."""
    u = g(comp, "uploadDestinationId")
    if not isinstance(u, str) or not u.strip():
        return "none", None
    u = u.strip()
    if safe_url(u):
        return "url", u
    # The id forms Amazon returns: an upload ("aplus-media/sc/…"), a media-library asset
    # ("aplus-media-library-service-media/…"), and a catalog image ("/images/I/…").
    if u.startswith(("aplus-media/", "aplus-media-library-service-media/")) and safe_url(MEDIA_HOST + u):
        return "url", MEDIA_HOST + u
    if u.startswith("/images/I/") and safe_url("https://m.media-amazon.com" + u):
        return "url", "https://m.media-amazon.com" + u
    return "id", u


def crop_of(comp):
    c = g(comp, "imageCropSpecification")
    w, h = num(g(c, "size", "width", "value")), num(g(c, "size", "height", "value"))
    if not (w and h and w > 0 and h > 0):
        return None
    return (num(g(c, "offset", "x", "value")) or 0.0, num(g(c, "offset", "y", "value")) or 0.0, w, h)


def placeholder(label, size, note, ratio=None):
    w, h = size
    return ('<div class="ph" style="aspect-ratio:%s"><span><b>%s</b><br>min %d &times; %d px<br>%s</span></div>'
            % (ratio or "%d/%d" % (w, h), esc(label), w, h, esc(note)))


def image(ctx, comp, label, size, required=True):
    """One image slot at the slot's ratio (the crop's when given), or a grey placeholder."""
    kind, url = image_url(comp)
    if kind == "none":
        if not required:
            return ""
        ctx.warn("%s: no image in this slot." % label)
        return placeholder(label, size, "no image")
    alt = text_of(g(comp, "altText"))
    if len(alt) > 100:
        ctx.warn("%s altText: %d characters, the limit is 100." % (label, len(alt)))
    cr = crop_of(comp)
    ratio = "%g/%g" % (cr[2], cr[3]) if cr else "%d/%d" % size
    if kind == "id":
        return placeholder(label, size, "id: " + url, ratio)
    data = ' data-crop="%g,%g,%g,%g"' % cr if cr else ""
    return ('<div class="slot" style="aspect-ratio:%s"><img src="%s" alt="%s" title="%s" loading="lazy"%s></div>'
            % (ratio, esc(url), esc(alt), esc(label), data))


IMG_EXT = re.compile(r"\.(jpe?g|png|gif|webp|avif)(\?|$)", re.I)


def video(ctx, comp, label, size):
    """A VideoComponent: a frame with a play badge and its ids, or the mapped poster or video."""
    w, h = size
    if not isinstance(comp, dict):
        ctx.warn("%s: no video in this slot." % label)
        return placeholder(label, size, "no video")
    vid, imid = g(comp, "videoMediaId"), g(comp, "imageMediaId")
    for k in ("videoMediaId", "imageMediaId", "imageCropSpecification"):
        if comp.get(k) in (None, ""):
            ctx.warn("%s: %s missing (a VideoComponent needs all three of videoMediaId, imageMediaId, "
                     "imageCropSpecification)." % (label, k))
    cr = crop_of(comp)
    ratio = "%g/%g" % (cr[2], cr[3]) if cr else "%d/%d" % size
    vurl = safe_url(ctx.media.get(str(vid))) if vid is not None else None
    purl = safe_url(ctx.media.get(str(imid))) if imid is not None else None
    if vurl and IMG_EXT.search(vurl) and not purl:
        purl, vurl = vurl, None
    ids = "video %s · image %s" % (vid or "?", imid or "?")
    if vurl:
        poster = ' poster="%s"' % esc(purl) if purl else ""
        return ('<div class="slot vid" style="aspect-ratio:%s"><video controls preload="metadata"%s src="%s"></video></div>'
                % (ratio, poster, esc(vurl)))
    if purl:
        return ('<div class="slot vid" style="aspect-ratio:%s"><img src="%s" alt="%s" loading="lazy">'
                '<i class="play"></i><em class="ids">%s</em></div>' % (ratio, esc(purl), esc(label), esc(ids)))
    return ('<div class="ph vidph" style="aspect-ratio:%s"><i class="play"></i><span><b>%s</b><br>%s<br>'
            'preview image min %d &times; %d px</span></div>' % (ratio, esc(label), esc(ids), w, h))


# ---------------------------------------------------------------- layout helpers

def cols(n, cells, cls=""):
    return '<div class="cols c%d %s">%s</div>' % (n, cls, "".join('<div class="cell">%s</div>' % c for c in cells))


def side(img_html, text_html, image_right=False, cls=""):
    return '<div class="side %s%s"><div class="sm">%s</div><div class="st">%s</div></div>' % (
        cls, " rev" if image_right else "", img_html, text_html)


def strip(cards, label):
    n = len(cards)
    body = "".join('<div class="card"><span class="pos">%s %d / %d</span>%s</div>' % (esc(label), i + 1, n, c)
                   for i, c in enumerate(cards))
    return '<div class="strip">%s</div>' % body


def tabs(names):
    return '<div class="tabs">%s</div>' % "".join(
        '<span class="%s">%s</span>' % ("on" if i == 0 else "", rich(t)) for i, t in enumerate(names))


def table(head, rows, cls=""):
    th = "".join("<th>%s</th>" % h for h in head)
    tr = "".join("<tr>%s</tr>" % "".join(("<th>%s</th>" if j == 0 else "<td>%s</td>") % c for j, c in enumerate(r))
                 for r in rows)
    return '<div class="tw"><table class="tbl %s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
        cls, th, tr)


def overlay(img_html, box_html, right=False, dark=True):
    return '<div class="ovl">%s<div class="box %s %s">%s</div></div>' % (
        img_html, "right" if right else "left", "dark" if dark else "light", box_html)


def block_text(b, h="h3", body="body"):
    return T(g(b, "headline"), h) + P(g(b, "body"), body)


# ---------------------------------------------------------------- STANDARD_* modules

def s_company_logo(c, m, L):
    return '<div class="logo">%s</div>' % image(c, g(m, "companyLogo"), L + "companyLogo", (600, 180))


def s_comparison_table(c, m, L):
    columns = by_pos(items(m, "productColumns"))
    labels = {num(x.get("position")): text_of(x) for x in items(m, "metricRowLabels")}
    positions = set(k for k in labels if k is not None)
    for col in columns:
        positions |= set(p for p in (num(x.get("position")) for x in items(col, "metrics")) if p is not None)
    head = [""]
    for i, col in enumerate(columns):
        cell = image(c, g(col, "image"), "%sproductColumns[%d].image" % (L, i), (150, 300), required=False)
        cell += T(g(col, "title"), "h4") + ('<div class="asin">%s</div>' % esc(col["asin"]) if col.get("asin") else "")
        head.append('<div class="%s">%s</div>' % ("hl" if col.get("highlight") is True else "", cell))
    rows = []
    for p in sorted(positions):
        row = [esc(labels.get(p, ""))]
        for col in columns:
            v = next((text_of(x) for x in items(col, "metrics") if num(x.get("position")) == p), "")
            row.append(esc(v))
        rows.append(row)
    return table(head, rows, "cmp")


def _image_blocks(c, m, L, n, size, h="h3"):
    cells = []
    for i in range(1, n + 1):
        b = g(m, "block%d" % i)
        cells.append(image(c, g(b, "image"), "%sblock%d.image" % (L, i), size) + block_text(b, h))
    return cells


def s_four_image_text(c, m, L):
    return T(g(m, "headline"), "h1") + cols(4, _image_blocks(c, m, L, 4, (220, 200)))


def s_four_image_text_quadrant(c, m, L):
    cells = []
    for i in range(1, 5):
        b = g(m, "block%d" % i)
        cells.append(side(image(c, g(b, "image"), "%sblock%d.image" % (L, i), (135, 135)), block_text(b), cls="q"))
    return cols(2, cells, "quad")


def s_header_image_text(c, m, L):
    b = g(m, "block")
    return (T(g(m, "headline"), "h1") + image(c, g(b, "image"), L + "block.image", (970, 600))
            + block_text(b, "h2"))


def s_image_sidebar(c, m, L):
    ic, dt, sb = g(m, "imageCaptionBlock"), g(m, "descriptionTextBlock"), g(m, "sidebarImageTextBlock")
    main = image(c, g(ic, "image"), L + "imageCaptionBlock.image", (300, 400)) + T(g(ic, "caption"), "cap")
    mid = T(g(dt, "headline"), "h3") + P(g(dt, "body")) + bullets(items(m, "descriptionListBlock", "textList"))
    bar = (image(c, g(sb, "image"), L + "sidebarImageTextBlock.image", (300, 175)) + block_text(sb)
           + bullets(items(m, "sidebarListBlock", "textList")))
    return T(g(m, "headline"), "h1") + '<div class="cols sidebar">%s</div>' % "".join(
        '<div class="cell">%s</div>' % x for x in (main, mid, '<div class="bar">%s</div>' % bar))


def s_image_text_overlay(c, m, L):
    b = g(m, "block")
    dark = m.get("overlayColorType") != "LIGHT"
    return overlay(image(c, g(b, "image"), L + "block.image", (970, 300)), block_text(b, "h2"), dark=dark)


def s_multiple_image_text(c, m, L):
    cards = []
    for i, it in enumerate(items(m, "blocks")):
        b = g(it, "block")
        cards.append(image(c, g(b, "image"), "%sblocks[%d].block.image" % (L, i), (300, 300))
                     + block_text(b) + T(g(it, "caption"), "cap"))
    return strip(cards, "Block") if cards else '<div class="empty">No blocks.</div>'


def s_product_description(c, m, L):
    return P(g(m, "body"))


def s_single_image_highlights(c, m, L):
    tb = "".join(block_text(g(m, "textBlock%d" % i)) for i in (1, 2, 3))
    bl = g(m, "bulletedListBlock")
    specs = T(g(bl, "headline"), "h3") + bullets(items(bl, "block", "textList"))
    return T(g(m, "headline"), "h1") + cols(3, [image(c, g(m, "image"), L + "image", (300, 300)), tb, specs], "hl3")


def s_single_image_specs_detail(c, m, L):
    desc = T(g(m, "descriptionHeadline"), "h2") + "".join(block_text(g(m, "descriptionBlock%d" % i)) for i in (1, 2))
    sl, st = g(m, "specificationListBlock"), g(m, "specificationTextBlock")
    spec = (T(g(m, "specificationHeadline"), "h2") + T(g(sl, "headline"), "h3")
            + bullets(items(sl, "block", "textList")) + block_text(st))
    return T(g(m, "headline"), "h1") + cols(3, [image(c, g(m, "image"), L + "image", (300, 300)), desc, spec], "hl3")


def s_single_side_image(c, m, L):
    b = g(m, "block")
    return side(image(c, g(b, "image"), L + "block.image", (300, 300)), block_text(b, "h2"),
                image_right=m.get("imagePositionType") == "RIGHT", cls="narrow")


def _spec_tables(pairs, count):
    count = 2 if count == 2 else 1
    half = (len(pairs) + 1) // 2 if count == 2 else len(pairs)
    parts = [pairs[:half], pairs[half:]] if count == 2 else [pairs]
    return cols(count, ['<table class="tbl spec">%s</table>' % "".join(
        "<tr><th>%s</th><td>%s</td></tr>" % (k, v) for k, v in part) for part in parts if part], "specs")


def s_tech_specs(c, m, L):
    pairs = [(rich(g(x, "label")), rich(g(x, "description"))) for x in items(m, "specificationList")]
    return T(g(m, "headline"), "h1") + _spec_tables(pairs, num(m.get("tableCount")))


def s_text(c, m, L):
    return T(g(m, "headline"), "h1") + P(g(m, "body"))


def s_three_image_text(c, m, L):
    return T(g(m, "headline"), "h1") + cols(3, _image_blocks(c, m, L, 3, (300, 300)))


# ---------------------------------------------------------------- PREMIUM_* modules

def p_image_text(c, m, L):
    # positionType names where the TEXT sits: LEFT puts the text left and the image right
    # (measured on a live Premium page, 2026-11-26).
    txt = T(g(m, "subheadline"), "ptopic") + T(g(m, "headline"), "ph1") + P(g(m, "bodyText"), "pbody")
    img = image(c, g(m, "image"), L + "image", (800, 600))
    text_right = m.get("positionType") == "RIGHT"
    return '<div class="pit%s"><div class="pit-img">%s</div><div class="pit-txt">%s</div></div>' % (
        " text-right" if text_right else "", img, txt)


def p_text(c, m, L):
    return T(g(m, "headline"), "h1") + P(g(m, "description"))


def _bg(c, m, L):
    k, comp = c.pick(m)
    return image(c, comp, L + k, (600, 450) if c.mobile else (1464, 600))


def p_full_background_text(c, m, L):
    box = T(g(m, "subheadline"), "kick") + T(g(m, "headline"), "h1") + P(g(m, "description"))
    return overlay(_bg(c, m, L), box, right=m.get("positionType") == "RIGHT", dark=m.get("colorType") != "LIGHT")


def p_full_background_image(c, m, L):
    # Headline above the image, the footer below, both centred (live Premium page).
    return T(g(m, "headline"), "ph1 pfb-h ctr") + _bg(c, m, L) + P(g(m, "footer"), "pp1 pfb-f ctr")


def _image_columns(c, m, L, size):
    cells = []
    for i, it in enumerate(by_pos(items(m, "columns"), "imageColumn")):
        col = g(it, "imageColumn")
        cells.append(image(c, g(col, "image"), "%scolumns[%d].imageColumn.image" % (L, i), size)
                     + T(g(col, "headline"), "h3") + P(g(col, "description")))
    return cells


def p_four_column_images(c, m, L):
    cells = _image_columns(c, m, L, (300, 225))
    return T(g(m, "headline"), "h1 ctr") + cols(max(len(cells), 1), cells)


def p_dual_image_text(c, m, L):
    return T(g(m, "headline"), "h1 ctr") + cols(2, _image_columns(c, m, L, (650, 350)))


def _panels(m, key):
    return [(i, g(it, key)) for i, it in enumerate(by_pos(items(m, "carouselCards"), key))]


def _panel_img(c, p, L, i, key):
    k, comp = c.pick(p)
    return image(c, comp, "%scarouselCards[%d].%s.%s" % (L, i, key, k), (600, 450) if c.mobile else (1464, 600))


def p_image_carousel(c, m, L):
    cards = []
    for i, p in _panels(m, "imagePanel"):
        btn = '<span class="btn">%s</span>' % rich(g(p, "buttonText")) if text_of(g(p, "buttonText")).strip() else ""
        asin = '<div class="asin">ASIN %s</div>' % esc(text_of(g(p, "asin"))) if text_of(g(p, "asin")) else ""
        cards.append(_panel_img(c, p, L, i, "imagePanel") + T(g(p, "title"), "h2") + P(g(p, "description")) + btn + asin)
    return T(g(m, "headline"), "h1 ctr") + strip(cards, "Panel") + P(g(m, "footer"), "body ctr")


def p_navigation_carousel(c, m, L):
    panels = _panels(m, "navigationPanel")
    cards = [_panel_img(c, p, L, i, "navigationPanel") + T(g(p, "subtitle"), "kick") + T(g(p, "title"), "h2")
             + P(g(p, "description")) for i, p in panels]
    return tabs([g(p, "navText") for _, p in panels]) + strip(cards, "Panel")


def p_regimen_carousel(c, m, L):
    panels = _panels(m, "regimenPanel")
    cards = [overlay(_panel_img(c, p, L, i, "regimenPanel"), T(g(p, "title"), "h2") + P(g(p, "description")),
                     dark=False) for i, p in panels]
    return T(g(m, "headline"), "h1 ctr") + tabs([g(p, "navText") for _, p in panels]) + strip(cards, "Step")


def _product_head(c, prod, label, size, desk="desktopImage", mob="mobileImage", required=True, img_key=None):
    if img_key:
        comp, k = g(prod, img_key), img_key
    else:
        k, comp = c.pick(prod, desk, mob)
    cell = image(c, comp, label + "." + k, size, required=required)
    asin = text_of(g(prod, "productAsin"))
    return cell + T(g(prod, "productTitle"), "h4") + ('<div class="asin">%s</div>' % esc(asin) if asin else "")


def p_three_column_comparison(c, m, L):
    prods = by_pos(items(m, "comparisonProducts"))
    head = [""] + [_product_head(c, p, "%scomparisonProducts[%d]" % (L, i), (300, 225), img_key="image")
                   for i, p in enumerate(prods)]
    rows = []
    for r in by_pos(items(m, "comparisonRows")):
        vals = items(r, "metricValues")
        name = next((rich(g(v, "metricName")) for v in vals if text_of(g(v, "metricName")).strip()), "")
        rows.append([name] + [P(g(v, "metricValue"), "cellp") for v in vals])
    return T(g(m, "headline"), "h1 ctr") + table(head, rows, "cmp")


def _compare_rows(rows, prods, key):
    out = []
    ppos = [num(g(p, "comparisonProduct", "position")) for p in prods]
    for r in by_pos(rows, key):
        row = g(r, key)
        check = text_of(g(row, "comparisonType")).strip().lower() == "checkbox"
        fields = {num(g(f, "comparisonField", "position")): text_of(g(f, "comparisonField", "value"))
                  for f in items(row, "comparisonFields")}
        info = T(g(row, "additionalInfo"), "info")
        cells = [rich(g(row, "metricName")) + info]
        for p in ppos:
            v = fields.get(p, "")
            if check:
                v = '<span class="yes">&#10003;</span>' if v.strip().lower() == "true" else '<span class="no">&mdash;</span>'
            else:
                v = esc(v)
            cells.append(v)
        out.append(cells)
    return out


def p_comparison_carousel(c, m, L):
    prods = by_pos(items(m, "comparisonProducts"), "comparisonProduct")
    head = [""] + [_product_head(c, g(p, "comparisonProduct"), "%scomparisonProducts[%d].comparisonProduct" % (L, i),
                                 (600, 450) if c.mobile else (488, 700)) for i, p in enumerate(prods)]
    return T(g(m, "headline"), "h1 ctr") + table(head, _compare_rows(items(m, "comparisonMetrics"), prods,
                                                                      "comparisonRow"), "cmp")


def p_comparison_scroller(c, m, L):
    prods = by_pos(items(m, "comparisonProducts"), "comparisonProduct")
    head = [""] + [_product_head(c, g(p, "comparisonProduct"), "%scomparisonProducts[%d].comparisonProduct" % (L, i),
                                 (200, 225), img_key="desktopImage") for i, p in enumerate(prods)]
    rows = _compare_rows(items(m, "comparisonRows"), prods, "comparisonRow")
    for flag, name in (("showPrices", "Price"), ("showReviews", "Customer reviews"), ("showATC", "Add to Cart")):
        if m.get(flag) is True:
            rows.insert(0, [name] + ['<span class="auto">from Amazon</span>'] * len(prods))
    return T(g(m, "headline"), "h1 ctr") + table(head, rows, "cmp")


def _hotspots(c, m, L, key):
    comp = g(m, "desktopImage")
    cr = crop_of(comp)
    fw, fh = (cr[2], cr[3]) if cr else (1464.0, 600.0)
    spots = items(m, "hotSpots")
    dots, legend, cards = [], [], []
    for i, it in enumerate(spots):
        hs = g(it, key)
        x, y = num(text_of(g(hs, "xCoordinate"))), num(text_of(g(hs, "yCoordinate")))
        if x is not None and y is not None:
            dots.append('<b class="dot" style="left:%.2f%%;top:%.2f%%">%d</b>'
                        % (max(0, min(100, x / fw * 100)), max(0, min(100, y / fh * 100)), i + 1))
        legend.append("<li>%s%s</li>" % (T(g(hs, "title"), "h4"), T(g(hs, "description"), "body")))
        if c.mobile:
            cards.append(image(c, g(hs, "mobileImage"), "%shotSpots[%d].%s.mobileImage" % (L, i, key), (600, 450))
                         + T(g(hs, "title"), "h4") + T(g(hs, "description"), "body"))
    base = image(c, comp, L + "desktopImage", (1464, 600))
    out = '<div class="hs">%s%s</div>' % (base, "".join(dots))
    if c.mobile:
        return out + strip(cards, "Hotspot")
    return out + '<ol class="legend">%s</ol>' % "".join(legend)


def p_hotspot_image(c, m, L):
    return _hotspots(c, m, L, "imageHotSpot")


def p_hotspot_image_text(c, m, L):
    return T(g(m, "headline"), "h1 ctr") + P(g(m, "mainDescription"), "body ctr") + _hotspots(c, m, L, "imageTextHotSpot")


def p_faq(c, m, L):
    dark = m.get("colorType") == "DARK"
    qa = "".join('<div class="qa"><div class="q">%s</div>%s</div>' % (P(g(it, "faq", "question"), "qp"),
                                                                       P(g(it, "faq", "answer")))
                 for it in items(m, "faqs"))
    return '<div class="faq %s">%s</div>' % ("dark" if dark else "light", qa)


def p_tech_specs(c, m, L):
    pairs = [(rich(g(x, "techSpec", "specKey")), rich(g(x, "techSpec", "specValue"))) for x in items(m, "techSpecs")]
    return T(g(m, "headline"), "h1") + _spec_tables(pairs, num(m.get("columnCount")))


def p_video_text(c, m, L):
    txt = T(g(m, "title"), "kick") + T(g(m, "headline"), "h1") + P(g(m, "description"))
    return side(video(c, g(m, "video"), L + "video", (800, 600)), txt, image_right=m.get("positionType") == "RIGHT")


def p_hero_video(c, m, L):
    return (video(c, g(m, "heroVideo"), L + "heroVideo", (1464, 600)) + T(g(m, "headline"), "h1 ctr")
            + P(g(m, "footer"), "body ctr"))


def p_video_image_carousel(c, m, L):
    cards = []
    for i, p in _panels(m, "videoCarouselPanel"):
        lbl = "%scarouselCards[%d].videoCarouselPanel." % (L, i)
        if isinstance(g(p, "video"), dict):
            media = video(c, g(p, "video"), lbl + "video", (800, 600))
        else:
            k, comp = c.pick(p)
            media = image(c, comp, lbl + k, (600, 450) if c.mobile else (800, 600))
        txt = T(g(p, "title"), "kick") + T(g(p, "subheadline"), "h2") + P(g(p, "description"))
        cards.append(side(media, txt, image_right=g(p, "positionType") == "RIGHT"))
    return T(g(m, "headline"), "h1 ctr") + strip(cards, "Panel")


# ---------------------------------------------------------------- BRAND_STORY_* modules (cards)

def b_about(c, m, L):
    return ('<div class="bcard about">%s%s%s</div>'
            % (image(c, g(m, "logoImage"), L + "logoImage", (315, 145)), T(g(m, "title"), "h3"), P(g(m, "slogan"))))


def b_media_asset(c, m, L):
    txt = T(g(m, "title"), "h3") + P(g(m, "description"))
    return '<div class="bcard media">%s%s</div>' % (
        image(c, g(m, "image"), L + "image", (362, 453)), '<div class="mtx">%s</div>' % txt if txt else "")


def b_four_asin(c, m, L):
    cells = []
    for i, it in enumerate(items(m, "asinImages")):
        a = g(it, "asinImage")
        cells.append('<div class="fa-cell" title="%s">%s</div>' % (
            esc(text_of(g(a, "productAsin"))),
            image(c, g(a, "productImage"), "%sasinImages[%d].asinImage.productImage" % (L, i), (166, 182))))
    store = '<div class="store">Visit the Store</div>' if text_of(g(m, "brandStoreId")).strip() else ""
    return '<div class="bcard four"><div class="fa-grid">%s</div>%s%s</div>' % (
        "".join(cells), T(g(m, "title"), "fa-title"), store)


def b_questions(c, m, L):
    qa = "".join('<div class="qa">%s%s</div>' % (T(g(it, "questionAnswerPair", "question"), "q"),
                                                 P(g(it, "questionAnswerPair", "answer")))
                 for it in items(m, "questionAnswerPairs"))
    return '<div class="bcard qs">%s</div>' % qa


def b_image_with_logo(c, m, L):
    """Used as a card only when a second one is present; the first is the background."""
    k, comp = c.pick(m)
    return '<div class="bcard media">%s<div class="mtx">%s%s</div></div>' % (
        image(c, comp, L + k, (463, 625) if c.mobile else (1464, 625)), T(g(m, "title"), "h3"), P(g(m, "description")))


# ---------------------------------------------------------------- module registry and limits

def _x(path):
    """Expand 'block{1-4}.headline' into its four paths."""
    mm = re.search(r"\{(\d+)-(\d+)\}", path)
    if not mm:
        return [path]
    return [path[:mm.start()] + str(i) + path[mm.end():] for i in range(int(mm.group(1)), int(mm.group(2)) + 1)]


# kind: v = text value max chars, p = paragraph total max chars, r = paragraph max rows, n = (min, max) items
MODULES = {
    "STANDARD_COMPANY_LOGO": ("standardCompanyLogo", s_company_logo, []),
    "STANDARD_COMPARISON_TABLE": ("standardComparisonTable", s_comparison_table, [
        ("productColumns", "n", (0, 6)), ("productColumns[].title", "v", 80),
        ("productColumns[].metrics", "n", (0, 10)), ("productColumns[].metrics[]", "v", 250),
        ("metricRowLabels", "n", (0, 10)), ("metricRowLabels[]", "v", 100)]),
    "STANDARD_FOUR_IMAGE_TEXT": ("standardFourImageText", s_four_image_text, [
        ("headline", "v", 200), ("block{1-4}.headline", "v", 160), ("block{1-4}.body", "p", 1000)]),
    "STANDARD_FOUR_IMAGE_TEXT_QUADRANT": ("standardFourImageTextQuadrant", s_four_image_text_quadrant, [
        ("block{1-4}.headline", "v", 160), ("block{1-4}.body", "p", 1000)]),
    "STANDARD_HEADER_IMAGE_TEXT": ("standardHeaderImageText", s_header_image_text, [
        ("headline", "v", 150), ("block.headline", "v", 150), ("block.body", "p", 6000)]),
    "STANDARD_IMAGE_SIDEBAR": ("standardImageSidebar", s_image_sidebar, [
        ("headline", "v", 160), ("descriptionTextBlock.headline", "v", 200), ("descriptionTextBlock.body", "p", 500),
        ("descriptionListBlock.textList", "n", (0, 8)), ("descriptionListBlock.textList[].text", "v", 200),
        ("imageCaptionBlock.caption", "v", 200), ("sidebarImageTextBlock.headline", "v", 200),
        ("sidebarImageTextBlock.body", "p", 500), ("sidebarListBlock.textList", "n", (0, 8)),
        ("sidebarListBlock.textList[].text", "v", 200)]),
    "STANDARD_IMAGE_TEXT_OVERLAY": ("standardImageTextOverlay", s_image_text_overlay, [
        ("block.headline", "v", 70), ("block.body", "p", 300)]),
    "STANDARD_MULTIPLE_IMAGE_TEXT": ("standardMultipleImageText", s_multiple_image_text, [
        ("blocks[].block.headline", "v", 160), ("blocks[].block.body", "p", 1000), ("blocks[].caption", "v", 200)]),
    "STANDARD_PRODUCT_DESCRIPTION": ("standardProductDescription", s_product_description, [("body", "p", 6000)]),
    "STANDARD_SINGLE_IMAGE_HIGHLIGHTS": ("standardSingleImageHighlights", s_single_image_highlights, [
        ("headline", "v", 160), ("textBlock1.headline", "v", 200), ("textBlock1.body", "p", 1000),
        ("textBlock{2-3}.headline", "v", 200), ("textBlock{2-3}.body", "p", 400),
        ("bulletedListBlock.headline", "v", 160), ("bulletedListBlock.block.textList", "n", (0, 8)),
        ("bulletedListBlock.block.textList[].text", "v", 100)]),
    "STANDARD_SINGLE_IMAGE_SPECS_DETAIL": ("standardSingleImageSpecsDetail", s_single_image_specs_detail, [
        ("headline", "v", 200), ("descriptionHeadline", "v", 160), ("descriptionBlock{1-2}.headline", "v", 200),
        ("descriptionBlock{1-2}.body", "p", 400), ("specificationHeadline", "v", 160),
        ("specificationListBlock.headline", "v", 200), ("specificationListBlock.block.textList", "n", (0, 8)),
        ("specificationListBlock.block.textList[].text", "v", 200), ("specificationTextBlock.headline", "v", 200),
        ("specificationTextBlock.body", "p", 1000)]),
    "STANDARD_SINGLE_SIDE_IMAGE": ("standardSingleSideImage", s_single_side_image, [
        ("block.headline", "v", 160), ("block.body", "p", 1000)]),
    "STANDARD_TECH_SPECS": ("standardTechSpecs", s_tech_specs, [
        ("headline", "v", 80), ("specificationList", "n", (4, 16)), ("specificationList[].label", "v", 30),
        ("specificationList[].description", "v", 500)]),
    "STANDARD_TEXT": ("standardText", s_text, [("headline", "v", 160), ("body", "p", 5000)]),
    "STANDARD_THREE_IMAGE_TEXT": ("standardThreeImageText", s_three_image_text, [
        ("headline", "v", 200), ("block{1-3}.headline", "v", 160), ("block{1-3}.body", "p", 1000)]),

    "PREMIUM_IMAGE_TEXT": ("premiumImageText", p_image_text, [
        ("headline", "v", 80), ("subheadline", "v", 40), ("bodyText", "r", 5), ("bodyText", "p", 500)]),
    "PREMIUM_TEXT": ("premiumText", p_text, [("headline", "v", 80), ("description", "r", 11),
                                             ("description", "p", 5000)]),
    "PREMIUM_FULL_BACKGROUND_TEXT": ("premiumFullBackgroundText", p_full_background_text, [
        ("subheadline", "v", 40), ("headline", "v", 60), ("description", "r", 2), ("description", "p", 300)]),
    "PREMIUM_FULL_BACKGROUND_IMAGE": ("premiumFullBackgroundImage", p_full_background_image, [
        ("headline", "v", 80), ("footer", "r", 4), ("footer", "p", 300)]),
    "PREMIUM_FOUR_COLUMN_IMAGES": ("premiumFourColumnImages", p_four_column_images, [
        ("headline", "v", 80), ("columns", "n", (3, 4)), ("columns[].imageColumn.headline", "v", 30),
        ("columns[].imageColumn.description", "r", 5), ("columns[].imageColumn.description", "p", 150)]),
    "PREMIUM_DUAL_IMAGE_TEXT": ("premiumDualImageText", p_dual_image_text, [
        ("headline", "v", 50), ("columns", "n", (2, 2)), ("columns[].imageColumn.headline", "v", 50),
        ("columns[].imageColumn.description", "r", 5), ("columns[].imageColumn.description", "p", 300)]),
    "PREMIUM_IMAGE_CAROUSEL": ("premiumImageCarousel", p_image_carousel, [
        ("headline", "v", 80), ("footer", "r", 4), ("footer", "p", 300), ("carouselCards", "n", (2, 6)),
        ("carouselCards[].imagePanel.title", "v", 50), ("carouselCards[].imagePanel.buttonText", "v", 12),
        ("carouselCards[].imagePanel.description", "r", 4), ("carouselCards[].imagePanel.description", "p", 200)]),
    "PREMIUM_NAVIGATION_CAROUSEL": ("premiumNavigationCarousel", p_navigation_carousel, [
        ("carouselCards", "n", (2, 5)), ("carouselCards[].navigationPanel.navText", "v", 25),
        ("carouselCards[].navigationPanel.title", "v", 50), ("carouselCards[].navigationPanel.subtitle", "v", 25),
        ("carouselCards[].navigationPanel.description", "r", 4),
        ("carouselCards[].navigationPanel.description", "p", 100)]),
    "PREMIUM_REGIMEN_CAROUSEL": ("premiumRegimenCarousel", p_regimen_carousel, [
        ("headline", "v", 100), ("carouselCards", "n", (2, 5)), ("carouselCards[].regimenPanel.navText", "v", 20),
        ("carouselCards[].regimenPanel.title", "v", 20), ("carouselCards[].regimenPanel.description", "r", 4),
        ("carouselCards[].regimenPanel.description", "p", 100)]),
    "PREMIUM_THREE_COLUMN_COMPARISON": ("premiumThreeColumnComparison", p_three_column_comparison, [
        ("headline", "v", 80), ("comparisonProducts", "n", (3, 3)), ("comparisonProducts[].productTitle", "v", 30),
        ("comparisonRows", "n", (2, 5)), ("comparisonRows[].metricValues", "n", (3, 3)),
        ("comparisonRows[].metricValues[].metricName", "v", 30),
        ("comparisonRows[].metricValues[].metricValue", "r", 1),
        ("comparisonRows[].metricValues[].metricValue", "p", 80)]),
    "PREMIUM_COMPARISON_CAROUSEL": ("premiumComparisonCarousel", p_comparison_carousel, [
        ("headline", "v", 25), ("comparisonProducts", "n", (3, 5)),
        ("comparisonProducts[].comparisonProduct.productTitle", "v", 25), ("comparisonMetrics", "n", (3, 7)),
        ("comparisonMetrics[].comparisonRow.metricName", "v", 20),
        ("comparisonMetrics[].comparisonRow.comparisonFields[].comparisonField", "v", 20)]),
    "PREMIUM_COMPARISON_SCROLLER": ("premiumComparisonScroller", p_comparison_scroller, [
        ("headline", "v", 80), ("comparisonProducts", "n", (3, 7)),
        ("comparisonProducts[].comparisonProduct.productTitle", "v", 25), ("comparisonRows", "n", (5, 12)),
        ("comparisonRows[].comparisonRow.metricName", "v", 30),
        ("comparisonRows[].comparisonRow.additionalInfo", "v", 150),
        ("comparisonRows[].comparisonRow.comparisonFields[].comparisonField", "v", 30)]),
    "PREMIUM_HOTSPOT_IMAGE": ("premiumHotspotImage", p_hotspot_image, [
        ("hotSpots", "n", (2, 6)), ("hotSpots[].imageHotSpot.title", "v", 50),
        ("hotSpots[].imageHotSpot.description", "v", 200)]),
    "PREMIUM_HOTSPOT_IMAGE_TEXT": ("premiumHotspotImageText", p_hotspot_image_text, [
        ("headline", "v", 80), ("mainDescription", "r", 2), ("mainDescription", "p", 300), ("hotSpots", "n", (2, 6)),
        ("hotSpots[].imageTextHotSpot.title", "v", 50)]),
    "PREMIUM_FAQ": ("premiumFaq", p_faq, [
        ("faqs", "n", (2, 5)), ("faqs[].faq.question", "r", 1), ("faqs[].faq.question", "p", 120),
        ("faqs[].faq.answer", "r", 5), ("faqs[].faq.answer", "p", 250)]),
    "PREMIUM_TECH_SPECS": ("premiumTechSpecs", p_tech_specs, [
        ("headline", "v", 80), ("techSpecs", "n", (4, 16)), ("techSpecs[].techSpec.specKey", "v", 30),
        ("techSpecs[].techSpec.specValue", "v", 500)]),
    "PREMIUM_VIDEO_TEXT": ("premiumVideoText", p_video_text, [
        ("headline", "v", 80), ("title", "v", 40), ("description", "r", 5), ("description", "p", 500)]),
    "PREMIUM_HERO_VIDEO": ("premiumHeroVideo", p_hero_video, [
        ("headline", "v", 80), ("footer", "r", 4), ("footer", "p", 300)]),
    "PREMIUM_VIDEO_IMAGE_CAROUSEL": ("premiumVideoImageCarousel", p_video_image_carousel, [
        ("headline", "v", 80), ("carouselCards", "n", (2, 6)),
        ("carouselCards[].videoCarouselPanel.subheadline", "v", 80),
        ("carouselCards[].videoCarouselPanel.title", "v", 50),
        ("carouselCards[].videoCarouselPanel.description", "r", 4),
        ("carouselCards[].videoCarouselPanel.description", "p", 500)]),

    "BRAND_STORY_IMAGE_WITH_LOGO": ("brandStoryImageWithLogo", b_image_with_logo, [
        ("title", "v", 30), ("description", "r", 3), ("description", "p", 135)]),
    "BRAND_STORY_FOUR_ASIN": ("brandStoryFourAsin", b_four_asin, [
        ("title", "v", 30), ("brandStoreId", "v", 100), ("asinImages", "n", (4, 4))]),
    "BRAND_STORY_MEDIA_ASSET": ("brandStoryMediaAsset", b_media_asset, [
        ("title", "v", 30), ("description", "r", 3), ("description", "p", 135)]),
    "BRAND_STORY_ABOUT": ("brandStoryAbout", b_about, [
        ("title", "v", 30), ("slogan", "r", 10), ("slogan", "p", 450)]),
    "BRAND_STORY_QUESTIONS": ("brandStoryQuestions", b_questions, [
        ("questionAnswerPairs", "n", (3, 3)), ("questionAnswerPairs[].questionAnswerPair.question", "v", 70),
        ("questionAnswerPairs[].questionAnswerPair.answer", "r", 3),
        ("questionAnswerPairs[].questionAnswerPair.answer", "p", 200)]),
}
KEY_TO_TYPE = {v[0]: k for k, v in MODULES.items()}


def family(t):
    return "BRAND_STORY" if str(t).startswith("BRAND_STORY_") else str(t).split("_", 1)[0]


def resolve(node, path):
    """Every (concrete path, value) a limit path names; '[]' walks a list."""
    found = [("", node)]
    for part in path.split("."):
        arr = part.endswith("[]")
        key = part[:-2] if arr else part
        nxt = []
        for here, n in found:
            v = n.get(key) if isinstance(n, dict) else None
            if v is None:
                continue
            p = "%s.%s" % (here, key) if here else key
            if arr and isinstance(v, list):
                nxt += [("%s[%d]" % (p, i), x) for i, x in enumerate(v)]
            elif not arr:
                nxt.append((p, v))
        found = nxt
    return found


def check_limits(label, body, limits, warn):
    for path, kind, arg in limits:
        for one in _x(path):
            for where, v in resolve(body, one):
                if kind == "v":
                    n = len(text_of(v))
                    if n > arg:
                        warn("%s %s: %d characters, the limit is %d." % (label, where, n, arg))
                elif kind == "p":
                    n = sum(len(t) for t in para_texts(v))
                    if n > arg:
                        warn("%s %s: %d characters in total, the limit is %d." % (label, where, n, arg))
                elif kind == "r":
                    n = len(items(v, "textList"))
                    if n > arg:
                        warn("%s %s: %d text rows, the limit is %d." % (label, where, n, arg))
                elif kind == "n" and isinstance(v, list):
                    lo, hi = arg
                    if not lo <= len(v) <= hi:
                        want = "exactly %d" % lo if lo == hi else "%d to %d" % (lo, hi)
                        warn("%s %s: %d items, the schema allows %s." % (label, where, len(v), want))
                    seen = [num(g(x, "position")) if "position" in x else num(g(next(iter(x.values()), None), "position"))
                            for x in v if isinstance(x, dict) and x]
                    dup = sorted(set(p for p in seen if p is not None and seen.count(p) > 1))
                    if dup:
                        warn("%s %s: duplicate position %s (positions are unique)." % (
                            label, where, ", ".join("%g" % d for d in dup)))


def check_document(doc, warn):
    name = text_of(doc.get("name"))
    if not 1 <= len(name) <= 100:
        warn("Document name: %d characters, the schema allows 1 to 100." % len(name))
    ctype = doc.get("contentType")
    if ctype not in ("EBC", "EMC", "BrandStory"):
        warn("contentType %s is not one of EBC, EMC, BrandStory." % json.dumps(ctype))
    loc = doc.get("locale")
    if not isinstance(loc, str) or not loc:
        warn("locale is missing (a hyphenated tag such as en-US).")
    elif "_" in loc:
        warn("locale %s uses an underscore; the locale is hyphenated (en-US)." % loc)
    mods = doc.get("contentModuleList")
    if not 1 <= len(mods) <= 100:
        warn("contentModuleList: %d modules, the schema allows 1 to 100." % len(mods))
    fams = {}
    for i, m in enumerate(mods):
        label = "Module %d" % (i + 1)
        if not isinstance(m, dict):
            warn("%s is not an object." % label)
            continue
        t = m.get("contentModuleType")
        spec = MODULES.get(t)
        others = [k for k in m if k in KEY_TO_TYPE and (not spec or k != spec[0])]
        if not spec:
            warn("%s: unknown module type %s." % (label, json.dumps(t)))
            continue
        fams.setdefault(family(t), []).append(i + 1)
        key = spec[0]
        if not isinstance(m.get(key), dict):
            hint = " (found %s, the key of %s)" % (others[0], KEY_TO_TYPE[others[0]]) if others else ""
            warn("%s (%s): module key %s is missing%s." % (label, t, key, hint))
        elif others:
            warn("%s (%s): also carries %s, which does not match contentModuleType." % (label, t, ", ".join(others)))
        if isinstance(m.get(key), dict):
            check_limits("%s (%s)" % (label, t), m[key], spec[2], warn)
    if len(fams) > 1:
        warn("Mixed module families in one document: %s. A document holds one family only." % "; ".join(
            "%s (modules %s)" % (f, ", ".join(map(str, ix))) for f, ix in fams.items()))
    if len(fams.get("PREMIUM", [])) > PREMIUM_MAX_MODULES:
        warn("%d Premium modules; a Premium document holds at most %d." % (len(fams["PREMIUM"]), PREMIUM_MAX_MODULES))
    if "BRAND_STORY" in fams or ctype == "BrandStory":
        n = sum(1 for m in mods if isinstance(m, dict) and m.get("contentModuleType") == "BRAND_STORY_IMAGE_WITH_LOGO")
        if n != 1:
            warn("A Brand Story holds exactly one BRAND_STORY_IMAGE_WITH_LOGO; this one has %d." % n)
        first = mods[0] if mods and isinstance(mods[0], dict) else {}
        if n and first.get("contentModuleType") != "BRAND_STORY_IMAGE_WITH_LOGO":
            warn("BRAND_STORY_IMAGE_WITH_LOGO must be the first module; Amazon refuses the "
                 "submission otherwise.")
        if len(mods) < 3:
            warn("A Brand Story needs at least 3 modules for Amazon to accept the submission; "
                 "this one has %d." % len(mods))
        if ctype != "BrandStory":
            warn("BRAND_STORY_* modules need contentType BrandStory (this document says %s)." % json.dumps(ctype))
    elif ctype == "BrandStory" and fams:
        warn("contentType BrandStory takes BRAND_STORY_* modules only.")


# ---------------------------------------------------------------- page

def render_module(ctx, i, m):
    label = "Module %d" % (i + 1)
    if not isinstance(m, dict):
        return '<section class="mod"><div class="lbl">%s</div><div class="bad">Not an object.</div></section>' % label
    t = m.get("contentModuleType")
    spec = MODULES.get(t)
    head = '<div class="lbl">%d &middot; %s</div>' % (i + 1, esc(t))
    if not spec:
        return '<section class="mod">%s<div class="bad">Unknown module type: %s</div></section>' % (head, esc(t))
    body = m.get(spec[0])
    if not isinstance(body, dict):
        return '<section class="mod">%s<div class="bad">Module key %s is missing.</div></section>' % (head, esc(spec[0]))
    return '<section class="mod %s">%s%s</section>' % (family(t).lower(), head, spec[1](ctx, body, label + " "))


def render_brand_story(ctx, mods):
    first = next((i for i, m in enumerate(mods) if isinstance(m, dict)
                  and m.get("contentModuleType") == "BRAND_STORY_IMAGE_WITH_LOGO"), None)
    bg_html, intro, cards = "", "", []
    if first is not None:
        m = g(mods[first], "brandStoryImageWithLogo") or {}
        k, comp = ctx.pick(m)
        bg_html = image(ctx, comp, "Module %d %s" % (first + 1, k), (463, 625) if ctx.mobile else (1464, 625))
        # The logo card is the background's own first panel: empty when the document has no
        # title or description (the brand's panel is then part of the image itself).
        words = T(g(m, "title"), "h2") + P(g(m, "description"))
        intro = ('<div class="card intro%s"><span class="pos">%d &middot; BRAND_STORY_IMAGE_WITH_LOGO</span>%s</div>'
                 % ("" if words else " blank", first + 1,
                    '<div class="blogo">Brand logo</div>' + words if words else ""))
    for i, m in enumerate(mods):
        if i == first:
            continue
        t = m.get("contentModuleType") if isinstance(m, dict) else None
        spec = MODULES.get(t)
        body = g(m, spec[0]) if spec else None
        inner = spec[1](ctx, body, "Module %d " % (i + 1)) if spec and isinstance(body, dict) else \
            '<div class="bad">%s</div>' % esc(t or "not an object")
        cards.append('<div class="card"><span class="pos">%d &middot; %s</span>%s</div>' % (i + 1, esc(t), inner))
    if first is None:
        bg_html = placeholder("BRAND_STORY_IMAGE_WITH_LOGO", (1464, 625), "missing")
    dots = '<div class="bdots">%s</div>' % "".join(
        '<i%s></i>' % (' class="on"' if j == 0 else "") for j in range(len(cards) + 1)) if ctx.mobile else ""
    arrows = '' if ctx.mobile else '<i class="barrow l"></i><i class="barrow r"></i>'
    return ('<section class="mod brand"><div class="bs">%s<div class="bstrip">%s%s</div>%s</div>%s</section>'
            % (bg_html, intro, "".join(cards), arrows, dots))


CSS = """
:root{--ink:#0f1111;--muted:#565959;--line:#d5d9d9;--ph:#e3e6e6;--accent:#007185;--page:#f3f3f3}
*{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--ink);font:14px/1.45 "Amazon Ember",Arial,Helvetica,sans-serif}
.vt{position:absolute;opacity:0;pointer-events:none}
header{background:#232f3e;color:#fff;padding:14px 16px}
header h1{font-size:18px;margin:0 0 4px}header .meta{color:#c8ccd0;font-size:13px}
nav{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;align-items:center}
nav label{cursor:pointer;border:1px solid #6b7785;border-radius:4px;padding:4px 12px;font-size:13px;user-select:none}
#v-d:checked~header label[for=v-d],#v-m:checked~header label[for=v-m],#v-b:checked~header label[for=v-b],
#v-l:checked~header label[for=v-l]{background:#fff;color:#232f3e}
.checks{margin:0;background:#fff8e6;border-bottom:1px solid #f0d28a;padding:10px 16px;font-size:13px}
.checks.ok{background:#eef8f1;border-color:#b6dfc2}.checks h2{font-size:14px;margin:0 0 4px}
.checks ul{margin:0;padding-left:20px}.note{color:var(--muted);font-size:12px;padding:8px 16px 0}
main{display:flex;gap:24px;padding:16px;overflow-x:auto;align-items:flex-start}
#v-d:checked~main .pane.m,#v-m:checked~main .pane.d{display:none}
.lbl,.pos{display:none}#v-l:checked~main .lbl{display:block}#v-l:checked~main .pos{display:inline-block}
.pane{flex:0 0 auto}.pane>h2{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:0 0 8px}
.frame{background:#fff;padding:16px;border:1px solid var(--line)}
.frame.std{width:1002px}.frame.wide{width:1496px;zoom:.66;font-size:20px}
.frame.phone{width:375px;padding:12px;border-radius:24px;border:8px solid #232f3e}
.mod{margin:0 0 28px}.mod:last-child{margin-bottom:0}
.lbl{font:11px/1.4 Menlo,Consolas,monospace;color:var(--accent);margin:0 0 6px}.wide .lbl,.wide .pos{font-size:16px}
.h1{font-size:1.5em;font-weight:700;margin:0 0 .4em}.h2{font-size:1.25em;font-weight:700;margin:.4em 0}
.h3{font-size:1.07em;font-weight:700;margin:.5em 0 .2em}.h4{font-weight:700;margin:.4em 0 .1em}
.kick{text-transform:uppercase;letter-spacing:.06em;font-size:.85em;color:var(--muted);margin:.3em 0}
.body p,.qp p,.cellp p{margin:0 0 .5em}.body p:last-child{margin-bottom:0}.ctr{text-align:center}
.cap{font-size:.9em;color:var(--muted);margin-top:.3em}.info{font-size:.8em;color:var(--muted);font-weight:400}
.asin{font:12px Menlo,Consolas,monospace;color:var(--muted)}.wide .asin{font-size:16px}
.bul{margin:.3em 0;padding-left:1.2em}.tx ul,.tx ol{margin:.2em 0;padding-left:1.2em}
.slot{position:relative;overflow:hidden;background:var(--ph);width:100%}
.slot img,.slot video{display:block;width:100%;height:100%;object-fit:cover}
.slot img.cropped{position:absolute;height:auto;max-width:none;object-fit:fill}
.ph{display:flex;align-items:center;justify-content:center;text-align:center;background:var(--ph);color:var(--muted);
 font-size:12px;line-height:1.35;padding:8px;width:100%;border:1px dashed #b7bdbd;overflow:hidden;word-break:break-all;position:relative}
.wide .ph{font-size:17px}
.vidph{background:#2f3a47;color:#d6dbe0;border-color:#2f3a47}
.play{position:absolute;left:50%;top:50%;width:56px;height:56px;margin:-28px 0 0 -28px;border-radius:50%;background:rgba(0,0,0,.55);pointer-events:none}
.play:after{content:"";position:absolute;left:22px;top:16px;border-style:solid;border-width:12px 0 12px 18px;border-color:transparent transparent transparent #fff}
.vidph{flex-direction:column}.vidph .play{position:relative;left:auto;top:auto;margin:0 0 10px;flex:none}.ids{position:absolute;left:6px;bottom:6px;background:rgba(0,0,0,.6);color:#fff;font:11px Menlo,monospace;padding:2px 6px;font-style:normal}
.cols{display:grid;gap:16px}.c1{grid-template-columns:1fr}.c2{grid-template-columns:repeat(2,1fr)}
.c3{grid-template-columns:repeat(3,1fr)}.c4{grid-template-columns:repeat(4,1fr)}
.sidebar{grid-template-columns:1fr 1.3fr 1fr}.bar{background:#f7f8f8;padding:10px}
.side{display:flex;gap:24px;align-items:center}.side.rev{flex-direction:row-reverse}.side>.sm,.side>.st{flex:1 1 0;min-width:0}
.side.narrow>.sm{flex:0 0 300px}.side.q>.sm{flex:0 0 135px}.side.q{align-items:flex-start;gap:12px}
.logo{max-width:600px;margin:0 auto}
.ovl{position:relative}.ovl .box{position:absolute;top:8%;bottom:8%;width:40%;padding:1.2em;display:flex;flex-direction:column;justify-content:center;overflow:hidden}
.box.left{left:4%}.box.right{right:4%}.box.dark{background:rgba(15,17,17,.62);color:#fff}.box.dark .kick{color:#d6dbe0}
.box.light{background:rgba(255,255,255,.82)}
.strip{display:flex;gap:16px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:8px}
.strip>.card{flex:0 0 72%;scroll-snap-align:start;position:relative}
.pos{display:inline-block;font:11px Menlo,Consolas,monospace;color:var(--accent);margin-bottom:4px}
.btn{display:inline-block;background:#ffd814;border-radius:20px;padding:.25em 1em;margin:.3em 0;font-size:.9em}
.tabs{display:flex;gap:4px;justify-content:center;margin:0 0 10px;flex-wrap:wrap}
.tabs span{padding:.4em 1em;border-bottom:3px solid var(--line);color:var(--muted)}.tabs span.on{border-color:var(--ink);color:var(--ink);font-weight:700}
.tw{overflow-x:auto}.tbl{border-collapse:collapse;width:100%}
.tbl th,.tbl td{border:1px solid var(--line);padding:.5em .6em;text-align:center;vertical-align:top}
.tbl tbody th{text-align:left;background:#f7f8f8;width:18%}.tbl thead th{vertical-align:bottom;font-weight:400;min-width:110px}
.tbl thead .slot,.tbl thead .ph{max-width:200px;margin:0 auto}.hl{outline:3px solid #f0c14b;outline-offset:2px}
.yes{color:#067d62;font-weight:700}.no{color:#b7bdbd}.auto{color:var(--muted);font-style:italic;font-size:.85em}
.spec th{width:35%;text-align:left}.spec td{text-align:left}.specs{align-items:start}
.hs{position:relative}.dot{position:absolute;width:28px;height:28px;margin:-14px 0 0 -14px;border-radius:50%;background:#fff;border:3px solid #232f3e;font:700 13px/22px Arial;text-align:center;color:#232f3e}
.wide .dot{width:40px;height:40px;margin:-20px 0 0 -20px;font-size:18px;line-height:34px}
.legend{margin:.6em 0 0;padding-left:1.4em;columns:2}.legend li{break-inside:avoid;margin-bottom:.4em}
.faq{padding:1em 1.4em}.faq.dark{background:#232f3e;color:#fff}.faq.light{background:#f7f8f8}
.qa{padding:.6em 0;border-bottom:1px solid rgba(128,128,128,.3)}.qa:last-child{border:0}.q,.qp{font-weight:700}
.bs{position:relative}.bs>.slot,.bs>.ph{position:absolute;inset:0;height:100%}
.bstrip{position:relative;display:flex;gap:16px;overflow-x:auto;padding:28px;min-height:625px;align-items:center}
.bstrip>.card{flex:0 0 362px;height:453px;background:#fff;box-shadow:0 1px 6px rgba(0,0,0,.25);padding:10px;overflow:hidden}
.bstrip>.card.intro{flex-basis:420px;background:rgba(255,255,255,.86)}
.blogo{border:1px dashed #8d9696;color:var(--muted);font-size:.8em;padding:.6em;text-align:center;width:60%;margin:.4em 0 .6em}
.bcard .slot,.bcard .ph{margin-bottom:.4em}.bcard.media{position:relative;height:100%}.bcard.media>.slot,.bcard.media>.ph{height:100%}
.mtx{position:absolute;left:0;right:0;bottom:0;background:rgba(255,255,255,.88);padding:.5em .7em}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:8px}.four .g2>div{padding:0 13%}.store{margin-top:.4em;color:var(--accent);font-size:.9em}
.bad,.empty{background:#fdecea;color:#8a1c12;padding:12px;border:1px solid #f3b5ae}
/* mobile */
.phone .cols{grid-template-columns:1fr}.phone .side,.phone .side.rev{flex-direction:column;align-items:stretch;gap:10px}
.phone .side.narrow>.sm,.phone .side.q>.sm{flex:none}.phone .side.q{flex-direction:row}
.phone .ovl .box{position:static;width:auto;margin-top:0}.phone .strip>.card{flex-basis:86%}
.phone .h1{font-size:1.3em}.phone .legend{columns:1}.phone .quad{grid-template-columns:1fr}
.phone .bstrip{min-height:506px;padding:16px}.phone .bstrip>.card{flex:0 0 260px;height:380px}.phone .bstrip>.card.intro{flex-basis:260px}
.phone .tbl thead th{min-width:90px}
/* ---- Amazon product page, measured on live pages 2026-11-26 (desktop 1500 px window, mobile 375 px) ---- */
.lbl,.pos{display:none}#v-l:checked~main .lbl{display:block}#v-l:checked~main .pos{display:inline-block}
.frame{border:0;background:#fff}
.frame.wide,.frame.std{width:1500px;zoom:1;font-size:14px;padding:8px 18px 24px}
.frame.std .mod{max-width:970px;margin:0 auto 28px}
.wide .mod,.phone .mod.premium{margin:0}
.frame.phone{width:391px;padding:8px 15px 16px;font-size:16px}
.pdp-h{font-size:20px;line-height:32px;font-weight:700;margin:0;padding:0 0 4px}
.phone .pdp-h{font-size:18px;line-height:22px}
.ph1{font-size:32px;line-height:38.4px;font-weight:700;margin:0}
.phone .ph1{font-size:22px;line-height:26.4px}
.pfb-h{padding:40px 0}.phone .pfb-h{padding:20px 0}
.pp1 p{font-size:20px;line-height:26px;font-weight:300;margin:0}
.phone .pp1 p{font-size:15px;line-height:21px}
.pfb-f{padding:40px 0}.phone .pfb-f{padding:20px 0}
.pit{display:flex;padding:40px}
.pit>div{flex:0 0 50%;min-width:0}
.pit-txt{padding:40px;display:flex;flex-direction:column;justify-content:center;order:0}
.pit-img{order:1}.pit.text-right .pit-txt{order:2}
.ptopic{font-size:16px;line-height:22.4px;font-weight:700;padding-bottom:0}
.pit .ph1{padding-bottom:20px}
.pbody p{font-size:16px;line-height:22.4px;font-weight:300;margin:0 0 14px}
.phone .pit{display:block;padding:0}
.phone .pit-txt{padding:20px}
.phone .ptopic{font-size:13px;line-height:18.2px;padding-bottom:10px}
.phone .pbody p{font-size:15px;line-height:21px;margin:0 0 8px}
.bs{position:relative;height:625px;overflow:hidden}
.bs>.slot,.bs>.ph{position:absolute;inset:0;height:100%;aspect-ratio:auto!important}
.bs>.slot img{position:absolute;left:0!important;top:0!important;width:100%!important;height:100%!important;object-fit:cover}
.bstrip{position:absolute;left:72px;top:149px;right:0;display:flex;gap:30px;overflow:hidden;padding:0;min-height:0;align-items:flex-start}
.bstrip>.card{flex:0 0 362px;height:453px;background:#fff;box-shadow:none;padding:15px;overflow:hidden}
.bstrip>.card.intro{flex-basis:362px;background:#fff}.bstrip>.card.intro.blank{background:transparent}
.fa-grid{display:grid;grid-template-columns:162px 162px;grid-auto-rows:185px;gap:6px}
.fa-cell .slot,.fa-cell .ph{height:185px;aspect-ratio:auto!important;background:#fff;margin:0;padding:2px}
.fa-cell .slot img{object-fit:contain}
.fa-title{font-size:18px;line-height:24px;font-weight:700;margin:23px 0 0;padding:0 0 0 0}
.barrow{position:absolute;top:330px;width:34px;height:65px;background:#fff;border-radius:8px;box-shadow:0 2px 5px rgba(15,17,17,.15)}
.barrow.l{left:0}.barrow.r{right:0}
.barrow:after{content:"";position:absolute;top:27px;width:9px;height:9px;border:solid #0f1111;border-width:0 2px 2px 0}
.barrow.l:after{left:14px;transform:rotate(135deg)}.barrow.r:after{left:10px;transform:rotate(-45deg)}
.phone .bs{height:auto;padding:80px 0 0;overflow:hidden}
.phone .bstrip{position:relative;left:auto;top:auto;gap:16px;padding:0 2px 24px;overflow-x:auto}
.phone .bstrip>.card{flex:0 0 293px;height:auto;min-height:365px;padding:17px}
.phone .bstrip>.card.intro.blank{display:none}
.phone .fa-grid{grid-template-columns:124px 124px;grid-auto-rows:141px;gap:10px}
.phone .fa-cell .slot,.phone .fa-cell .ph{height:141px}
.phone .fa-title{font-size:16px;line-height:20px;margin-top:25px}
.bdots{display:flex;gap:4px;justify-content:center;padding:12px 0 4px}
.bdots i{width:16px;height:16px;border:1.5px solid #565959;border-radius:50%;margin:2px}
.bdots i.on{background:#c45500;border-color:#c45500}
/* every other Premium module: Amazon's Premium type scale (the same .aplus-h1 / .aplus-p2 / topic sizes) */
.mod.premium .h1{font-size:32px;line-height:38.4px}
.mod.premium .h3{font-size:20px;line-height:26px}
.mod.premium .body p{font-size:16px;line-height:22.4px;font-weight:300}
.mod.premium .kick{text-transform:none;letter-spacing:0;font-size:16px;font-weight:700;color:inherit}
.phone .mod.premium .h1{font-size:22px;line-height:26.4px}
.phone .mod.premium .h3{font-size:17px;line-height:22px}
.phone .mod.premium .body p{font-size:15px;line-height:21px}
.phone .mod.premium .kick{font-size:13px}
"""

JS = """
(function(){function c(i){var p=i.getAttribute('data-crop').split(',').map(Number),W=i.naturalWidth;
if(!W||!(p[2]>0)||!(p[3]>0))return;
/* A crop is in the uploaded file's pixels; Amazon's image host can serve a smaller copy. A crop that does
   not fit the served image is drawn as the whole image, covering the slot. */
if(p[0]+p[2]>W*1.01||p[1]+p[3]>i.naturalHeight*1.01){i.removeAttribute('data-crop');return;}i.style.width=(W/p[2]*100)+'%';i.style.left=(-p[0]/p[2]*100)+'%';
i.style.top=(-p[1]/p[3]*100)+'%';if(i.closest('.bs'))return;i.className+=' cropped';i.removeAttribute('data-crop');}
function run(){var a=document.querySelectorAll('img[data-crop]');for(var k=0;k<a.length;k++)c(a[k]);return a.length;}
document.addEventListener('load',function(e){if(e.target.tagName==='IMG'&&e.target.hasAttribute('data-crop'))c(e.target);},true);
var n=0,t=setInterval(function(){if(!run()||++n>100)clearInterval(t);},300);
var v={desktop:'v-d',mobile:'v-m',both:'v-b'}[location.hash.slice(1)];if(v)document.getElementById(v).checked=true;})();
"""


def render_page(doc, media):
    warnings = {}
    check_document(doc, lambda w: warnings.setdefault(w, None))
    mods = doc.get("contentModuleList")
    fams = {family(m.get("contentModuleType")) for m in mods if isinstance(m, dict) and m.get("contentModuleType") in MODULES}
    brand = doc.get("contentType") == "BrandStory" or fams == {"BRAND_STORY"}
    wide = brand or "PREMIUM" in fams
    panes = []
    for mobile in (False, True):
        ctx = Ctx(mobile, media, warnings)
        if brand:
            inner = render_brand_story(ctx, mods)
        else:
            inner = "".join(render_module(ctx, i, m) for i, m in enumerate(mods))
        if mobile:
            title, cls = "Mobile &middot; 375 px", "phone"
        elif wide:
            title, cls = "Desktop &middot; 1,464 px", "wide"
        else:
            title, cls = "Desktop &middot; 970 px", "std"
        # Amazon's own section heading above the content, as on the product page.
        heading = '<h2 class="pdp-h">%s</h2>' % ("From the brand" if brand else "Product description")
        panes.append('<section class="pane %s"><h2>%s</h2><div class="frame %s">%s%s</div></section>'
                     % ("m" if mobile else "d", title, cls, heading, inner))
    kind = "Brand Story" if brand else ("Premium A+" if "PREMIUM" in fams else "Basic A+")
    meta = "%s &middot; contentType %s &middot; locale %s &middot; %d module%s" % (
        kind, esc(doc.get("contentType")), esc(doc.get("locale")), len(mods), "" if len(mods) == 1 else "s")
    if warnings:
        checks = '<div class="checks"><h2>Checks (%d)</h2><ul>%s</ul></div>' % (
            len(warnings), "".join("<li>%s</li>" % esc(w) for w in warnings))
    else:
        checks = '<div class="checks ok"><h2>Checks</h2>No problems found by the checks this preview runs.</div>'
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>%s &middot; A+ preview</title>
<style>%s</style></head><body>
<input type="radio" name="v" id="v-d" class="vt" checked><input type="radio" name="v" id="v-m" class="vt">
<input type="radio" name="v" id="v-b" class="vt"><input type="checkbox" id="v-l" class="vt">
<header><h1>%s</h1><div class="meta">%s</div>
<nav><label for="v-d">Desktop</label><label for="v-m">Mobile</label><label for="v-b">Side by side</label>
<label for="v-l">Show module labels</label></nav></header>
%s<div class="note">Drawn with the sizes, fonts and spacing of Amazon's product page for review before you create or submit; Amazon's page decides the final look. Images are shown from their URLs.</div>
<main>%s</main><script>%s</script></body></html>
""" % (esc(doc.get("name") or "A+ document"), CSS, esc(doc.get("name") or "A+ document"), meta, checks,
       "".join(panes), JS)
    return page, list(warnings)


# ---------------------------------------------------------------- CLI

def unwrap(obj):
    for path in (("data", "contentRecord", "contentDocument"), ("contentRecord", "contentDocument"),
                 ("data", "contentDocument"), ("contentDocument",), ()):
        d = g(obj, *path) if path else obj
        if isinstance(d, dict) and isinstance(d.get("contentModuleList"), list):
            return d
    return None


def parse_media(pairs):
    out = {}
    for p in pairs or []:
        k, sep, v = p.partition("=")
        if not sep or not k.strip() or not safe_url(v):
            raise ValueError("--media-url expects ID=https://... (got %r)" % p)
        out[k.strip()] = v.strip()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="preview_aplus.py",
        description="Render an Amazon A+ content or Brand Story document (contentDocument JSON) as one "
                    "self-contained HTML page with a desktop and a mobile view, and list the checks it fails "
                    "against the module limits. The layout is approximate; nothing is sent to Amazon.",
        epilog="Input: a contentDocument {name, contentType, locale, contentModuleList}, or the envelope a document "
               "read returns ({\"contentDocument\": ...} or {\"data\": {\"contentDocument\": ...}}). Use - for stdin. "
               "Exit 0 when the HTML is written (checks never block it), 2 when the input cannot be read.")
    ap.add_argument("document", help="path to the document JSON, or - for stdin")
    ap.add_argument("-o", "--output", help="HTML file to write (default: <document>.preview.html beside the input)")
    ap.add_argument("--open", action="store_true", help="open the page in the default browser when written")
    ap.add_argument("--media-url", action="append", metavar="ID=URL",
                    help="map a video's videoMediaId or imageMediaId to a URL (an image or a video file); repeatable")
    a = ap.parse_args(argv)
    try:
        media = parse_media(a.media_url)
    except ValueError as e:
        ap.error(str(e))
    try:
        raw = sys.stdin.read() if a.document == "-" else open(a.document, encoding="utf-8").read()
        doc = unwrap(json.loads(raw))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        print("error: cannot read %s: %s" % (a.document, e), file=sys.stderr)
        return 2
    if doc is None:
        print("error: %s holds no contentDocument with a contentModuleList." % a.document, file=sys.stderr)
        return 2
    out = a.output or ("aplus-preview.html" if a.document == "-" else os.path.splitext(a.document)[0] + ".preview.html")
    page, warnings = render_page(doc, media)
    try:
        with open(out, "w", encoding="utf-8") as f:
            f.write(page)
    except OSError as e:
        print("error: cannot write %s: %s" % (out, e), file=sys.stderr)
        return 1
    for w in warnings:
        print("check: " + w, file=sys.stderr)
    print("wrote %s (%d check%s)" % (out, len(warnings), "" if len(warnings) == 1 else "s"))
    if a.open:
        webbrowser.open("file://" + os.path.abspath(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
