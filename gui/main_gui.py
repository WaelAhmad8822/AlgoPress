import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import json
import math
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lossless.rle import compress as rle_compress, decompress as rle_decompress
from lossless.huffman import (
    compress as huffman_compress,
    decompress as huffman_decompress,
    frequency_dict,
    build_tree,
)
from lossless.golomb import compress as golomb_compress, decompress as golomb_decompress
from lossless.lzw import compress as lzw_compress, decompress as lzw_decompress
from lossy.quantization import quantize_image, dequantize_image


ALGORITHMS = {
    "lossless": [
        ("rle", "RLE"),
        ("huffman", "Huffman"),
        ("golomb", "Golomb"),
        ("lzw", "LZW"),
    ],
    "lossy": [
        ("quantization", "Vector Quantization"),
    ],
}


def compression_percentage(original_size, compressed_size):
    if original_size == 0:
        return 0.0
    reduction = 1 - (compressed_size / original_size)
    return round(reduction * 100, 2)


def compression_ratio(original_size, compressed_size):
    if original_size == 0 or compressed_size == 0:
        return None
    return round(original_size / compressed_size, 2)


def show_result_window(title, output_path, percent=None, ratio=None, mse=None, decompress_fn=None):
    result_window = tk.Toplevel(root)
    result_window.title(title)
    result_window.geometry("440x240")

    info = f"Saved to:\n{output_path}"
    ttk.Label(result_window, text=info, wraplength=400, justify="left").pack(pady=8)

    if percent is not None:
        ttk.Label(result_window, text=f"Compression: {percent}%").pack(pady=2)
    if ratio is not None:
        ttk.Label(result_window, text=f"Ratio: {ratio}:1").pack(pady=2)
    if mse is not None:
        ttk.Label(result_window, text=f"MSE: {mse:.2f}").pack(pady=2)

    def open_file():
        try:
            os.startfile(output_path)
        except Exception as exc:
            messagebox.showerror("Error", f"Cannot open file: {exc}")

    def open_folder():
        try:
            os.startfile(os.path.dirname(output_path))
        except Exception as exc:
            messagebox.showerror("Error", f"Cannot open folder: {exc}")

    btn_frame = ttk.Frame(result_window)
    btn_frame.pack(pady=6)
    ttk.Button(btn_frame, text="Open File", width=16, command=open_file).grid(row=0, column=0, padx=4, pady=2)
    ttk.Button(btn_frame, text="Open Folder", width=16, command=open_folder).grid(row=0, column=1, padx=4, pady=2)

    if decompress_fn:
        ttk.Button(result_window, text="Decompress", width=16, command=decompress_fn).pack(pady=6)

    ttk.Button(result_window, text="Close", width=16, command=result_window.destroy).pack(pady=4)


