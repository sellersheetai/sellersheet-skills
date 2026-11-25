# Preview a document before you create or submit it

`scripts/preview_aplus.py` draws a document as one local HTML page, with a desktop and a mobile
view, so the user can see roughly how it will look before anything goes to Amazon. Python 3.9 or
later, standard library only; nothing is sent anywhere except the browser's requests for the
images themselves.

```bash
python3 scripts/preview_aplus.py document.json            # writes document.preview.html
python3 scripts/preview_aplus.py document.json -o page.html --open
python3 scripts/preview_aplus.py document.json --media-url <videoMediaId>=https://…/clip.mp4 \
                                               --media-url <imageMediaId>=https://…/poster.jpg
```

- **Input:** a `contentDocument` (`name`, `contentType`, `locale`, `contentModuleList`), or the
  answer of `aplusContent_getContentDocument` as it came back (`{"contentDocument": …}` or
  `{"data": {"contentDocument": …}}`), so a live document can be previewed too. `-` reads stdin.
- **Views:** Basic at 970 px; Premium and Brand Story at 1,464 px shown at 66%; mobile at 375 px.
  Desktop slots show `desktopImage`, mobile shows `mobileImage`. Append `#mobile` or `#both` to
  the page address to open on that view.
- **Images:** a URL is shown as it is; an Amazon id (`aplus-media/sc/….png`) is shown from
  Amazon's image host; anything else is a grey box with the slot and its minimum size.
  `imageCropSpecification` is honoured.
- **Video:** a dark frame with the two media ids, unless `--media-url` maps an id to a URL.
- **Brand Story:** the "From the Brand" carousel, `BRAND_STORY_IMAGE_WITH_LOGO` as the
  background and first card. The brand logo on that card comes from the brand, not the
  document, so it is drawn as a box.
- **Checks** (listed on the page and printed to stderr, never blocking): unknown module type,
  missing or mismatched module key, mixed families, more than 7 Premium modules, a Brand Story
  without exactly one `BRAND_STORY_IMAGE_WITH_LOGO` as its first module or with fewer than 3
  modules, text over the limits in `schema/`, item counts and duplicate positions outside the
  schema, an image slot left empty, alt text over 100 characters. A clean page is not Amazon's validation: still run the dry run.
- Hotspot markers are placed on a 1,464 × 600 frame (the crop's size when one is given).
- Exit 0 when the page is written, 2 when the input cannot be read.
