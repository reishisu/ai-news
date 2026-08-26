"""腕を組んだポーズの「囲まれた透明」を数える。dark_assist 修正の前後比較。

囲まれた透明 = 外周から届かない透明画素。腕と胴の間の影が食われると、
そこがキャラに囲まれた透明の帯になる。修正前の値は 2026/8/26 の実測
(コミット bb1bb74 時点の cast)。修正後は現在の cast を測る。
髪と肩の隙間のような**本物の背景**も含む数字なので、0にはならない。
差分だけを読むこと。

## 結果: **この指標は使えなかった**（記事には使っていない）

修正後に hinata/stop が +5460、shirase/smug が +9525 と**増えた**。
影が食われていた時は、透明の帯が外周まで繋がって「囲まれていない」扱いになり、
影が戻ると、腕と胴の間の**本物の背景**が正しく「囲まれた」に変わるため。
つまり修復すると数字が増える方向にも動く。前後比較には使えない。
dark_assist 修正の根拠は grow.py（消す画素数の段数別比較）と目視の側にある。
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
CAST = ROOT / "_assets/character/cast"
BEFORE = {"hinata/stop": 44854, "hinata/smug": 24506, "kotoha/angry": 2601,
          "aoi/angry": 2145, "shirase/smug": 4026, "kurumi/think": 1287}

print(f"{'対象':16}{'修正前':>10}{'修正後':>10}{'差':>10}")
for spec, before in BEFORE.items():
    who, pose = spec.split("/")
    a = np.asarray(Image.open(CAST / who / f"{pose}.png").convert("RGBA"))[:, :, 3]
    trans = a < 8
    lab, n = ndimage.label(trans, structure=np.ones((3, 3), int))
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    inner = int((trans & ~np.isin(lab, list(edge))).sum())
    print(f"{spec:16}{before:10}{inner:10}{inner - before:+10}")
