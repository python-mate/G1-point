# G1-point

🏇 G1-point, joint development Python project! This project has three major sections.

First, input and output, using LineMessagingApi. Second, scraping, using requests and beautifulsoup4. Third, store data into SpreadSheets. Pipenv, Heroku, Flask web app, deployment using GitHub Actions.

## LT document

このプロジェクトは Lightening Talk を見据えて進められました。 LT 資料はこちら([G1-point/docs/(2021-04-27)ふたりLT発表用.md](https://github.com/yuu-eguci/G1-point/blob/main/docs/(2021-04-27)ふたりLT発表用.md))。

## G1-point structure

### Blueprint

一番最初の打ち合わせで作成された設計図です。

![first-blueprint](https://user-images.githubusercontent.com/28250432/115021400-e1a89f80-9ef6-11eb-8aca-10a214f4a84a.png)

### Blueprint ver2

設計図に具体性を加えたものです。

![second-blueprint](https://user-images.githubusercontent.com/28250432/117222088-9e7e8400-ae45-11eb-91e6-a2b5004e4930.png)

### Structure note by REDpapa

REDpapa による整理図です。

![papaサンによる整理](https://user-images.githubusercontent.com/28250432/117222240-fcab6700-ae45-11eb-88ff-ec352086e4fb.png)

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

G1-point repository はたくさん環境変数を使っています。一部のスクリプトは、以下の .env を必要とします。

```env
# 実際にプログラムが動く環境で必要な env(Heroku を想定)
LINE_CHANNEL_ACCESS_TOKEN = ''
LINE_CHANNEL_SECRET = ''
LINE_G1_GROUP_ID = ''
SLACK_CHANNEL_NAME = ''
SLACK_BOT_TOKEN = ''
GSPREAD_CREDENTIAL_JSON = ''

# CI/CD 環境で必要な env(GitHub Actions を想定)
HEROKU_API_KEY = ''
HEROKU_APP_NAME = ''
HEROKU_EMAIL = ''
```
