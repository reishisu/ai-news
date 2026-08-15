#!/usr/bin/env python3
"""`aws s3 cp` が Unity Web のビルドに何を付けるかを、
AWS CLI 自身の関数を呼んで確かめる。

S3 へは一切アップロードしない(認証情報が無い)。
CLI がリクエストに載せる値を、ローカルで組み立てて見るだけ。

awscli/customizations/s3/utils.py:
  guess_content_type() … mimetypes.guess_type(name)[0] を返す
  _set_general_object_params() … ContentEncoding は
  --content-encoding を渡したときだけ載る
"""
import mimetypes
import sys

sys.path.insert(0, "/usr/local/lib/python3.11/dist-packages")
from awscli.customizations.s3.utils import guess_content_type  # noqa: E402

FILES = [
    "app.loader.js",
    "app.framework.js.br",
    "app.wasm",
    "app.wasm.br",
    "app.data.br",
    "app.wasm.gz",
]


def main():
    print("■ aws s3 cp が載せる値(推定)")
    for name in FILES:
        ctype = guess_content_type(name)
        enc = mimetypes.guess_type(name)[1]
        print(name)
        print("  type " + (ctype or "(付かない→S3既定)"))
        print("  enc  (付かない)")
        print("  ※mimetypesの符号化推測: " + (enc or "なし"))
    print()
    print("--content-encoding br を付けた場合")
    print("  enc  br")


if __name__ == "__main__":
    main()
