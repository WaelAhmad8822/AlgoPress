# Data Compression Project

Interactive toolkit for experimenting with lossless and lossy compression algorithms through a desktop GUI built in Tkinter. Supports compress/decompress flows, compression percentage/ratio metrics, and a modern “Data Compression Studio” interface.

## Features
- Lossless: RLE, Huffman, Golomb, LZW (compress & decompress).
- Lossy: Vector Quantization over image blocks (compress to `.npz`, decompress to PNG).
- GUI: Select mode/algorithm, browse input, run compress/decompress, view results, open output file/folder.
- Metrics: Compression percentage and ratio, plus elapsed time per run.

## Prerequisites
- Python 3.11+ recommended (tested with 3.13).
- Pillow and NumPy for image handling and vector quantization.

Install deps:
```bash
python -m pip install pillow numpy
```

## Run the GUI
```bash
python gui/main_gui.py
```

## Using the App
1) Pick **Mode** (Lossless or Lossy) and an **Algorithm** from the dropdown.
2) Click **Browse** to select input:
   - Lossless compress: text file (`.txt`) or JSON for Huffman/LZW outputs.
   - Lossless decompress: choose the produced output file (`*_output.txt` or `huffman_output.json`, `lzw_output.json`).
   - Lossy compress: image (`.png/.jpg/.jpeg`).
   - Lossy decompress: the generated `.npz` file.
3) Click **Compress** or **Decompress**.
4) View metrics in the status panel and optional result window (open file/folder, quick decompress for compressed outputs).

## Outputs
- RLE: `rle_output.txt` / `rle_decompressed.txt`
- Huffman: `huffman_output.json` (stores compressed bits + frequency table) / `huffman_decompressed.txt`
- Golomb: `golomb_output.txt` / `golomb_decompressed.txt`
- LZW: `lzw_output.json` (stores code list) / `lzw_decompressed.txt`
- Vector Quantization: `compressed_image.npz` (codebook + assignments) / `decompressed_image.png`

## Notes
- Compression percentages/ratios are estimated from byte sizes (Huffman/LZW use approximations where needed).
- Vector quantization is block-based with a simple k-means; adjust in `lossy/quantization.py` (levels, block size) if desired.
- The GUI uses the `clam` ttk theme; adjust styling in `gui/main_gui.py` if needed.


