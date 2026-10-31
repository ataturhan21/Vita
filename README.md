# Vita Toolbox

A Streamlit collection of small image, video, text, and download utilities.

## Included tools

| Tool | Current implementation |
| --- | --- |
| Image editor | Color and sharpness adjustments, rotation, resizing, flips, filters, and optional remove.bg integration |
| Video editor | Upload a video, adjust playback speed, preview the processed MP4, and download it |
| Spelling correction | TextBlob-based text correction |
| YouTube downloader | Download a supported YouTube watch or shorts URL to the machine running the app |

The current repository contains these 4 pages. It does not include a PDF conversion page or a voice-cloning implementation.

## Run locally

The original instructions use Python 3.10.10 and Poetry 1.4.0. The supported Python range and original dependencies are recorded in [`pyproject.toml`](pyproject.toml) and `poetry.lock`.

```bash
git clone https://github.com/ataturhan21/Vita.git
cd Vita
poetry install --no-root
poetry run streamlit run "vita/👋 Welcome.py"
```

Run from the repository root so `static/` images resolve. [`start.bat`](start.bat) handles the working directory on Windows.

The video page uses MoviePy and requires a working FFmpeg installation or the binary supplied through its environment. Uploaded videos are written to an isolated temporary directory for processing; temporary source, audio, and output files are removed after the result is read or processing fails.

## Optional background removal

Create `.streamlit/secrets.toml` using [`secrets.example.toml`](secrets.example.toml), then provide your `removebg_api_key`. This credential is used only when **Remove background** is selected in the image editor. The image is sent to the remove.bg service for that operation.

The existing `.gitignore` excludes `.streamlit/`; keep real credentials in that ignored directory.

## Project map

- [`vita/👋 Welcome.py`](vita/%F0%9F%91%8B%20Welcome.py): application entry point.
- [`vita/pages/`](vita/pages/): the 4 tool pages.
- [`vita/modules/utils.py`](vita/modules/utils.py): shared page configuration and styling.
- [`static/`](static/): background assets.

The YouTube integration depends on the external site's behavior and the original pytube implementation. Check it with your intended URL before relying on a download workflow. The dependency set is preserved, and compatibility with current package releases has not been established.

## License

[GNU General Public License v3.0](LICENSE).
