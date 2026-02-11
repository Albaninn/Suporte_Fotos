# 📸 PhotoFlow Pro

> **Batch ingestion, organization, and processing suite for photographers.**
> Unifies multiple cameras, detects blurry photos via Computer Vision, and applies smart branding.

[![pt-br](https://img.shields.io/badge/lang-pt--br-green.svg)](README.pt-br.md)

![Badge Python](https://img.shields.io/static/v1?label=PYTHON&message=3.10+&color=blue&style=for-the-badge)
![Badge CV](https://img.shields.io/static/v1?label=OPENCV&message=COMPUTER%20VISION&color=green&style=for-the-badge)
![Badge Status](https://img.shields.io/static/v1?label=STATUS&message=V1.0%20STABLE&color=success&style=for-the-badge)

## 📌 The Problem
In professional photography workflows (sports events, weddings), three pain points are constant:
1.  **Desynchronization:** Photos from multiple bodies (Nikon, Canon) get out of order when renamed.
2.  **Slow Culling:** Finding blurry/shaken photos in a batch of 2,000 images takes hours.
3.  **Manual Export:** Opening Lightroom just to apply a simple watermark and resize for client delivery.

## 🚀 The Solution
**PhotoFlow Pro** is a Desktop application that automates ingestion. It reads raw EXIF metadata for perfect chronological sorting, uses mathematical algorithms to detect sharpness, and applies branding (logos) respecting photo orientation.

### Key Features

#### 1. 🧠 Smart Organization (Recursive Backend)
* **Deep Scan:** Automatically detects photos in subfolders of memory cards.
* **Real Chronology:** Sorts files based on the `DateTimeOriginal` EXIF tag, ignoring arbitrary filenames (`DSC_001`, `IMG_999`).

#### 2. 👁️ Blur Detection (Computer Vision)
* Uses **OpenCV** and the **Laplacian** operator to calculate edge variance in images.
* Generates an automatic report pointing out which files fall below the user-defined sharpness threshold.

#### 3. 💧 Smart Watermark (Dynamic Branding)
* **Proportional Logic:** The logo always occupies X% of the image width, regardless of whether the photo is **Portrait (Vertical)** or **Landscape (Horizontal)**.
* **Opacity Control:** 0-100% slider for subtle watermarking.
* **Rotation Correction:** Applies EXIF orientation before processing to ensure the logo stays in the correct corner.

#### 4. 🛡️ Metadata & Persistence
* **IPTC Injection:** Writes *Copyright* and *Artist Name* directly into the final file metadata.
* **Saved Settings:** The app remembers your preferences (folders, sensitivity, texts) in a local JSON file.

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **GUI:** CustomTkinter (Modern UI / Dark Mode)
* **Image Processing:** Pillow (PIL) + ImageOps
* **Computer Vision:** OpenCV (`cv2`)
* **Metadata:** PieExif
* **Build:** Auto-Py-To-Exe (PyInstaller)

## ⚙️ Installation and Execution

### Running from source
1.  Clone the repository:
    ```bash
    git clone [https://github.com/Albaninn/Suporte_Fotos.git](https://github.com/Albaninn/Suporte_Fotos.git)
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run:
    ```bash
    python src/main.py
    ```

### Generating the Executable (.exe)
This project is configured to be compiled into a single portable file.
1.  Install the builder: `pip install auto-py-to-exe`
2.  Run `auto-py-to-exe` and select the script `src/main.py`.
3.  Make sure to include the `camera.ico` icon as an additional resource.

### Executable Path (.exe)
`Suporte_Fotos\output\PhotoFlow.exe`

## 📂 Project Structure

```text
PhotoFlow_Pro/
├── output/
│   ├── PhotoFlow.exe 
├── src/
│   ├── backend.py       # Logic (OpenCV, Pillow, EXIF Sorting)
│   ├── interface.py     # GUI (CustomTkinter, Tabs, Events)
│   └── main.py          # Entry Point
├── camera.ico           # App Icon
├── user_config.json     # (Auto-generated)
├── requirements.txt     # Dependencies
└── README.md            # Documentation (English)


## 🤝 Contribution

Suggestions and pull requests are welcome. This project was developed to solve real-world pain points in sports and social photography workflows.

Developed by Luckas Serenato