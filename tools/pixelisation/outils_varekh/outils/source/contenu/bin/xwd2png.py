"""Convertit une image XWD (sortie de xwd) en PNG, sans dependance (zlib seulement)."""
import struct, sys, zlib

def lire_xwd(data):
    h = struct.unpack(">25I", data[:100])
    header_size, _, fmt, depth, w, hgt = h[0], h[1], h[2], h[3], h[4], h[5]
    byte_order, bpp, bpl, ncolors = h[7], h[11], h[12], h[19]
    rmask, gmask, bmask = h[13], h[14], h[15]
    off = header_size + ncolors * 12
    px = data[off:off + bpl * hgt]
    if bpp not in (24, 32):
        raise SystemExit(f"xwd2png : {bpp} bits/pixel non gere (24 ou 32 attendu)")
    n = bpp // 8
    rows = []
    for y in range(hgt):
        row = px[y * bpl:y * bpl + w * n]
        b = bytearray(w * 3)
        if byte_order == 0:   # LSBFirst : B G R (X)
            b[0::3] = row[2::n]; b[1::3] = row[1::n]; b[2::3] = row[0::n]
        else:                 # MSBFirst : (X) R G B
            o = n - 3
            b[0::3] = row[o::n]; b[1::3] = row[o + 1::n]; b[2::3] = row[o + 2::n]
        rows.append(b"\x00" + bytes(b))
    return w, hgt, b"".join(rows)

def png(w, h, raw):
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))

if __name__ == "__main__":
    src = open(sys.argv[1], "rb").read() if sys.argv[1] != "-" else sys.stdin.buffer.read()
    w, h, raw = lire_xwd(src)
    open(sys.argv[2], "wb").write(png(w, h, raw))
    print(f"{sys.argv[2]} : {w}x{h}")
