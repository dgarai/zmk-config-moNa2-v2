#!/usr/bin/env python3
"""moNa2-v2 のキーマップを他のキーボードのリポジトリ向けに変換する。

マスター（このリポジトリの config/mona2.keymap）を唯一の真実とし、
以下の 2 つのリポジトリ向けの keymap を生成する。

  paw3222 : dgarai/zmk-for-moNa2-paw3222
            同じ moNa2 シールド（42キー）。センサーだけが違うので丸ごとコピーする。

  roBa    : dgarai/zmk-config-roBa
            43キー。2段目の左内側に moNa2 には無いキーが 1 個ある。
            そのため各レイヤーの 2段目に 1 個補い、コンボの key-positions を
            15 以降 +1 ずらす。デバイス固有のヘッダ（#include や &trackball）は
            変換先の既存ファイルのものを温存する。

使い方:
    python3 tools/sync-keymap.py --variant paw3222 --out ../paw3222/config/mona2.keymap
    python3 tools/sync-keymap.py --variant roBa    --out ../roBa/config/roBa.keymap
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

# roBa の 2段目左内側キー（グローバル位置 15）に入れる binding。
# レイヤー名で指定が無いものは ROBA_EXTRA_DEFAULT を使う。
ROBA_EXTRA_DEFAULT = "&trans"
ROBA_EXTRA_PER_LAYER = {
    "default_layer": "&kp LS(LG(S))",          # macOS スクリーンショット
    "NUM": "&kp LC(LA(KP_NUMBER_0))",
}

# roBa で 2段目に 1 個増える位置（0-origin のグローバルキー位置）。
ROBA_EXTRA_POSITION = 15
# 2段目の行の中での挿入インデックス（1段目が 10 キーなので 15 - 10）。
ROBA_EXTRA_ROW = 1
ROBA_EXTRA_INDEX = ROBA_EXTRA_POSITION - 10
# 変換後に各レイヤーが持つべきキー数。ずれていたら同期を失敗させる。
ROBA_KEY_COUNT = 43

ROOT_LINE = "/ {"


def split_header_body(text: str) -> tuple[str, str]:
    """`/ {` より前（デバイス固有ヘッダ）と、それ以降（共有する本体）に分ける。"""
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.rstrip("\n") == ROOT_LINE:
            return "".join(lines[:i]), "".join(lines[i:])
    raise SystemExit(f"'{ROOT_LINE}' が見つかりません")


BINDING_RE = re.compile(r"(?:(?<=\s)|^)&")


def binding_offsets(line: str) -> list[int]:
    """binding の行の中で、各 binding が始まる文字位置を返す。"""
    return [m.start() for m in BINDING_RE.finditer(line)]


def transform_layers(
    body: str, extra_for: dict[str, str], expected_keys: int
) -> str:
    """各レイヤーの 2段目に 1 キー補う。

    行を組み直すと整列が崩れて差分が読めなくなるので、2段目の行にだけ
    文字列として挿入し、他の行はマスターのまま残す。
    """
    lines = body.splitlines()
    out: list[str] = []
    i = 0
    block_re = re.compile(r"^\s+([A-Za-z_][A-Za-z_0-9]*) \{$")
    current_layer: str | None = None

    while i < len(lines):
        line = lines[i]
        match = block_re.match(line)
        if match:
            current_layer = match.group(1)
            out.append(line)
            i += 1
            continue

        if line.strip() == "bindings = <" and current_layer is not None:
            out.append(line)
            i += 1
            rows: list[str] = []
            while i < len(lines) and lines[i].strip() != ">;":
                rows.append(lines[i])
                i += 1
            if len(rows) <= ROBA_EXTRA_ROW:
                raise SystemExit(
                    f"レイヤー {current_layer} の行数が足りません: {len(rows)}"
                )
            extra = extra_for.get(current_layer, ROBA_EXTRA_DEFAULT)
            target = rows[ROBA_EXTRA_ROW]
            offsets = binding_offsets(target)
            if len(offsets) <= ROBA_EXTRA_INDEX:
                raise SystemExit(
                    f"レイヤー {current_layer} の 2段目のキー数が足りません: {len(offsets)}"
                )
            at = offsets[ROBA_EXTRA_INDEX]
            rows[ROBA_EXTRA_ROW] = target[:at] + extra + "  " + target[at:]

            total = sum(len(binding_offsets(row)) for row in rows)
            if total != expected_keys:
                raise SystemExit(
                    f"レイヤー {current_layer} のキー数が {total} 個です"
                    f"（{expected_keys} 個であるべき）。マスターのレイアウトが"
                    f"変わった可能性があります。tools/sync-keymap.py を見直してください。"
                )
            out.extend(rows)
            continue

        out.append(line)
        i += 1

    return "\n".join(out) + "\n"


def shift_combo_positions(body: str, threshold: int, delta: int) -> str:
    """コンボの key-positions のうち threshold 以上の値を delta ずらす。"""

    def repl(match: re.Match[str]) -> str:
        positions = [int(v) for v in match.group(1).split()]
        shifted = [p + delta if p >= threshold else p for p in positions]
        return "key-positions = <" + " ".join(str(p) for p in shifted) + ">;"

    return re.sub(r"key-positions = <([\d\s]+)>;", repl, body)


def drop_porting_comments(body: str) -> str:
    """moNa2 への移植時に付けた '// roBa: ... → moNa2: ...' のコメントを落とす。"""
    out: list[str] = []
    for line in body.splitlines():
        if re.match(r"^\s*// roBa: ", line):
            # 直後の空行も一緒に落とす
            if out and out[-1].strip() == "":
                out.pop()
            continue
        out.append(line)
    return "\n".join(out) + "\n"


GENERATED_MARKER = "このファイルは自動生成です"

GENERATED_BANNER = """\
/*
 * {marker}。直接編集しないでください。
 *
 * マスター : https://github.com/dgarai/zmk-config-moNa2-v2 の config/mona2.keymap
 * 生成     : マスター側の tools/sync-keymap.py（--variant {variant}）
 *
 * キーマップを変えたいときはマスターを編集してください。ここへの変更は
 * 次回の同期で上書きされます。同期の止め方・元に戻し方は KEYMAP-SYNC.md を参照。
 */

