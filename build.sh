#!/usr/bin/env bash
# ビルド失敗時にスクリプトを終了する
set -o errexit

# ffmpegのインストール
pip update
pip install -y ffmpeg

# Pythonのパッケージインストール
pip install -r requirements.txt