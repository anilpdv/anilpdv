# Profile artwork

The README uses self-contained SVG panels with mobile variants. Text and diagrams are editable in `scripts/render_profile.py`; linked cards and social buttons are ordinary Markdown/HTML links around images.

- `night-vista.jpg`: original background illustration generated using the built-in image-generation tool. Typography and profile facts are added in SVG, not generated in the illustration.
- `icons/*.svg`: Simple Icons v15, CC0, obtained from https://github.com/simple-icons/simple-icons. Brand logos identify their respective tools.
- `metrics*.svg`, `dashboard*.svg`, `data.json`: generated from GitHub's API. Stars cover public non-fork repositories; contributions cover the past year. Counts are never fabricated.
- Other SVGs: original vector artwork and layout authored for this profile.

## Refresh

The `Refresh profile SVGs` GitHub Actions workflow runs daily or on manual dispatch. It uses the repository's standard `GITHUB_TOKEN`; no personal access token or third-party stats-image service is required. The workflow only commits generated assets.

For local work, run `python3 scripts/render_profile.py --data response.json` with a complete paginated response in the same GraphQL shape as the script's query. Without `--data`, the script reads `GITHUB_TOKEN` or `GH_TOKEN` from the environment and fetches public data itself.

Artwork prompt: Original panoramic anime-inspired midnight illustration for a GitHub profile; an anonymous hooded developer seen from behind on a rocky overlook in the right third, distant coastal city and layered indigo mountains, a pink-violet moon and restrained cyan stars, left half dark and empty for SVG typography. No text, logos, interface panels, or watermark. The user-supplied Designer.png was a mood and composition reference.
