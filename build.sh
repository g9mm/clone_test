#!/usr/bin/env bash
# ビルド失敗時にスクリプトを終了する
set -o errexit

# ffmpegのインストール
apt-get update
apt-get install -y ffmpeg

# Pythonのパッケージインストール
pip install -r requirements.txt