## 概要

Viewkitは、wxPythonを基盤としたアクセシブルなWindowsアプリケーション開発のためのPythonライブラリです。ACT Laboratory（AccessibleToolsLaboratory）が開発し、主にアクセシビリティを重視したGUIアプリケーションの迅速な開発を目的としています。

## 基本情報

- **プロジェクト名**: viewkit
- **バージョン**: 0.1.0
- **開発者**: ACT Laboratory
- **対象プラットフォーム**: Windows
- **Python要件**: Python 3.8-3.12 (32bit版推奨)
- **ライセンス**: 明記なし（コピーライト表示あり）

## 主要な依存関係

```
wxpython==4.2.2      # GUI フレームワーク
pywin32              # Windows API アクセス
winpaths             # Windows パス管理
pyinstaller==6.11.0  # 実行ファイル作成
pillow==9.5          # 画像処理
autopep8             # コード整形
cerberus             # データ検証
```

## アーキテクチャ概要

Viewkitは以下の主要コンポーネントで構成されています：

### 1. アプリケーション管理 (`app.py`, `mainwnd.py`)

- **App**: wxPythonアプリケーションのライフサイクル管理
- **MainWindow**: メインウィンドウの基底クラス
- 多言語対応（gettext使用）
- 設定ファイル管理

### 2. コンテキスト管理 (`context/`)

- **ApplicationContext**: アプリケーション全体の設定・状態管理
- **WindowContext**: ウィンドウレベルの状態管理
- メニュー、機能、参照の統合管理

### 3. UI作成システム (`creator/`)

- **ViewCreator**: 宣言的UI作成の中核クラス
- 豊富なウィジェット対応（ボタン、テキスト、リスト等）
- ダークモード対応
- アクセシビリティ最適化

### 4. 機能管理 (`feature/`)

- **Feature**: アプリケーション機能の抽象化
- **FeatureStore**: 機能の登録・管理
- ショートカットキー統合

### 5. メニューシステム (`menu/`)

- 階層メニュー構造
- アクセラレータキー対応
- 動的メニュー生成

### 6. 設定・ショートカット管理 (`settings/`, `shortcut/`)

- JSON設定ファイル管理
- ショートカットキー検証・管理
- 設定の永続化

## ディレクトリ構造

```
viewkit/
├── __init__.py           # メインエントリポイント
├── app.py               # アプリケーション管理
├── mainwnd.py           # メインウィンドウ基底クラス
├── context/             # コンテキスト管理
│   ├── app.py          # アプリケーションコンテキスト
│   └── window.py       # ウィンドウコンテキスト
├── creator/             # UI作成システム
│   ├── viewCreator.py  # UI作成の中核
│   └── objects/        # 各種ウィジェット実装
├── feature/             # 機能管理
├── menu/               # メニューシステム
├── settings/           # 設定管理
├── shortcut/           # ショートカット管理
├── ref/                # 参照管理
├── views/              # 標準ダイアログ
└── viewHelper.dll      # Windowsネイティブ最適化
```

## 開発上の注意点

### プラットフォーム制限

- Windows専用設計
- 32bit Python推奨
- viewHelper.dllのネイティブ依存

### 依存関係管理

- wxPython 4.2.2固定
- PyInstaller 6.11.0固定
- バージョン固定による安定性重視

## 対象ユーザー

- アクセシブルなWindows GUI アプリケーション開発者
- ACT Laboratory内での活用が主目的
- スクリーンリーダー対応アプリケーション開発者
- 迅速なプロトタイピングが必要な開発者

## まとめ

Viewkitは、アクセシビリティを最優先に設計されたwxPython抽象化ライブラリです。宣言的UI作成、機能ベースアーキテクチャ、統合された設定・ショートカット管理により、アクセシブルなWindowsアプリケーションの迅速な開発を可能にします。Windows専用ですが、その制約により最適化された設計となっています。
