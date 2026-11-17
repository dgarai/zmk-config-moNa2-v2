# zmk-config-moNa2

<img src="keymap-drawer/mona2_01.svg">

## キーマップ同期

このリポジトリの `config/mona2.keymap` が、同じレイアウトのキーボード 3 台のマスター。
ここを更新すると GitHub Actions が以下へ自動で配る。

- [dgarai/zmk-for-moNa2-paw3222](https://github.com/dgarai/zmk-for-moNa2-paw3222)
- [dgarai/zmk-config-roBa](https://github.com/dgarai/zmk-config-roBa)

**キーマップの編集はこのリポジトリだけで行う。** 同期先の keymap は自動生成なので、
そちらを編集しても次の同期で上書きされる。

仕組み・セットアップ・元に戻す手順は [KEYMAP-SYNC.md](KEYMAP-SYNC.md) を参照。

## DYA Studio（レベル2）

[DYA Studio](https://studio.dya.cormoran.works) で、ブラウザからキーマップ・マクロ・コンボ・トラックボール・BLE 接続などを変更できる。

- ZMK 本体は Custom Studio Protocol 対応の [cormoran/zmk `main+dya`](https://github.com/cormoran/zmk/tree/main+dya)（Zephyr 4.1）。実験的な fork なので、壊れたら `main` の旧構成に戻す
- 右手側を USB でつなぎ、Chrome / Edge で開いて「USB」を選ぶ（Bluetooth 接続も可）
- トラックボールの感度・スクロール量・スナップ・オートマウスは Trackball タブで変更できる。初期値は旧構成と同じ向き・量に合わせてある（`boards/shields/mona2/mona2_r.overlay`）
- Studio で変えた内容はキーボード本体に保存され、このリポジトリの `config/mona2.keymap` には戻らない。恒久的に残したい変更は keymap にも反映する
- 旧構成から書き換えた直後は、左右とも `settings_reset` を書き込んでから新しいファームを書き込む

# COROPITを使用するへ

> 注: 下記は旧ドライバ（badjeff 版 `pixart,pmw3610`）時代の手順。DYA Studio 対応後は `invert-x` / `invert-y` の代わりに
> `config/mona2_r.conf` の `CONFIG_PMW3610_INVERT_X` / `CONFIG_PMW3610_INVERT_Y` で指定する（DYA Studio の Trackball タブからも変更可）。

COROPITを使用する方は以下のようにコードを編集してください。

mona2_r.overlay

修正前
```
  trackball_central: trackball_central@0 {
        status = "okay";
        compatible = "pixart,pmw3610";  //トラボセンサ用のドライバとバインド
        reg = <0>;
        spi-max-frequency = <2000000>;
        irq-gpios = <&gpio0 2 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>; //P0.02を指定(MOTION)
        cpi = <600>;
        //swap-xy;
        //invert-x; //COROPIT版ではコメントアウトを外す
        //invert-y; //COROPIT版ではコメントアウトを外す
        evt-type = <INPUT_EV_REL>;
        x-input-code = <INPUT_REL_X>;
        y-input-code = <INPUT_REL_Y>;
    };
};

```
**修正後**
```
  trackball_central: trackball_central@0 {
        status = "okay";
        compatible = "pixart,pmw3610";  //トラボセンサ用のドライバとバインド
        reg = <0>;
        spi-max-frequency = <2000000>;
        irq-gpios = <&gpio0 2 (GPIO_ACTIVE_LOW | GPIO_PULL_UP)>; //P0.02を指定(MOTION)
        cpi = <600>;
        //swap-xy;
        invert-x; //COROPIT版ではコメントアウトを外す
        invert-y; //COROPIT版ではコメントアウトを外す
        evt-type = <INPUT_EV_REL>;
        x-input-code = <INPUT_REL_X>;
        y-input-code = <INPUT_REL_Y>;
    };
};

```
