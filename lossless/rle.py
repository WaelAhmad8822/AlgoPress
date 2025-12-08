def compress(data):
    if not data:
        return ""
    
    result = ""
    count = 1
    
    for i in range(1, len(data)):
        if data[i] == data[i - 1]:
            count += 1
        else:
            result += str(count) + data[i - 1]
            count = 1
    result += str(count) + data[-1]
    return result


def decompress(data):
    if not data:
        return ""
    
    result = ""
    count = ""
    
    for char in data:
        if char.isdigit():
            count += char
        else:
            result += char * int(count)
            count = ""
    return result


if __name__ == "__main__":
    sample = "AAAABBDAA"
    compressed = compress(sample)
    print("Compressed:", compressed)
    print("Decompressed:", decompress(compressed))
