# Viewkit

## 概要

- wxPythonを用いたアクセシブルなWindows向けアプリケーションを作るためのライブラリ。
- 開発元であるAccessibleToolsLaboratoryのWindows向けソフトウェア開発に用いることを主目的に開発しているが、このライブラリのみであればラボ以外でもそのまま活用可能にしてある。


## 動作環境

32bit版Python 3.12

## バージョンアップについて

Python3.13対応に向けての課題を書き残しておく。2025年2月現在の情報。
- wxPythonを動かすにはpillowが必須
- Pillow9.5のWheelが3.12までしか存在しない。ここが一番のネック。
- PyInstaller・wxPythonは3.13対応完了していそう。
