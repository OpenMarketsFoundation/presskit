# Asset sources and verification

`identity-paths.json` is the canonical corrected vector master. Every full-size logo and application reuses these paths. Stacked and horizontal lockups align the badge to the full text block, including FOUNDATION. Logo SVGs contain vector paths without embedded images or font dependencies.

`homepage-artwork.json` records the original homepage file, source revision and SHA-256 checksum. `illustrations/lemonade-children-day-transparent.webp` is a byte-for-byte copy. The PNG encoding has identical decoded RGBA pixels for SVG/PDF renderer compatibility. Neither version is retouched, cropped, recolored or regenerated. The rejected replacement scenes and outdated concept board are removed from current downloads.

`build.py` generates the shared layouts from these sources. `render.cjs` exports PNGs using Sharp. `finish.py` exports vector PDFs, the guide and video using svglib, ReportLab and imageio-ffmpeg. These are offline authoring tools; they do not alter the original artwork. Install their dependencies in an isolated authoring environment, not the website runtime. Run the scripts from any directory in that order. `validate.py` checks the packaged files; `check-consistency.py` verifies original pixels and lockup bounds.

## Deliverables

- Twelve SVG logos, twenty-four transparent PNGs and twelve vector PDFs.
- Seven SVG templates and self-contained exports; the square hero wrapper has no text.
- Original square homepage artwork and the existing podcast watercolor background.
- Three-page PDF brand guide, local font files with SIL licenses and font ZIP.
- Five-column palette chart and color values in CSS, SCSS, JSON and plain text.
- Six-second silent 1080p MP4 intro, website icons and press information.

See [quality review](quality-review.md), [validation](validation.json) and [consistency checks](consistency.json).
