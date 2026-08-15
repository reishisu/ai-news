#!/usr/bin/env python3
"""検証用の最小 .wasm と、その圧縮版を作る。

Unity の Web ビルドは .wasm / .data / .js を Brotli か Gzip で
圧縮して出力する。ここでは中身の代わりに、
add(i32,i32)->i32 だけを持つ最小の wasm を使う。

gzip は Python 標準ライブラリ、brotli は Node の zlib を借りる
（Python 側に brotli が無いため）。
"""
import gzip
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent

# 手書きの最小 wasm モジュール
WASM = bytes([
    0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,  # magic + version
    0x01, 0x07, 0x01, 0x60, 0x02, 0x7f, 0x7f, 0x01, 0x7f,  # type
    0x03, 0x02, 0x01, 0x00,                                # function
    0x07, 0x07, 0x01, 0x03, 0x61, 0x64, 0x64, 0x00, 0x00,  # export "add"
    0x0a, 0x09, 0x01, 0x07, 0x00,
    0x20, 0x00, 0x20, 0x01, 0x6a, 0x0b,                    # code
])


def main():
    raw = HERE / "app.wasm"
    raw.write_bytes(WASM)

    gz = HERE / "app.wasm.gz"
    gz.write_bytes(gzip.compress(WASM, 9))

    br = HERE / "app.wasm.br"
    subprocess.run(
        ["node", "-e",
         "const z=require('zlib'),f=require('fs');"
         "f.writeFileSync(process.argv[2],"
         "z.brotliCompressSync(f.readFileSync(process.argv[1])))",
         str(raw), str(br)],
        check=True,
    )

    for p in (raw, gz, br):
        print(f"{p.name:<14}{len(p.read_bytes()):>5} bytes")


if __name__ == "__main__":
    main()
