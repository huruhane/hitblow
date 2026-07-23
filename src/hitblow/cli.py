"""コマンドの入口。第3回で `hitblow` コマンドがここ（main）を呼ぶ。"""

from .game import play


def is_gui_available() -> bool:
    """GUI (tkinter) が利用可能な環境かどうかを判定する"""
    try:
        import tkinter

        # ディスプレイ環境がない（Headless環境等）場合のチェック
        root = tkinter.Tk()
        root.destroy()
        return True
    except Exception:
        # ImportError や TclError (Display couldn't be opened) をキャッチ
        return False


def main():
    print("Hit & Blow へようこそ！")

    gui_supported = is_gui_available()

    # GUIが使えない環境の場合は、即座にCUIを起動する
    if not gui_supported:
        print("※ お使いの環境ではGUIがサポートされていないため、CUIモードで起動します。\n")
        play()
        return

    # GUIが使える環境のみ選択肢を表示する
    while True:
        choice = (
            input("プレイモードを選択してください（1: CUI / 2: GUI）: ")
            .strip()
        )

        if choice == "1":
            play()
            return

        if choice == "2":
            from .gui import main as gui_main

            gui_main()
            return

        print("エラー: 1 か 2 を入力してください。")