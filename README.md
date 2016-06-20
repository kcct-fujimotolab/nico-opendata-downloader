# nico-opendata Downloader

## 使い方

1. `.env.sample` を参考に `.env` を作成する．

```sh
email="xxx@example.com"
Policy="XXXXXXXXXXXXXXXX"
Signature="XXXXXXXXXXXXXXXX"
Key-Pair-Id="XXXXXXXXXXXXXXXX"
```

2. 依存パッケージをインストールする

```
pip install -r requirements.txt
```

3. ダウンロードコマンドを叩く．

```
python dl_nico_opendata.py --all
```
