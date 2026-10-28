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

# COROPITを使用するへ

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
