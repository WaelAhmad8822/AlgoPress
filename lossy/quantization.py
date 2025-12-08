from PIL import Image
import numpy as np
import os


def _extract_blocks(pixels, block_size):
    h, w = pixels.shape
    bh, bw = block_size
    h_trim = h - (h % bh)
    w_trim = w - (w % bw)
    cropped = pixels[:h_trim, :w_trim]
    blocks = cropped.reshape(h_trim // bh, bh, w_trim // bw, bw)
    blocks = blocks.swapaxes(1, 2).reshape(-1, bh * bw)
    return blocks, (h_trim, w_trim)


def _reconstruct_image(codebook, assignments, trimmed_shape, block_size, original_shape):
    bh, bw = block_size
    h_trim, w_trim = trimmed_shape
    blocks = codebook[assignments].reshape(h_trim // bh, w_trim // bw, bh, bw)
    blocks = blocks.swapaxes(1, 2).reshape(h_trim, w_trim)

    # pad back to original shape if cropped
    h, w = original_shape
    canvas = np.zeros((h, w), dtype=np.uint8)
    canvas[:h_trim, :w_trim] = blocks
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
    Returns compression percentage estimate vs original file size.
    """
    if not save_path.endswith(".npz"):
        base, _ = os.path.splitext(save_path)
        save_path = base + ".npz"

    pic = Image.open(image_path).convert('L')
    pixels = np.array(pic, dtype=np.uint8)

    blocks, trimmed_shape = _extract_blocks(pixels, block_size)
    codebook, assignments = _kmeans(blocks, levels)

    np.savez_compressed(
        save_path,
        codebook=codebook,
        assignments=assignments,
        trimmed_shape=np.array(trimmed_shape),
        original_shape=np.array(pixels.shape),
        block_size=np.array(block_size),
    )

    # compute an estimated compression percentage using file sizes
    original_size = os.path.getsize(image_path)
    compressed_size = os.path.getsize(save_path)
    percent = 0.0 if original_size == 0 else round((1 - (compressed_size / original_size)) * 100, 2)

    print(f"Vector-quantized image saved as {save_path} ({percent}% reduction)")
    return percent


def dequantize_image(compressed_path, save_path="decompressed_image.png"):
    data = np.load(compressed_path)
    codebook = data["codebook"]
    assignments = data["assignments"]
    trimmed_shape = tuple(data["trimmed_shape"])
    original_shape = tuple(data["original_shape"])
    block_size = tuple(data["block_size"])

    reconstructed = _reconstruct_image(codebook, assignments, trimmed_shape, block_size, original_shape)
    Image.fromarray(reconstructed.astype(np.uint8)).save(save_path)
    print(f"Decompressed image saved as {save_path}")


if __name__ == "__main__":
    quantize_image("sample_image.png", levels=16)
