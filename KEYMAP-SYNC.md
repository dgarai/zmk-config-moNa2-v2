# キーマップ同期（マスター側）

このリポジトリの `config/mona2.keymap` を唯一の真実として、同じレイアウトの
他のキーボード 2 台へキーマップを配る仕組み。導入日 2026-10-28。

```
keymap-editor で このリポジトリ を SAVE
  → main に push
      ├─ build.yml        このリポジトリのファームウェア
      ├─ draw.yml         このリポジトリのキーマップ図
      └─ sync-keymap.yml  ← 同期
           ├─ dgarai/zmk-for-moNa2-paw3222 へ push → 向こうの build / draw が走る
           └─ dgarai/zmk-config-roBa       へ push → 向こうの build / draw が走る
```

## 守ること

**キーマップの編集はこのリポジトリだけで行う。** paw3222 と roBa の
`config/*.keymap` は自動生成なので、そちらを keymap-editor で編集しても
次の同期で上書きされる。keymap-editor には このリポジトリ だけを登録しておく。

## 同期先ごとの変換内容

| 同期先 | キー数 | 変換 |
|---|---|---|
| paw3222 | 42 | 同じ moNa2 シールドなので丸ごとコピー。センサーの違いは `boards/` と `*.conf` 側なのでキーマップには出てこない |
| roBa | 43 | 2段目の左内側に moNa2 には無いキーが 1 個あるため、各レイヤーの 2段目に 1 個補う。コンボの `key-positions` を 15 以降 +1 ずらす。`#include` や `&trackball` などのデバイス固有ヘッダは roBa 側の既存のものを温存する |

roBa で補うキーは `tools/sync-keymap.py` の `ROBA_EXTRA_PER_LAYER` で決めている。
現状は default レイヤーが `&kp LS(LG(S))`（macOS スクリーンショット）、
NUM レイヤーが `&kp LC(LA(KP_NUMBER_0))`、残りのレイヤーは `&trans`。

変換後に各レイヤーのキー数を検証しており、数が合わないと同期は失敗して止まる。
レイアウト自体を変えたときは `tools/sync-keymap.py` の定数を見直すこと。

## 手元で動かす

```sh
git clone https://github.com/dgarai/zmk-for-moNa2-paw3222.git
git clone https://github.com/dgarai/zmk-config-roBa.git

python3 tools/sync-keymap.py --variant paw3222 --out ../zmk-for-moNa2-paw3222/config/mona2.keymap
python3 tools/sync-keymap.py --variant roBa    --out ../zmk-config-roBa/config/roBa.keymap
```

何度実行しても同じ結果になる（冪等）。差分が無ければ「変更なし」と出て何もしない。

## 必要な Secrets

| Secret 名 | 用途 |
|---|---|
| `DEPLOY_KEY_PAW3222` | paw3222 リポジトリへ push するためのデプロイキー（秘密鍵） |
| `DEPLOY_KEY_ROBA` | roBa リポジトリへ push するためのデプロイキー（秘密鍵） |

`GITHUB_TOKEN` ではなくデプロイキーを使うのは意図的。`GITHUB_TOKEN` による push は
GitHub が再帰防止のためワークフローをトリガーしない仕様なので、同期しても同期先の
`build.yml` が走らず、ファームウェアが更新されない。デプロイキーなら通常の push と
同じように走る。PAT でも走るが、デプロイキーはリポジトリ 1 個の書き込みに限定される
ぶん権限が狭いのでこちらを選んだ。

### 鍵の作り直し方

```sh
ssh-keygen -t ed25519 -N "" -C "keymap-sync paw3222" -f /tmp/sync_paw3222
ssh-keygen -t ed25519 -N "" -C "keymap-sync roBa"    -f /tmp/sync_roBa
```

- 公開鍵（`.pub`）→ 同期先リポジトリの Settings → Deploy keys → Add deploy key。
  **Allow write access にチェックを入れる**
- 秘密鍵 → このリポジトリの Settings → Secrets and variables → Actions → 上の表の名前で登録
- 登録が終わったら `/tmp` の鍵は消す

## 元に戻す

### 一時的に止めたいだけ

GitHub の Actions タブ → 左の "Sync keymap to other boards" → 右上の `…` →
Disable workflow。同期先のファイルはそのまま残る。再開は Enable workflow。

### 同期の仕組みを完全に撤去する

```sh
git rm .github/workflows/sync-keymap.yml
git rm tools/sync-keymap.py
git rm KEYMAP-SYNC.md
git commit -m "Remove keymap sync" && git push
```

そのうえで

- このリポジトリの Settings → Secrets から `DEPLOY_KEY_PAW3222` と `DEPLOY_KEY_ROBA` を削除
- 同期先 2 つの Settings → Deploy keys から対応する鍵を削除
- 同期先のキーマップを導入前に戻す（手順は同期先の `KEYMAP-SYNC.md` に書いてある）

### 導入前のコミット

同期導入の直前の状態はこれ。ここに戻せば導入前に戻る。

| リポジトリ | コミット |
|---|---|
| zmk-config-moNa2-v2（このリポジトリ） | `ee50f28c00bac0bb6f13c6c0b621b988c0928281` |
| zmk-for-moNa2-paw3222 | `ae996d2b1faa9f86773b3a69049c6c67aa6acdc2` |
| zmk-config-roBa | `3f5865996afc1c2b912daad2ad277f5471bf6fc3` |
