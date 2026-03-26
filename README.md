# Movie Collage Maker

**Movie Collage Maker (MCM)** is an efficient desktop solution for extracting movie frames and creating high-quality cinematic collages. Whether you are a film critic, a content creator, or a fan, MCM allows you to transform video files into beautiful, subtitle-annotated image grids with just a few clicks. Perfect for creating "film aesthetics" posts, educational materials, or movie discussions.

## Screenshot & result


*Movie: Charade (1963), public domain*

<img width="1072" height="943" alt="screenshot" src="https://github.com/user-attachments/assets/926f7f70-0d39-4368-937c-85f06490640d" />

---

![collage](https://github.com/user-attachments/assets/f6e69f75-7df8-47a1-ba3e-e0e1a84c42bb)

---

## 🎞️ Supported Formats
The application relies on the power of **FFmpeg**, which allows for broad compatibility:
* **Video:** Supports nearly any video container and codec (MKV, MP4, AVI, WEBM, MOV, etc.).
* **Subtitles:** Works with internal (embedded) and external text-based subtitles (SRT, ASS, SSA, VTT). 
* **Note:** Image-based subtitles (like DVD VobSub or Blu-ray PGS) are not supported for text extraction.

---

# 1. Installation

To run Movie Collage Maker, you need **Python 3.x**.

Install the required Python library using pip:

```bash
pip install PySide6
```

Two system dependencies are needed as well (they are common, so check first if you don't have them already!):
```bash
ffmpeg -version
magick identify --version
```
If tool(s) can't be found, install them:

## Windows
- **ImageMagick:** [https://imagemagick.org/script/download.php#windows](https://imagemagick.org/script/download.php#windows) (choose `-static` version, preferably `Q8` for speed; remember to choose "add to system path" in installer)
- **FFmpeg:** [https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip) (copy to directory from `PATH` environment variable)

### Linux
```bash
sudo apt install ffmpeg imagemagick
```

### MacOS
```bash
brew install ffmpeg imagemagick
```

---

# 2. How to Create a Collage (Step-by-Step)

The workflow is designed to follow the numbered panels in the application:

1. **Project management:** Start by clicking **Import movie** to load your video file (MKV, MP4, AVI). You can also open an existing `.mcm` project here. If you got subtitles in external file, just name them after the movie (for e.g. movie `foobar.mp4` will need subtitles saved as `foobar.srt`).
2. **Subtitle list:** Scroll through the extracted subtitles. Click a line to jump to that specific frame in the preview. Double click on the subtitle to add it *as it is* to the project. You can also click one time to be able to customize it.
3. **Current frame editor:** Fine-tune your selection using navigation buttons (e.g., `+1` or `-5` frames). You can manually edit the text in the box if you want to change what appears on the image (like adding hearing impaired text, like `[angry]`). Click **Add to project ↓** to save the clip.
4. **Project clips:** View your selected frames. Use the **Sort** button to arrange them chronologically or remove any unwanted clips.
5. **Project options:** Choose your layout (Horizontal/Vertical), set the tile count (you need to specify columns/rows, the rest is calculated automatically), and customize the font or border. Finally, hit **GENERATE FILE** to save your masterpiece. **Note:** The file extension you provide during saving (e.g., `.jpg`, `.png`, `.webp`) defines the output image format.

---

# 3. Projects and Files

### The `.mcm` Project File
When you save your work, the app creates a `.mcm` file. This file is a JSON-based container that includes:
* **Global settings:** Font family, size, border thickness, color, layout type, and tile count.
* **Extra parameters:** All custom ImageMagick flags defined in the options panel.
* **Frames and Subtitles:** A complete list of all selected clips. Each entry stores the exact frame number and the **customized text**, so your manual edits to the dialogue are preserved even if you reload the project later.

---

# 4. Extra ImageMagick Parameters

The **Extra ImageMagick parameters** field allows you to inject native `montage` commands directly into the generation process. This is useful for advanced users who want more control over the output.

**Common examples:**
* `-quality 90` – Sets the JPEG compression level (0-100).
* `-resize 50%` – Shrinks the final collage to half its size (great for web sharing).
* `-shadow` – Adds a drop shadow to each tile in the collage.
* `-blur 0x5` – Applies a blur effect to the images.

For a full list of available flags, visit the official documentation:
👉 [ImageMagick Montage Options](https://imagemagick.org/script/montage.php#options)

---

# 5. Tips & Tricks

- **Drag & Drop:** You don't need to browse folders. Simply drag your video file or `.mcm` project file and drop it anywhere into the app window.
- **Double-Click Action:** In the **Subtitle list** (Panel 2), double-clicking any line instantly adds that frame to your project, saving you time.
- **Filtering & Search:** Use the filter bar to find specific dialogue. Once you click a result, you can remove the filter text—the list will stay on your selected item, helping you see the surrounding context and find the exact moment you need.
- **Frame customization:** Sometimes the first frame of a subtitle may appear bad ("silly face" when a person is talking), so you can change it using the navigation buttons right below the frame.
- **Dirty Flag & Auto-Prompt:** The app tracks your changes. If you try to close the window or load a new movie without saving, MCM will ask if you want to save your current project first.
- **Result customization:** Use the **Font settings** and **Color** picker to match the collage style to the movie's atmosphere. It will apply globally to every frame. You can also add a border.

---

# ☕ Support My Work

Your support helps me maintain my Open Source projects, continue my volunteer work for NGOs, and produce more educational content.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/krzysiunet)

---
**License:** MIT  
**Author:** Krzysztof Blachnicki ([krzysiu.net](https://krzysiu.net))
