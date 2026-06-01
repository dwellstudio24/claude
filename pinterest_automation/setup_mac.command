#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Dwell Studio 24 — Pinterest 自動化 セットアップ
# このファイルをダブルクリックしてください
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cd "$(dirname "$0")"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Dwell Studio 24 — Pinterest セットアップ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Python チェック ──────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "❌ Python3 が見つかりません。"
    echo "   https://python.org/downloads からインストールしてください。"
    read -p "Enterで閉じる..."
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# ── パッケージインストール ────────────────────────
echo ""
echo "📦 パッケージをインストール中..."
pip3 install -r requirements.txt -q
echo "✅ パッケージ インストール完了"

# ── .env セットアップ ─────────────────────────────
if [ ! -f .env ]; then
    cp .env.example .env
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Pinterest アクセストークンを設定します"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Pinterest Developer Portal からトークンを取得して"
echo "以下に貼り付けてください："
echo ""
read -p "アクセストークン: " TOKEN

if [ -n "$TOKEN" ]; then
    # .env のトークン部分を更新
    sed -i '' "s|PINTEREST_ACCESS_TOKEN=.*|PINTEREST_ACCESS_TOKEN=$TOKEN|" .env
    echo ""
    echo "✅ トークンを保存しました"
fi

# ── 接続テスト ────────────────────────────────────
echo ""
echo "🔗 Pinterest接続テスト中..."
python3 main.py verify
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  接続に失敗しました。トークンを確認してください。"
    echo "    もう一度セットアップするには、このファイルをダブルクリックしてください。"
    read -p "Enterで閉じる..."
    exit 1
fi

# ── ボードID確認 ─────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " あなたのPinterestボード一覧:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 main.py boards
echo ""
echo "⬆️  上のボードIDを boards.yaml にコピーしてください"
echo ""
read -p "boards.yaml を今開きますか？ (y/n): " OPEN_BOARDS
if [ "$OPEN_BOARDS" = "y" ]; then
    open boards.yaml
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ✅ セットアップ完了！"
echo ""
echo " 次は run_pinterest.command をダブルクリックして"
echo " ピンを作成してください。"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Enterで閉じる..."
