
from heapq import heappush, heappop, heapify
from collections import defaultdict

class Node:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def frequency_dict(data):
    freq = defaultdict(int)
    for char in data:
        freq[char] += 1
    return freq

def build_tree(freq_dict):
    heap = [Node(char, freq) for char, freq in freq_dict.items()]
    heapify(heap)
    
    while len(heap) > 1:
        node1 = heappop(heap)
        node2 = heappop(heap)
        merged = Node(freq=node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heappush(heap, merged)
    return heap[0]  

def generate_codes(node, prefix="", code_dict={}):
    if node is None:
        return
    if node.char is not None:
        code_dict[node.char] = prefix
    generate_codes(node.left, prefix + "0", code_dict)
    generate_codes(node.right, prefix + "1", code_dict)
    return code_dict


def compress(data):
    freq = frequency_dict(data)
    root = build_tree(freq)
    codes = generate_codes(root)
    compressed = ''.join(codes[char] for char in data)
    return compressed, root  


def decompress(compressed, root):
    decompressed = ""
    node = root
    for bit in compressed:
        node = node.left if bit == '0' else node.right
        if node.char is not None:
            decompressed += node.char
            node = root
    return decompressed

if __name__ == "__main__":
    sample = "AAAABBBCCDAA"
    compressed, root = compress(sample)
    print("Compressed:", compressed)
    print("Decompressed:", decompress(compressed, root))
