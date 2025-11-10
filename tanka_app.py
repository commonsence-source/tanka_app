import streamlit as st
import random
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# 日本語フォント登録
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

# 保存フォルダ
DATA_DIR = Path("tanka_data")
DATA_DIR.mkdir(exist_ok=True)

st.title("📜 オンライン歌会")
st.write("短歌を投稿して、縦書き／横書き表示・PDF出力ができます。")

# --- 歌会名 ---
kakai_name = st.text_input("歌会名を入力してください", "春の会")
file_path = DATA_DIR / f"{kakai_name}.txt"

# --- 投稿フォーム ---
author = st.text_input("お名前（任意）")
tanka = st.text_area("短歌（1首）")

if st.button("投稿する"):
    if tanka.strip():
        with file_path.open("a", encoding="utf-8") as f:
            if author.strip():
                entry = f"{author.strip() }：{tanka.strip()}\n"
            else:
                entry = f"{tanka.strip()}\n"
            f.write(entry)
        st.success(f"「{kakai_name}」に短歌を投稿しました！")
    else:
        st.warning("短歌を入力してください。")

st.divider()

# --- 投稿一覧 ---
if file_path.exists():
    with file_path.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if st.button("ランダムに並び替える"):
        random.shuffle(lines)

    # 表示モード
    display_mode = st.radio(
        "表示モードを選択してください：",
        ["横書き", "縦書き"],
        horizontal=True
    )

    st.write("### 📖 投稿された短歌")

    # --- 表示スタイル ---
    if display_mode == "縦書き":
        st.markdown("""
        <style>
        .vertical-text {
            writing-mode: vertical-rl;
            text-orientation: upright;
            font-size: 1.2rem;
            line-height: 2;
            white-space: pre-wrap;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 10px;
            background-color: #fafafa;
            display: inline-block;
            margin: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

        for line in lines:
            st.markdown(f'<div class="vertical-text">🌸 {line}</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <style>
        .horizontal-text {
            font-size: 1.1rem;
            line-height: 1.6;
            border-bottom: 1px dotted #ccc;
            padding: 6px;
        }
        </style>
        """, unsafe_allow_html=True)

        for line in lines:
            st.markdown(f'<div class="horizontal-text">🌸 {line}</div>', unsafe_allow_html=True)

    st.divider()

    # --- PDF出力 ---
    st.subheader("📄 PDF出力")

    pdf_orientation = st.radio("PDFの向きを選択してください", ["縦書き", "横書き"], horizontal=True)

    if st.button("PDFを作成してダウンロード"):
        buffer = BytesIO()

        if pdf_orientation == "縦書き":
            # --- 縦書きPDF：一文字ずつ縦方向に配置 ---
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            font_name = "HeiseiMin-W3"
            font_size = 14
            col_spacing = 25 * mm  # 各短歌の列間隔
            row_spacing = 7 * mm   # 各文字の縦方向間隔

            # 右端から左へ列を進める
            x = width - 30 * mm
            y_start = height - 30 * mm

            for line in lines:
                y = y_start
                for char in line:
                    c.setFont(font_name, font_size)
                    c.drawString(x, y, char)
                    y -= row_spacing
                    if y < 30 * mm:  # 下端に来たら次ページへ
                        c.showPage()
                        c.setFont(font_name, font_size)
                        y = y_start
                # 一首ごとに左へずらす
                x -= col_spacing
                if x < 30 * mm:  # 左端に来たら新しいページ
                    c.showPage()
                    x = width - 30 * mm
                    y = y_start

            c.showPage()
            c.save()

        else:
            # --- 横書きPDF ---
            c = canvas.Canvas(buffer, pagesize=landscape(A4))
            width, height = landscape(A4)
            font_name = "HeiseiMin-W3"
            font_size = 14
            y = height - 30 * mm

            for line in lines:
                c.setFont(font_name, font_size)
                c.drawString(30 * mm, y, line)
                y -= 12 * mm
                if y < 20 * mm:
                    c.showPage()
                    y = height - 30 * mm
            c.showPage()
            c.save()

        st.download_button(
            label="📥 PDFをダウンロード",
            data=buffer.getvalue(),
            file_name=f"{kakai_name}.pdf",
            mime="application/pdf"
        )

else:
    st.info("まだ投稿がありません。")

