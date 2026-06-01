#!/bin/bash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Dwell Studio 24 — ピン作成ツール
# このファイルをダブルクリックして使います
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cd "$(dirname "$0")"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Dwell Studio 24 — Pinterest ピン作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 記事URLを入力 ─────────────────────────────────
read -p "📝 記事のURL: " ARTICLE_URL

if [ -z "$ARTICLE_URL" ]; then
    echo "URLが入力されていません。"
    read -p "Enterで閉じる..."
    exit 1
fi

# ── モード選択 ────────────────────────────────────
echo ""
echo "モードを選んでください："
echo "  1) テスト（画像生成のみ、Pinterestには投稿しない）"
echo "  2) 本番（Pinterestにスケジュール投稿）"
echo ""
read -p "番号を入力 (1 or 2): " MODE

if [ "$MODE" = "1" ]; then
    echo ""
    echo "🖼  画像を生成中（テストモード）..."
    python3 main.py create "$ARTICLE_URL" --dry-run --skip-review
elif [ "$MODE" = "2" ]; then
    echo ""
    echo "📌 ピンを作成・スケジュール中..."
    python3 main.py create "$ARTICLE_URL"
else
    echo "無効な選択です。"
    read -p "Enterで閉じる..."
    exit 1
fi

# ── 完了後にoutputフォルダを開く ──────────────────
echo ""
if [ -d "output" ]; then
    read -p "生成された画像を確認しますか？ (y/n): " OPEN
    if [ "$OPEN" = "y" ]; then
        open output/
    fi
fi

echo ""
read -p "Enterで閉じる..."
