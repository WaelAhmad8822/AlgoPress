from PIL import Image
import numpy as np
import os


def _extract_blocks(pixels, block_size):
    """
    Supports grayscale (H, W) and RGB (H, W, 3). Returns (blocks, trimmed_shape, channels).
    """
    if pixels.ndim == 2:
        h, w = pixels.shape
        channels = 1
    else:
        h, w, channels = pixels.shape
    bh, bw = block_size
    h_trim = h - (h % bh)
    w_trim = w - (w % bw)
    cropped = pixels[:h_trim, :w_trim] if channels == 1 else pixels[:h_trim, :w_trim, :]
    if channels == 1:
        blocks = cropped.reshape(h_trim // bh, bh, w_trim // bw, bw)
        blocks = blocks.swapaxes(1, 2).reshape(-1, bh * bw)
    else:
        blocks = cropped.reshape(h_trim // bh, bh, w_trim // bw, bw, channels)
        blocks = blocks.swapaxes(1, 2).reshape(-1, bh * bw * channels)
    return blocks, (h_trim, w_trim), channels


def _reconstruct_image(codebook, assignments, trimmed_shape, block_size, original_shape, channels):
    bh, bw = block_size
    h_trim, w_trim = trimmed_shape
    if channels == 1:
        blocks = codebook[assignments].reshape(h_trim // bh, w_trim // bw, bh, bw)
        blocks = blocks.swapaxes(1, 2).reshape(h_trim, w_trim)
    else:
        blocks = codebook[assignments].reshape(h_trim // bh, w_trim // bw, bh, bw, channels)
        blocks = blocks.swapaxes(1, 2).reshape(h_trim, w_trim, channels)

    # pad back to original shape if cropped
    if len(original_shape) == 2:
        h, w = original_shape
        canvas = np.zeros((h, w), dtype=np.uint8)
        canvas[:h_trim, :w_trim] = blocks
    else:
        h, w, c = original_shape
        canvas = np.zeros((h, w, c), dtype=np.uint8)
        canvas[:h_trim, :w_trim, :] = blocks
    return canvas


def _kmeans(data, k, max_iter=20):
    # Simple k-means for small images; not optimized for very large inputs.
    rng = np.random.default_rng()
    # initialize centers by sampling without replacement
    if data.shape[0] < k:
        k = data.shape[0]
    idx = rng.choice(data.shape[0], size=k, replace=False)
    centers = data[idx].astype(np.float32)

    for _ in range(max_iter):
        # assign
        dists = np.linalg.norm(data[:, None, :] - centers[None, :, :], axis=2)
        assignments = np.argmin(dists, axis=1)
        # recompute
        new_centers = np.stack(
            [data[assignments == i].mean(axis=0) if np.any(assignments == i) else centers[i] for i in range(k)]
        )
        if np.allclose(new_centers, centers):
            break
        centers = new_centers
    return centers.astype(np.uint8), assignments


def quantize_image(image_path, levels=16, save_path="compressed_image.npz", block_size=(4, 4)):
    """
    Vector quantization using k-means over image blocks.
    Saves compressed codebook + assignments to an .npz file.
    Returns (compression_percentage, mse) vs original file.
    """
    if not save_path.endswith(".npz"):
        base, _ = os.path.splitext(save_path)
        save_path = base + ".npz"

    # Preserve color; convert paletted/alpha images to RGB
    pic = Image.open(image_path)
    if pic.mode not in ("RGB", "L"):
        pic = pic.convert("RGB")
    pixels = np.array(pic, dtype=np.uint8)

    blocks, trimmed_shape, channels = _extract_blocks(pixels, block_size)
    codebook, assignments = _kmeans(blocks, levels)

    np.savez_compressed(
        save_path,
        codebook=codebook,
        assignments=assignments,
        trimmed_shape=np.array(trimmed_shape),
        original_shape=np.array(pixels.shape),
        block_size=np.array(block_size),
        channels=np.array(channels),
        mode=np.array(pic.mode),
    )

    # compute estimated compression percentage using file sizes
    original_size = os.path.getsize(image_path)
    compressed_size = os.path.getsize(save_path)
    percent = 0.0 if original_size == 0 else round((1 - (compressed_size / original_size)) * 100, 2)

    # compute reconstruction MSE between original and quantized
    quantized_image = _reconstruct_image(codebook, assignments, trimmed_shape, block_size, pixels.shape, channels)
    mse = float(np.mean((pixels.astype(np.float32) - quantized_image.astype(np.float32)) ** 2))

    print(f"Vector-quantized image saved as {save_path} ({percent}% reduction), MSE={mse:.2f}")
    return percent, mse


def dequantize_image(compressed_path, save_path="decompressed_image.png"):
    data = np.load(compressed_path)
    codebook = data["codebook"]
    assignments = data["assignments"]
    # ensure shapes are plain Python ints
    trimmed_shape = tuple(int(x) for x in data["trimmed_shape"])
    original_shape = tuple(int(x) for x in data["original_shape"])
    block_size = tuple(int(x) for x in data["block_size"])
    channels = int(data.get("channels", 1))
    mode = str(data.get("mode", "RGB"))

    reconstructed = _reconstruct_image(codebook, assignments, trimmed_shape, block_size, original_shape, channels)
    image_out = Image.fromarray(reconstructed.astype(np.uint8))
    if channels == 1 and mode == "RGB":
        # fallback to L if data is single-channel
        image_out = image_out.convert("RGB")
    image_out.save(save_path)
    print(f"Decompressed image saved as {save_path}")


if __name__ == "__main__":
    quantize_image("sample_image.png", levels=16)
