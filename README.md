# 🧾 MCD OCR - Automated McDonald's Receipt Parser & Data Extractor

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-2.10.0-red.svg)](https://github.com/PaddlePaddle/PaddleOCR)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Extraction-150458.svg)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An industrial-grade, parallelized Python application designed to automatically process receipt images (specifically McDonald's receipt format), extract 12-character survey codes (`XXXX-XXXX-XXXX`), total prices, and distinguish transaction types (*In Total* vs. *Out Total*). Powered by **PaddleOCR**, regex pattern matching engines, and **ProcessPoolExecutor** multiprocessing, the tool exports structured receipt data into clean Excel spreadsheets (`.xlsx`).

---

## 🎥 Video Demo

*(Upload your video demo here)*

---

## ✨ Key Features

- ⚡ **High-Performance Parallel Processing**: Utilizes `concurrent.futures.ProcessPoolExecutor` with dynamic multi-core worker control managed via `Threads.txt`.
- 🤖 **AI-Driven Text Recognition**: Powered by **PaddleOCR** with angle classification (`use_angle_cls=True`) enabled to accurately detect and recognize text on skewed or upside-down receipt scans.
- 🎯 **Advanced 12-Digit Code Extraction**: Employs robust regex algorithms to detect, clean, and extract 12-character survey codes (`XXXX-XXXX-XXXX`), splitting them automatically into three distinct parts (`Part 1`, `Part 2`, `Part 3`) for downstream processing.
- 💵 **Price & Transaction Type Classification**:
  - Automatically identifies total transaction amounts while intelligent rules exclude `Subtotal` lines.
  - Classifies order types based on receipt keywords (*Eat-In* as `In Total`, *Takeaway/Drive-Thru* as `Out Total`, or `Unknown`).
  - Supports multiple numerical formats including missing decimals (`25` -> `25.00`) and colon-formatted amounts (`12:50` -> `12.50`).
- 📊 **Automated Excel Reporting**: Generates clean `.xlsx` reports (`ocr_results.xlsx`) sorted using natural numerical order (`1.jpg`, `2.jpg`, `10.jpg`).
- 🛡️ **File Lock Protection**: Automatically falls back to `ocr_results_latest.xlsx` if the main Excel file is locked or open in another application.
- 🖼️ **Multi-Format & Auto-Renaming Pipeline**: Accepts `.jpg`, `.jpeg`, `.png`, `.bmp`, and `.webp` images while auto-indexing image files sequentially for clean batch processing.

---

## 🛠️ Technologies & Architecture

| Layer / Component | Technology Stack | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.8+ | Primary backend programming environment |
| **OCR Engine** | [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | Deep-learning powered text detection and recognition with angle classification |
| **Parallel Execution** | `concurrent.futures.ProcessPoolExecutor` | Multi-core parallel batch processing of image files |
| **Regex & Extraction** | Python `re` Module | Custom pattern matching for survey codes, total amounts, and transaction types |
| **Data Processing & Export** | Pandas, OpenPyXL | Data aggregation, natural sorting, and structured `.xlsx` spreadsheet writing |
| **Image Processing** | OpenCV, Pillow, Scikit-Image | Image handling, format validation, and pre-processing pipeline |

### System Architecture Flow

```
┌───────────────────────────┐
│     Enhanced/ Folder      │  <-- Receipt Images (.jpg, .png, etc.)
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│  Image Auto-Renaming &    │  <-- Standardizes file indexing (1.jpg, 2.jpg...)
│    Natural Sort Filter    │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│   ProcessPoolExecutor     │  <-- Dynamically managed by Threads.txt
└─────────────┬─────────────┘
              │
      ┌───────┴───────┐ (Parallel Workers)
      ▼               ▼
┌───────────┐   ┌───────────┐
│ PaddleOCR │   │ PaddleOCR │  <-- Text Detection & Recognition (use_angle_cls)
└─────┬─────┘   └─────┬─────┘
      │               │
      └───────┬───────┘
              ▼
┌───────────────────────────┐
│ Regex Parsing Engine      │  <-- Extracts Code (Part 1, 2, 3), Price, and Order Type
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│  Pandas DataFrame &       │  <-- Saves structured data to ocr_results.xlsx
│   Excel Export Engine     │      (with lock fallback to ocr_results_latest.xlsx)
└───────────────────────────┘
```

---

## 📂 Project Structure

```
MCD_OCR/
├── 📁 Enhanced/               # Directory containing input receipt image files
│   ├── 1.jpg                 # Sample receipt image 1
│   ├── 2.jpg                 # Sample receipt image 2
│   └── ...                   # Additional receipt scans (.jpg, .png, .webp, etc.)
├── 📄 Modified.py             # Main entry point: Batch OCR runner, regex parser, & Excel exporter
├── 📄 Checking_Pattern.py     # Regex pattern validator & test script for 12-digit code formats
├── 📄 Threads.txt             # Configuration file defining worker thread count (e.g., 6)
├── 📄 ocr_results.xlsx        # Output Excel file containing parsed receipt metadata
├── 📄 requirements.txt        # Full list of Python package dependencies
└── 📄 README.md               # Project documentation
```

---

## 📋 Prerequisites

Before setting up and running the project, ensure you have the following installed on your system:

- **Python 3.8+** (Python 3.10 or 3.11 recommended)
- **pip** (Python package installer)
- **C++ Build Tools** (Required on Windows for compiling native dependencies like `pyclipper` or `Cython` if pre-built wheels aren't present)
- *(Optional)* **NVIDIA GPU with CUDA & cuDNN** for accelerated PaddleOCR processing.

---

## ⚙️ Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/rehanahmd218/mcd-receipt-parser.git
   cd mcd-receipt-parser
   ```

2. **Create a Virtual Environment**
   - **Windows:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux/macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 🚀 How to Use

### Step 1: Place Receipt Images
Add your target receipt image files into the `Enhanced/` directory. Supported file extensions include `.jpg`, `.jpeg`, `.png`, `.bmp`, and `.webp`.

### Step 2: Configure Worker Threads
Specify the maximum number of parallel processes in `Threads.txt` (default is `6`).
```text
6
```

### Step 3: Run the Parser
Execute the main script:
```bash
python Modified.py
```

**What happens when executed:**
1. The script automatically standardizes file names in `Enhanced/` sequentially (e.g., `1.jpg`, `2.jpg`).
2. Multi-threaded processing starts using the thread count in `Threads.txt`.
3. Terminal progress logs output status for each receipt image processed.
4. Parsing results are collected, naturally sorted, and written to `ocr_results.xlsx`.

---

## 🧪 Testing & Validation

To test and validate regular expression patterns for receipt codes against sample strings, run:

```bash
python Checking_Pattern.py
```

This utility tests strict (`XXXX-XXXX-XXXX`) and relaxed spacing patterns against edge cases (such as spaces between digits or hyphens).

---

## ⚙️ Configuration Notes

- **`Threads.txt`**: Adjust worker thread count depending on system CPU resources. Higher numbers speed up processing but require more CPU cores/RAM.
- **`ocr_results.xlsx`**: If this file is currently open in Excel when running the pipeline, the system safely writes to `ocr_results_latest.xlsx` to avoid data loss.

---

## 🔒 Privacy & Security Notes

- **Local Execution**: All OCR recognition and text extraction run **entirely locally** on your machine. No receipt images or extracted data are uploaded to external APIs or third-party cloud servers.
- **Data Protection**: Ensure any sensitive customer information on scanned receipts is handled according to local data privacy laws (e.g., GDPR).

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](../../issues).

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## ⚠️ Disclaimer

This project is an independent open-source utility developed for educational, research, and data processing purposes. It is **not affiliated with, endorsed by, sponsored by, or officially associated with McDonald's Corporation** or any of its subsidiaries or affiliates. All product names, logos, trademarks, and registered trademarks belong to their respective owners. Users are solely responsible for ensuring their use of this software complies with applicable laws, regulations, and third-party terms of service.