"""


def strip_generated_banner(text: str) -> str:
    """前回の同期で付けた自動生成バナーを取り除く（二重に付くのを防ぐ）。"""
    if not text.startswith("/*"):
        return text
    end = text.find("*/")
    if end == -1 or GENERATED_MARKER not in text[:end]:
        return text
    return text[end + 2 :].lstrip("\n")


def build_paw3222(master_text: str, _target_text: str) -> str:
    # 同じ 42 キーの moNa2 シールド。センサーの違いは boards/ と *.conf 側なので
    # keymap はマスターをそのまま使える。
    header, body = split_header_body(master_text)
    return GENERATED_BANNER.format(marker=GENERATED_MARKER, variant="paw3222") + header + body


def build_roba(master_text: str, target_text: str) -> str:
    # デバイス固有ヘッダ（&trackball など）は変換先の既存のものを温存する。
    target_header, _ = split_header_body(strip_generated_banner(target_text))
    _, master_body = split_header_body(master_text)
    body = drop_porting_comments(master_body)
    body = shift_combo_positions(body, ROBA_EXTRA_POSITION, 1)
    body = transform_layers(body, ROBA_EXTRA_PER_LAYER, ROBA_KEY_COUNT)
    return GENERATED_BANNER.format(marker=GENERATED_MARKER, variant="roBa") + target_header + body


BUILDERS = {"paw3222": build_paw3222, "roBa": build_roba}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", required=True, choices=sorted(BUILDERS))
    parser.add_argument("--out", required=True, type=pathlib.Path)
    parser.add_argument(
        "--master",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parent.parent / "config" / "mona2.keymap",
    )
    args = parser.parse_args()

    master_text = args.master.read_text(encoding="utf-8")
    target_text = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
    if not target_text and args.variant == "roBa":
        raise SystemExit("roBa はヘッダを既存ファイルから引き継ぐため、--out が存在する必要があります")

    result = BUILDERS[args.variant](master_text, target_text)
    if result == target_text:
        print(f"{args.out}: 変更なし")
        return 0
    args.out.write_text(result, encoding="utf-8")
    print(f"{args.out}: 更新しました")
    return 0


if __name__ == "__main__":
    sys.exit(main())
