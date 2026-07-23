"""コマンドの入口。第3回で `hitblow` コマンドがここ（main）を呼ぶ。"""

from .game import play


def main():
    print("Hit & Blow へようこそ！")
    while True:
        choice = input("プレイモードを選択してください（1: CUI / 2: GUI）: ").strip()

        if choice == "1":
            play()
            return

        if choice == "2":
            # GUI は tkinter を使うため、CUI 実行環境に影響しないようここで遅延 import する
            from .gui import main as gui_main

            gui_main()
            return

        print("エラー: 1 か 2 を入力してください。")
