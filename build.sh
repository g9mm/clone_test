#!/usr/bin/env bash
# ビルド失敗時にスクリプトを終了する
set -o errexit

# ffmpegのインストール
pip install ffmpeg-python

# Pythonのパッケージインストール
pip install -r requirements.txt