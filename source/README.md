# Asset sources and verification

The symbol and logo lettering originate in `concepts/open-markets-identity.png`. `identity-paths.json` records their vector contours and source regions. Every full-size logo variant reuses these paths; the small website icon is a subset of the same symbol contours. The logo SVG files contain only vector shapes, with no embedded raster logos or font dependency.

`build-manifest.json` records the palette and application list. `validation.json` records checks for dimensions, transparency, consistent geometry across color variants, vector PDFs, editable text, local links, font licenses and complete video decoding.

## Deliverables

- 12 SVG logos: four arrangements in ink, black and white.
- 24 transparent logo PNGs: each SVG exported at 512 and 2048 pixels wide.
- 12 vector logo PDFs.
- Seven editable SVG templates and their self-contained artwork exports.
- Three watercolor backgrounds reconstructed from the approved board.
- Three-page PDF brand guide.
- Merriweather and Manrope fonts with SIL Open Font License files and a font ZIP.
- Five-column color chart in PNG and self-contained SVG, plus color values in CSS, SCSS, JSON and plain text.
- A six-second, silent 1080p MP4 intro.
- Website icon SVG and PNG sizes, press information and media references.

The artwork and PDFs were visually reviewed locally. No browser automation or live website deployment is part of this asset build.
