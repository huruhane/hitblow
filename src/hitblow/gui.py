"""Tkinter による Hit & Blow の GUI 版（カード表示版）。

CLI 版（game.py / cli.py）とは別ファイルで、こちらは
    python -m hitblow.gui
または
    python gui.py   （hitblow パッケージのフォルダ内に置いた場合）
で起動できる。

判定ロジックは core.py の judge / make_secret をそのまま使う。
CPU 対戦モードの「候補を絞り込みながら推理する」ロジックは
enemy.py の考え方を、input() を使わないイベント駆動の形に書き直したもの。
アイテム（ヒント表示）も同様に、item.py の「1ゲームにつき1回、テキの
数字を1桁だけ見せる」という考え方を、print() ではなく履歴カードへの
追加としてイベント駆動の形に書き直したもの（使用済みフラグは GUI 側の
インスタンス変数として持つため、「もう一度遊ぶ」で正しくリセットされる）。
タイマーも同様に、time.py の「開始時に計測を始め、決着時に経過時間を
表示する」という考え方を、GUI 側のインスタンス変数（開始時刻）で管理し、
さらに `root.after` による1秒ごとの再描画で「今何秒経ったか」をリアル
タイム表示できるようにしたもの。

このバージョンでの変更点:
    - 予想の結果を、数字ごとの「カード」として表示
        - 桁が完全一致（Hit）              -> 緑背景
        - 数字は合っているが桁違い（Blow） -> オレンジ背景
        - どちらでもない                    -> グレー背景
    - 履歴をスクロール可能なカード一覧として表示（従来のテキストログの代わり）
    - アイテム（ヒント表示）ボタンを追加。1ゲームにつき1回だけ使え、
      テキ（あなたが当てる相手の数字）の中からランダムに1桁を見せる。
    - タイマー表示を追加。ゲーム開始と同時に計測を始め、画面上部に
      経過時間をリアルタイム表示し、決着時に最終タイムを表示する。

含まれる機能:
    - 予想入力・Hit/Blow のカード表示（基本機能）
    - CPU 対戦モード（交互にターンを進める）
    - アイテム（ヒント表示・1ゲーム1回）
    - タイマー表示（リアルタイム経過時間・決着時の最終タイム）
"""

import itertools
import random
import time
import tkinter as tk
from tkinter import messagebox

try:
    # パッケージ内から `python -m hitblow.gui` で起動する場合
    from .core import judge, make_secret
except ImportError:
    # 単独ファイルとして `python gui.py` で起動する場合の保険
    from core import judge, make_secret

# カードの配色（Hit=緑, Blow=オレンジ, それ以外=グレー）
COLOR_HIT = "#4CAF50"
COLOR_BLOW = "#FF9800"
COLOR_NONE = "#E0E0E0"
COLOR_HIT_FG = "white"
COLOR_BLOW_FG = "white"
COLOR_NONE_FG = "#555555"


class HitBlowGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hit & Blow")
        self.root.geometry("560x680")
        self.root.resizable(False, False)

        # ゲーム状態を保持する変数（開始時にリセットされる）
        self.digits = 3
        self.is_cpu_mode = False
        self.cpu_secret = ""  # プレイヤーが当てる相手（CPU or ランダム）の数字＝テキ
        self.my_secret = ""  # CPU が当てる、プレイヤー側の数字
        self.cpu_candidates = []
        self.tries = 0
        self.game_over = False
        self.item_used = False  # アイテム（ヒント）を使用済みかどうか
        self.start_time = None  # ゲーム開始時刻（time.time()）
        self.timer_job = None  # root.after() のジョブID（キャンセル用）

        self._build_setup_frame()

    # ------------------------------------------------------------------
    # 画面①: 開始設定（桁数・CPU対戦モードの有無・自分の秘密の数字）
    # ------------------------------------------------------------------
    def _build_setup_frame(self):
        self.setup_frame = tk.Frame(self.root, padx=20, pady=20)
        self.setup_frame.pack(fill="both", expand=True)

        tk.Label(self.setup_frame, text="Hit & Blow", font=("", 20, "bold")).pack(
            pady=(0, 20)
        )

        # 桁数選択
        digit_row = tk.Frame(self.setup_frame)
        digit_row.pack(pady=5, anchor="w")
        tk.Label(digit_row, text="桁数:").pack(side="left")
        self.digits_var = tk.IntVar(value=3)
        tk.Spinbox(
            digit_row, from_=2, to=6, width=5, textvariable=self.digits_var
        ).pack(side="left", padx=5)

        # CPU対戦モードの有無
        self.cpu_mode_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self.setup_frame,
            text="CPU対戦モードにする（交互に交代して入力）",
            variable=self.cpu_mode_var,
            command=self._toggle_secret_entry,
        ).pack(pady=10, anchor="w")

        # CPU対戦モード時のみ表示: 自分の秘密の数字を入力する欄
        self.secret_row = tk.Frame(self.setup_frame)
        tk.Label(self.secret_row, text="CPUに当てさせる、あなたの秘密の数字:").pack(
            anchor="w"
        )
        self.secret_var = tk.StringVar()
        self.secret_entry = tk.Entry(
            self.secret_row, textvariable=self.secret_var, width=15
        )
        self.secret_entry.pack(anchor="w", pady=(5, 0))

        # 凡例（色の意味を先に見せておく）
        legend_row = tk.Frame(self.setup_frame)
        legend_row.pack(pady=(15, 0), anchor="w")
        self._legend_card(
            legend_row, "1", COLOR_HIT, COLOR_HIT_FG, "Hit（位置も数字も一致）"
        )
        legend_row2 = tk.Frame(self.setup_frame)
        legend_row2.pack(pady=(5, 0), anchor="w")
        self._legend_card(
            legend_row2,
            "2",
            COLOR_BLOW,
            COLOR_BLOW_FG,
            "Blow（数字は合っているが位置違い）",
        )
        legend_row3 = tk.Frame(self.setup_frame)
        legend_row3.pack(pady=(5, 0), anchor="w")
        self._legend_card(legend_row3, "3", COLOR_NONE, COLOR_NONE_FG, "含まれない数字")

        self.start_button = tk.Button(
            self.setup_frame, text="ゲーム開始", command=self._start_game, width=15
        )
        self.start_button.pack(pady=20)

        self.setup_error_label = tk.Label(self.setup_frame, text="", fg="red")
        self.setup_error_label.pack()

    def _legend_card(self, parent, digit, bg, fg, description):
        tk.Label(
            parent,
            text=digit,
            width=3,
            height=1,
            bg=bg,
            fg=fg,
            font=("", 12, "bold"),
            relief="solid",
            bd=1,
        ).pack(side="left")
        tk.Label(parent, text="  " + description).pack(side="left")

    def _toggle_secret_entry(self):
        if self.cpu_mode_var.get():
            self.secret_row.pack(pady=5, anchor="w")
        else:
            self.secret_row.pack_forget()

    def _start_game(self):
        digits = self.digits_var.get()

        if not (2 <= digits <= 6):
            self.setup_error_label.config(text="桁数は2〜6の範囲で指定してください。")
            return

        self.digits = digits
        self.is_cpu_mode = self.cpu_mode_var.get()

        # プレイヤーが当てる相手の数字（ランダム生成）＝テキ
        self.cpu_secret = make_secret(digits)

        if self.is_cpu_mode:
            my_secret = self.secret_var.get().strip()
            if (
                len(my_secret) != digits
                or not my_secret.isdigit()
                or len(set(my_secret)) != digits
            ):
                self.setup_error_label.config(
                    text=f"{digits}桁の重複のない数字を正しく入力してください。"
                )
                return
            self.my_secret = my_secret

            # CPU 側の候補リストを全順列で初期化
            all_perms = itertools.permutations("0123456789", digits)
            self.cpu_candidates = ["".join(p) for p in all_perms]
        else:
            self.my_secret = make_secret(digits)  # 使わないが一応用意しておく

        self.tries = 0
        self.game_over = False
        self.item_used = False  # 新しいゲームなのでアイテムも使える状態に戻す
        self.start_time = (
            time.time()
        )  # ① 開始時刻を記録（time.py の start_timer に相当）

        self.setup_frame.destroy()
        self._build_game_frame()

    # ------------------------------------------------------------------
    # 画面②: ゲーム本編（予想入力・カード履歴表示）
    # ------------------------------------------------------------------
    def _build_game_frame(self):
        self.game_frame = tk.Frame(self.root, padx=20, pady=20)
        self.game_frame.pack(fill="both", expand=True)

        mode_text = "CPU対戦モード" if self.is_cpu_mode else "通常モード"
        header_row = tk.Frame(self.game_frame)
        header_row.pack(fill="x", pady=(0, 10))
        tk.Button(
            header_row, text="⏮ 最初の画面に戻る", command=self._confirm_restart
        ).pack(side="left")
        tk.Label(
            header_row,
            text=f"Hit & Blow（{self.digits}桁・重複なし）－ {mode_text}",
            font=("", 13, "bold"),
        ).pack(side="left", padx=(10, 0))
        self.timer_label = tk.Label(
            header_row, text="⏱️ 0秒", font=("", 11), fg="#555555"
        )
        self.timer_label.pack(side="right")

        # --- スクロール可能な履歴エリア（カードを並べる場所） ---
        history_container = tk.Frame(self.game_frame)
        history_container.pack(fill="both", expand=True)
        self.history_canvas = tk.Canvas(
            history_container,
            width=500,
            height=340,
            highlightthickness=1,
            highlightbackground="#CCCCCC",
        )
        scrollbar = tk.Scrollbar(
            history_container, orient="vertical", command=self.history_canvas.yview
        )
        self.history_canvas.configure(yscrollcommand=scrollbar.set)
        self.history_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.history_frame = tk.Frame(self.history_canvas)
        self.history_window = self.history_canvas.create_window(
            (0, 0), window=self.history_frame, anchor="nw"
        )
        self.history_frame.bind(
            "<Configure>",
            lambda e: self.history_canvas.configure(
                scrollregion=self.history_canvas.bbox("all")
            ),
        )
        self.history_canvas.bind(
            "<Configure>",
            lambda e: self.history_canvas.itemconfig(
                self.history_window, width=e.width
            ),
        )
        # マウスホイールでスクロール
        self.history_canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.history_canvas.yview_scroll(
                int(-1 * (e.delta / 120)), "units"
            ),
        )

        # 入力欄
        input_row = tk.Frame(self.game_frame)
        input_row.pack(pady=10, fill="x")
        tk.Label(input_row, text="予想 > ").pack(side="left")
        self.guess_var = tk.StringVar()
        self.guess_entry = tk.Entry(input_row, textvariable=self.guess_var, width=15)
        self.guess_entry.pack(side="left", padx=5)
        self.guess_entry.bind("<Return>", lambda event: self._submit_guess())
        self.guess_entry.focus_set()

        self.submit_button = tk.Button(
            input_row, text="決定", command=self._submit_guess
        )
        self.submit_button.pack(side="left")

        # アイテム（ヒント）ボタン
        item_row = tk.Frame(self.game_frame)
        item_row.pack(pady=(0, 5), fill="x")
        self.item_button = tk.Button(
            item_row,
            text="🎁 アイテムを使う（ヒントを見る・1ゲーム1回）",
            command=self._use_item,
        )
        self.item_button.pack(side="left")

        self.status_label = tk.Label(self.game_frame, text="", font=("", 11, "bold"))
        self.status_label.pack(pady=(10, 0))

        self._add_info_row(f"ゲームを開始します（{self.digits}桁・重複なし）。")
        if self.is_cpu_mode:
            self._add_info_row(
                "⚔️ CPU対戦モード：あなたとCPUが交互に相手の数字を当て合います。"
            )

        self._tick_timer()  # ① タイマー表示の更新ループを開始

    # ------------------------------------------------------------------
    # タイマー（time.py の start_timer / show_clear_time に相当）
    # ------------------------------------------------------------------
    def _format_elapsed(self, elapsed_seconds):
        """経過秒数を「X分Y秒」または「Y秒」の文字列にする。"""
        minutes = int(elapsed_seconds // 60)
        seconds = int(elapsed_seconds % 60)
        if minutes > 0:
            return f"{minutes}分{seconds}秒"
        return f"{seconds}秒"

    def _tick_timer(self):
        """1秒ごとに呼び出され、経過時間の表示を更新し続ける。"""
        if self.game_over or self.start_time is None:
            return

        elapsed = time.time() - self.start_time
        self.timer_label.config(text=f"⏱️ {self._format_elapsed(elapsed)}")
        self.timer_job = self.root.after(1000, self._tick_timer)

    def _stop_timer(self):
        """タイマーの更新ループを止める（決着時・再スタート時に呼ぶ）。"""
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    # ------------------------------------------------------------------
    # 履歴エリアへの行追加
    # ------------------------------------------------------------------
    def _add_info_row(self, text):
        """カードではない、通常のお知らせテキストを履歴に追加する。"""
        row = tk.Frame(self.history_frame, pady=4)
        row.pack(fill="x", anchor="w")
        tk.Label(row, text=text, anchor="w", justify="left", wraplength=460).pack(
            side="left"
        )
        self._scroll_to_bottom()

    def _add_guess_row(self, label_text, guess, secret, hit, blow):
        """予想結果を、桁ごとに色分けしたカードとして履歴に追加する。"""
        row = tk.Frame(self.history_frame, pady=6)
        row.pack(fill="x", anchor="w")

        tk.Label(row, text=label_text, width=6, anchor="w", font=("", 10, "bold")).pack(
            side="left"
        )

        cards_frame = tk.Frame(row)
        cards_frame.pack(side="left")
        for i, ch in enumerate(guess):
            if ch == secret[i]:
                bg, fg = COLOR_HIT, COLOR_HIT_FG
            elif ch in secret:
                bg, fg = COLOR_BLOW, COLOR_BLOW_FG
            else:
                bg, fg = COLOR_NONE, COLOR_NONE_FG
            tk.Label(
                cards_frame,
                text=ch,
                width=3,
                height=1,
                bg=bg,
                fg=fg,
                font=("", 16, "bold"),
                relief="solid",
                bd=1,
            ).pack(side="left", padx=2)

        tk.Label(
            row,
            text=f"   Hit={hit}  Blow={blow}",
            anchor="w",
        ).pack(side="left", padx=(10, 0))

        self._scroll_to_bottom()

    def _add_hint_row(self, digit):
        """アイテム使用時のヒントを、専用の見た目で履歴に追加する。"""
        row = tk.Frame(self.history_frame, pady=6)
        row.pack(fill="x", anchor="w")

        tk.Label(row, text="ヒント", width=6, anchor="w", font=("", 10, "bold")).pack(
            side="left"
        )
        tk.Label(
            row,
            text=digit,
            width=3,
            height=1,
            bg="#2196F3",
            fg="white",
            font=("", 16, "bold"),
            relief="solid",
            bd=1,
        ).pack(side="left", padx=2)
        tk.Label(
            row,
            text="   この数字はテキに含まれています",
            anchor="w",
        ).pack(side="left", padx=(10, 0))

        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        self.history_frame.update_idletasks()
        self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))
        self.history_canvas.yview_moveto(1.0)

    # ------------------------------------------------------------------
    # アイテム（ヒント表示）
    # ------------------------------------------------------------------
    def _use_item(self):
        """テキ（cpu_secret）の中からランダムに1桁を見せる。1ゲームにつき1回のみ。"""
        if self.game_over or self.item_used:
            return

        idx = random.randint(0, self.digits - 1)
        digit = self.cpu_secret[idx]

        self._add_hint_row(digit)

        self.item_used = True
        self.item_button.config(state="disabled")

    # ------------------------------------------------------------------
    # プレイヤーの手番
    # ------------------------------------------------------------------
    def _submit_guess(self):
        if self.game_over:
            return

        guess = self.guess_var.get().strip()

        if len(guess) != self.digits or not guess.isdigit():
            messagebox.showwarning(
                "入力エラー", f"{self.digits}桁の数字で入力してください。"
            )
            return

        self.guess_var.set("")
        self.tries += 1

        hit, blow = judge(self.cpu_secret, guess)
        self._add_guess_row("あなた", guess, self.cpu_secret, hit, blow)

        if hit == self.digits:
            elapsed_text = self._format_elapsed(time.time() - self.start_time)
            self.status_label.config(
                text=(
                    f"🎉 正解！ あなたの勝利です！"
                    f"（ターン数: {self.tries} 回 / クリア時間: {elapsed_text}）"
                ),
                fg="#2E7D32",
            )
            self._end_game()
            return

        if self.is_cpu_mode:
            self._cpu_turn()

    # ------------------------------------------------------------------
    # CPU の手番
    # ------------------------------------------------------------------
    def _cpu_turn(self):
        if not self.cpu_candidates:
            self._add_info_row(
                "🤔 CPU「候補が尽きてしまいました…推理を続けられません」"
            )
            return

        cpu_guess = random.choice(self.cpu_candidates)
        cpu_hit, cpu_blow = judge(self.my_secret, cpu_guess)
        self._add_guess_row("CPU", cpu_guess, self.my_secret, cpu_hit, cpu_blow)

        if cpu_hit == self.digits:
            elapsed_text = self._format_elapsed(time.time() - self.start_time)
            self.status_label.config(
                text=(
                    f"💀 残念！CPUが先に正解してしまいました…"
                    f"（答え: {self.my_secret} / 決着までの時間: {elapsed_text}）"
                ),
                fg="#C62828",
            )
            self._end_game()
            return

        # 候補を絞り込む
        self.cpu_candidates = [
            cand
            for cand in self.cpu_candidates
            if judge(cand, cpu_guess) == (cpu_hit, cpu_blow)
        ]

    def _end_game(self):
        self.game_over = True
        self._stop_timer()
        self.submit_button.config(state="disabled")
        self.guess_entry.config(state="disabled")
        self.item_button.config(state="disabled")

        restart_button = tk.Button(
            self.game_frame, text="もう一度遊ぶ", command=self._restart, width=15
        )
        restart_button.pack(pady=10)

    def _confirm_restart(self):
        """途中で最初の画面に戻る（決着前は確認ダイアログを挟む）。"""
        if not self.game_over:
            if not messagebox.askyesno(
                "確認", "現在のゲームを中断して、最初の画面に戻りますか？"
            ):
                return
        self._restart()

    def _restart(self):
        self._stop_timer()
        self.history_canvas.unbind_all("<MouseWheel>")
        self.game_frame.destroy()
        self._build_setup_frame()


def main():
    root = tk.Tk()
    HitBlowGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