def run_rle(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    compressed = rle_compress(data)
    output_path = os.path.join(os.path.dirname(path), "rle_output.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(compressed)
    original_size = len(data.encode('utf-8'))
    compressed_size = len(compressed.encode('utf-8'))
    percent = compression_percentage(original_size, compressed_size)
    ratio = compression_ratio(original_size, compressed_size)
    show_result_window("RLE Result", output_path, percent, ratio, decompress_fn=lambda: run_rle_decompress(output_path))
    return {"output": output_path, "percent": percent, "ratio": ratio}


def run_rle_decompress(path):
    with open(path, 'r', encoding='utf-8') as f:
        compressed = f.read()
    decompressed = rle_decompress(compressed)
    output_path = os.path.join(os.path.dirname(path), "rle_decompressed.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decompressed)
    messagebox.showinfo("Done", f"RLE decompression done.\nSaved: {output_path}")
    return {"output": output_path}


def run_huffman(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    compressed, root = huffman_compress(data)
    freq = dict(frequency_dict(data))
    output_path = os.path.join(os.path.dirname(path), "huffman_output.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"compressed": compressed, "freq": freq}, f)
    compressed_size = max(1, math.ceil(len(compressed) / 8))  # bits to bytes approximation, avoid zero
    original_size = len(data.encode('utf-8'))
    percent = compression_percentage(original_size, compressed_size)
    ratio = compression_ratio(original_size, compressed_size)
    show_result_window("Huffman Result", output_path, percent, ratio, decompress_fn=lambda: run_huffman_decompress(output_path))
    return {"output": output_path, "percent": percent, "ratio": ratio}


def run_huffman_decompress(path):
    with open(path, 'r', encoding='utf-8') as f:
        payload = json.load(f)
    compressed = payload.get("compressed", "")
    freq = payload.get("freq", {})
    root = build_tree(freq)
    decompressed = huffman_decompress(compressed, root)
    output_path = os.path.join(os.path.dirname(path), "huffman_decompressed.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decompressed)
    messagebox.showinfo("Done", f"Huffman decompression done.\nSaved: {output_path}")
    return {"output": output_path}


def run_golomb(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    compressed = golomb_compress(data)
    output_path = os.path.join(os.path.dirname(path), "golomb_output.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(compressed)
    original_size = len(data.encode('utf-8'))
    compressed_size = len(compressed.encode('utf-8'))
    percent = compression_percentage(original_size, compressed_size)
    ratio = compression_ratio(original_size, compressed_size)
    show_result_window("Golomb Result", output_path, percent, ratio, decompress_fn=lambda: run_golomb_decompress(output_path))
    return {"output": output_path, "percent": percent, "ratio": ratio}


def run_golomb_decompress(path):
    with open(path, 'r', encoding='utf-8') as f:
        compressed = f.read()
    decompressed = golomb_decompress(compressed)
    output_path = os.path.join(os.path.dirname(path), "golomb_decompressed.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decompressed)
    messagebox.showinfo("Done", f"Golomb decompression done.\nSaved: {output_path}")
    return {"output": output_path}


def run_lzw(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()
    except UnicodeDecodeError:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            data = f.read()
    if not data:
        messagebox.showwarning("Empty file", "Selected file is empty; nothing to compress.")
        return {"output": "n/a", "percent": None, "ratio": None}
    compressed = lzw_compress(data)
    output_path = os.path.join(os.path.dirname(path), "lzw_output.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"compressed": compressed}, f)
    compressed_size = max(1, len(compressed) * 4)  # rough bytes estimate, avoid zero
    original_size = len(data.encode('utf-8'))
    percent = compression_percentage(original_size, compressed_size)
    ratio = compression_ratio(original_size, compressed_size)
    show_result_window("LZW Result", output_path, percent, ratio, decompress_fn=lambda: run_lzw_decompress(output_path))
    return {"output": output_path, "percent": percent, "ratio": ratio}


def run_lzw_decompress(path):
    with open(path, 'r', encoding='utf-8') as f:
        payload = json.load(f)
    compressed = payload.get("compressed", [])
    if not isinstance(compressed, list):
        raise ValueError("Invalid LZW file: 'compressed' field must be a list")
    decompressed = lzw_decompress(compressed.copy())
    output_path = os.path.join(os.path.dirname(path), "lzw_decompressed.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decompressed)
    messagebox.showinfo("Done", f"LZW decompression done.\nSaved: {output_path}")
    return {"output": output_path}


def run_quantization(image_path):
    output_path = os.path.join(os.path.dirname(image_path), "compressed_image.npz")
    percent, mse = quantize_image(image_path, levels=16, save_path=output_path)
    original_size = os.path.getsize(image_path)
    compressed_size = os.path.getsize(output_path)
    ratio = compression_ratio(original_size, compressed_size)
    show_result_window("Quantization Result", output_path, percent, ratio, mse, decompress_fn=lambda: run_quantization_decompress(output_path))
    return {"output": output_path, "percent": percent, "ratio": ratio, "mse": mse}


def run_quantization_decompress(image_path):
    output_path = os.path.join(os.path.dirname(image_path), "decompressed_image.png")
    dequantize_image(image_path, save_path=output_path)
    messagebox.showinfo("Done", f"Image decompression done.\nSaved: {output_path}")
    return {"output": output_path}


def update_algorithms(mode):
    algo_menu['menu'].delete(0, 'end')
    for key, label in ALGORITHMS[mode]:
        algo_menu['menu'].add_command(label=label, command=tk._setit(algo_var, key))
    algo_var.set(ALGORITHMS[mode][0][0])


def browse_file(action="compress"):
    mode = mode_var.get()
    if mode == "lossless":
        filetypes = [("Text/JSON", "*.txt *.json"), ("All files", "*.*")]
    else:
        if action == "compress":
            filetypes = [("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        else:
            filetypes = [("Compressed files", "*.npz"), ("All files", "*.*")]
    selected = filedialog.askopenfilename(filetypes=filetypes)
    if selected:
        file_var.set(selected)
        status_var.set(f"Selected: {selected}")


def perform(action):
    path = file_var.get()
    if not path:
        messagebox.showwarning("Select file", "Please choose a file first.")
        return

    mode = mode_var.get()
    algo = algo_var.get()

    start = time.perf_counter()
    result = None

    try:
        if algo == "rle":
            result = run_rle(path) if action == "compress" else run_rle_decompress(path)
        elif algo == "huffman":
            result = run_huffman(path) if action == "compress" else run_huffman_decompress(path)
        elif algo == "golomb":
            result = run_golomb(path) if action == "compress" else run_golomb_decompress(path)
        elif algo == "lzw":
            result = run_lzw(path) if action == "compress" else run_lzw_decompress(path)
        elif algo == "quantization":
            result = run_quantization(path) if action == "compress" else run_quantization_decompress(path)
    except Exception as exc:
        messagebox.showerror("Error", f"Operation failed: {exc}")
        return

    elapsed = time.perf_counter() - start
    output_path = result.get("output") if result else "n/a"
    percent = result.get("percent")
    ratio = result.get("ratio")
    mse = result.get("mse")

    status_var.set(f"{algo.title()} {action} finished in {elapsed:.3f}s")
    percent_text = f"Compression: {percent}%" if percent is not None else "Compression: n/a"
    ratio_text = f"Ratio: {ratio}:1" if ratio is not None else "Ratio: n/a"
    mse_text = f"MSE: {mse:.2f}" if mse is not None else "MSE: n/a"
    stats_var.set(f"Mode: {mode.title()} | Algo: {algo.title()} | Time: {elapsed:.3f}s\nOutput: {output_path}\n{percent_text} | {ratio_text} | {mse_text}")


root = tk.Tk()
root.title("Data Compression Studio")
root.geometry("620x360")
root.minsize(600, 340)

style = ttk.Style()
style.theme_use("clam")

mode_var = tk.StringVar(value="lossless")
algo_var = tk.StringVar(value="rle")
file_var = tk.StringVar(value="")
status_var = tk.StringVar(value="Ready")
stats_var = tk.StringVar(value="Mode: Lossless | Algo: RLE | Time: --\nOutput: --\nCompression: --")

# Top header
header = ttk.Label(root, text="Data Compression Studio", font=("Segoe UI", 14, "bold"))
header.pack(pady=(12, 6))

# sub = ttk.Label(root, text="Choose mode, algorithm, file, then compress or decompress.", wraplength=560, justify="center")
# sub.pack(pady=(0, 10))

container = ttk.Frame(root, padding=10)
container.pack(fill="both", expand=True)

# Left pane: mode and algorithm
left = ttk.Frame(container)
left.pack(side="left", fill="y", padx=(0, 10))

ttk.Label(left, text="Mode").pack(anchor="w")
mode_frame = ttk.Frame(left)
mode_frame.pack(anchor="w", pady=4)
ttk.Radiobutton(mode_frame, text="Lossless", variable=mode_var, value="lossless", command=lambda: update_algorithms("lossless")).pack(side="left", padx=4)
ttk.Radiobutton(mode_frame, text="Lossy", variable=mode_var, value="lossy", command=lambda: update_algorithms("lossy")).pack(side="left", padx=4)

ttk.Label(left, text="Algorithm").pack(anchor="w", pady=(8, 0))
algo_menu = ttk.OptionMenu(left, algo_var, algo_var.get(), *[label for _, label in ALGORITHMS["lossless"]])
algo_menu.pack(fill="x", pady=4)

# Right pane: file + actions
right = ttk.Frame(container)
right.pack(side="left", fill="both", expand=True)

file_frame = ttk.Frame(right)
file_frame.pack(fill="x", pady=(0, 8))
ttk.Label(file_frame, text="Input / Compressed File").pack(anchor="w")
file_entry = ttk.Entry(file_frame, textvariable=file_var, width=60)
file_entry.pack(side="left", fill="x", expand=True, padx=(0, 6), pady=4)
ttk.Button(file_frame, text="Browse", width=10, command=lambda: browse_file("compress")).pack(side="left")

action_frame = ttk.Frame(right)
action_frame.pack(pady=6)
ttk.Button(action_frame, text="Compress", width=16, command=lambda: perform("compress")).grid(row=0, column=0, padx=6, pady=4)
ttk.Button(action_frame, text="Decompress", width=16, command=lambda: browse_file("decompress") or perform("decompress")).grid(row=0, column=1, padx=6, pady=4)

status_label = ttk.Label(right, textvariable=status_var, foreground="#0078d4")
status_label.pack(anchor="w", pady=(8, 2))

stats_box = ttk.Label(right, textvariable=stats_var, background="#f7f7f7", relief="groove", padding=8, justify="left")
stats_box.pack(fill="x", pady=(4, 0))

update_algorithms("lossless")

root.mainloop()
