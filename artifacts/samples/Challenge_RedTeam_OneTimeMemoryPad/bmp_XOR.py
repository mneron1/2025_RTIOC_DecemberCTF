from pathlib import Path

b1 = Path("picture1.bmp").read_bytes()
b2 = Path("picture2.bmp").read_bytes()

# BMP pixel array offset is at bytes 10..13 (little-endian)
off = int.from_bytes(b1[10:14], "little")

# Keep header from picture1, XOR the pixel data
out = b1[:off] + bytes(a ^ b for a, b in zip(b1[off:], b2[off:]))

Path("recovered.bmp").write_bytes(out)
print("Wrote recovered.bmp - open it to read the flag.")
