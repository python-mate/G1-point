# G1-point

## G1-point blueprint

![g1-point](https://user-images.githubusercontent.com/28250432/115021400-e1a89f80-9ef6-11eb-8aca-10a214f4a84a.png)

## How to install

まず何らかの方法で pipenv を手に入れてください。

- [https://pipenv-ja.readthedocs.io/ja/translate-ja/install.html#installing-pipenv](https://pipenv-ja.readthedocs.io/ja/translate-ja/install.html#installing-pipenv)

「手に入れられたのか」わからない? こちら↓のコマンドを Terminal で打って、バージョンが出れば成功です。

```bash
pipenv --version
# -> pipenv, version 2020.11.15 みたいに出れば OK.
```

pipenv を手に入れてから、こう↓です。

```bash
git clone https://github.com/yuu-eguci/G1-point.git
cd G1-point
pipenv install
pipenv shell
# --> (G1-point) bash-3.2$ みたいに出れば OK.
```

## How to develop

- 開発はすべて `pipenv shell` してから行ってください。
- pip モジュールのインストールはすべて `pipenv install [パッケージの名前]` で行ってください。

```bash
# 作業を始めるときはまずこれをやる。
pipenv shell

# (たとえば)numpy 入れたいな……っていうときはこうする。
pipenv install numpy
```

## .env

```env
# 実際にプログラムが動く環境で必要な env(Heroku を想定)
LINE_CHANNEL_ACCESS_TOKEN = ''
LINE_CHANNEL_SECRET = ''
LINE_G1_GROUP_ID = ''

# CI/CD 環境で必要な env(GitHub Actions を想定)
HEROKU_API_KEY = ''
HEROKU_APP_NAME = ''
HEROKU_EMAIL = ''
```
