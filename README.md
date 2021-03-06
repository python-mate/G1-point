# G1-point

๐ G1-point, joint development Python project! This project has three major sections.

First, input and output, using LineMessagingApi. Second, scraping, using requests and beautifulsoup4. Third, store data into SpreadSheets. Pipenv, Heroku, Flask web app, deployment using GitHub Actions.

## LT document

ใใฎใใญใธใงใฏใใฏ Lightening Talk ใ่ฆๆฎใใฆ้ฒใใใใพใใใ LT ่ณๆใฏใใกใ([G1-point/docs/(2021-04-27)ใตใใLT็บ่กจ็จ.md](https://github.com/yuu-eguci/G1-point/blob/main/docs/(2021-04-27)ใตใใLT็บ่กจ็จ.md))ใ

## G1-point structure

### Blueprint

ไธ็ชๆๅใฎๆใกๅใใใงไฝๆใใใ่จญ่จๅณใงใใ

![first-blueprint](https://user-images.githubusercontent.com/28250432/115021400-e1a89f80-9ef6-11eb-8aca-10a214f4a84a.png)

### Blueprint ver2

่จญ่จๅณใซๅทไฝๆงใๅ ใใใใฎใงใใ

![second-blueprint](https://user-images.githubusercontent.com/28250432/117222088-9e7e8400-ae45-11eb-91e6-a2b5004e4930.png)

### Structure note by REDpapa

REDpapa ใซใใๆด็ๅณใงใใ

![papaใตใณใซใใๆด็](https://user-images.githubusercontent.com/28250432/117222240-fcab6700-ae45-11eb-88ff-ec352086e4fb.png)

## How to install

ใพใไฝใใใฎๆนๆณใง pipenv ใๆใซๅฅใใฆใใ ใใใ

- [https://pipenv-ja.readthedocs.io/ja/translate-ja/install.html#installing-pipenv](https://pipenv-ja.readthedocs.io/ja/translate-ja/install.html#installing-pipenv)

ใๆใซๅฅใใใใใฎใใใใใใชใ? ใใกใโใฎใณใใณใใ Terminal ใงๆใฃใฆใใใผใธใงใณใๅบใใฐๆๅใงใใ

```bash
pipenv --version
# -> pipenv, version 2020.11.15 ใฟใใใซๅบใใฐ OK.
```

pipenv ใๆใซๅฅใใฆใใใใใโใงใใ

```bash
git clone https://github.com/yuu-eguci/G1-point.git
cd G1-point
pipenv install
pipenv shell
# --> (G1-point) bash-3.2$ ใฟใใใซๅบใใฐ OK.
```

## How to develop

- ้็บใฏใในใฆ `pipenv shell` ใใฆใใ่กใฃใฆใใ ใใใ
- pip ใขใธใฅใผใซใฎใคใณในใใผใซใฏใในใฆ `pipenv install [ใใใฑใผใธใฎๅๅ]` ใง่กใฃใฆใใ ใใใ

```bash
# ไฝๆฅญใๅงใใใจใใฏใพใใใใใใใ
pipenv shell

# (ใใจใใฐ)numpy ๅฅใใใใชโฆโฆใฃใฆใใใจใใฏใใใใใ
pipenv install numpy
```

## .env

G1-point repository ใฏใใใใ็ฐๅขๅคๆฐใไฝฟใฃใฆใใพใใไธ้จใฎในใฏใชใใใฏใไปฅไธใฎ .env ใๅฟ่ฆใจใใพใใ

```env
# ๅฎ้ใซใใญใฐใฉใ ใๅใ็ฐๅขใงๅฟ่ฆใช env(Heroku ใๆณๅฎ)
LINE_CHANNEL_ACCESS_TOKEN = ''
LINE_CHANNEL_SECRET = ''
LINE_G1_GROUP_ID = ''
SLACK_CHANNEL_NAME = ''
SLACK_BOT_TOKEN = ''
GSPREAD_CREDENTIAL_JSON = ''

# CI/CD ็ฐๅขใงๅฟ่ฆใช env(GitHub Actions ใๆณๅฎ)
HEROKU_API_KEY = ''
HEROKU_APP_NAME = ''
HEROKU_EMAIL = ''
```
