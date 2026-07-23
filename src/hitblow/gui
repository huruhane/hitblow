"""Tkinter による Hit & Blow の GUI 版。

CLI 版（game.py / cli.py）とは別ファイルで、こちらは
    python -m hitblow.gui
または
    python gui.py   （hitblow パッケージのフォルダ内に置いた場合）
で起動できる。

判定ロジックは core.py の judge / make_secret をそのまま使い、
CPU 対戦モードの「候補を絞り込みながら推理する」ロジックは
enemy.py の考え方を、input() を使わないイベント駆動の形に書き直したもの。

含まれる機能:
    - 予想入力・Hit/Blow 表示（基本機能）
    - CPU 対戦モード（交互にターンを進める）

含まれない機能（CLI 版のみ）:
    - アイテム（ヒント表示）
    - タイマー表示
"""

import itertools
import random
import tkinter as tk
from tkinter import messagebox, scrolledtext

try:
    # パッケージ内から `python -m hitblow.gui` で起動する場合
    from .core import judge, make_secret
except ImportError:
    # 単独ファイルとして `python gui.py` で起動する場合の保険
    from core import judge, make_secret


class HitBlowGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hit & Blow")
        self.root.geometry("480x560")
        self.root.resizable(False, False)

        # ゲーム状態を保持する変数（開始時にリセットされる）
        self.digits = 3
        self.is_cpu_mode = False
        self.cpu_secret = ""  # プレイヤーが当てる相手（CPU or ランダム）の数字
        self.my_secret = ""  # CPU が当てる、プレイヤー側の数字
        self.cpu_candidates = []
        self.tries = 0
        self.game_over = False

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

        self.start_button = tk.Button(
            self.setup_frame, text="ゲーム開始", command=self._start_game, width=15
        )
        self.start_button.pack(pady=20)

        self.setup_error_label = tk.Label(self.setup_frame, text="", fg="red")
        self.setup_error_label.pack()

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

        # プレイヤーが当てる相手の数字（ランダム生成）
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

        self.setup_frame.destroy()
        self._build_game_frame()

    # ------------------------------------------------------------------
    # 画面②: ゲーム本編（予想入力・ログ表示）
    # ------------------------------------------------------------------
    def _build_game_frame(self):
        self.game_frame = tk.Frame(self.root, padx=20, pady=20)
        self.game_frame.pack(fill="both", expand=True)

        mode_text = "CPU対戦モード" if self.is_cpu_mode else "通常モード"
        tk.Label(
            self.game_frame,
            text=f"Hit & Blow（{self.digits}桁・重複なし）－ {mode_text}",
            font=("", 13, "bold"),
        ).pack(pady=(0, 10))

        # ログ表示欄
        self.log_area = scrolledtext.ScrolledText(
            self.game_frame, width=52, height=20, state="disabled", wrap="word"
        )
        self.log_area.pack(pady=5)

        # 入力欄
        input_row = tk.Frame(self.game_frame)
        input_row.pack(pady=10)

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

        self._log(f"ゲームを開始します（{self.digits}桁・重複なし）。")
        if self.is_cpu_mode:
            self._log("⚔️ CPU対戦モード：あなたとCPUが交互に相手の数字を当て合います。")

    def _log(self, text):
        self.log_area.config(state="normal")
        self.log_area.insert("end", text + "\n")
        self.log_area.config(state="disabled")
        self.log_area.see("end")

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
        self._log(f"[あなた] 予想 > {guess}   Hit={hit}  Blow={blow}")

        if hit == self.digits:
            self._log(f"\n🎉 正解！ あなたの勝利です！（ターン数: {self.tries} 回）")
            self._end_game()
            return

        if self.is_cpu_mode:
            self._cpu_turn()

    # ------------------------------------------------------------------
    # CPU の手番
    # ------------------------------------------------------------------
    def _cpu_turn(self):
        if not self.cpu_candidates:
            self._log("🤔 CPU「候補が尽きてしまいました…推理を続けられません」")
            return

        cpu_guess = random.choice(self.cpu_candidates)
        cpu_hit, cpu_blow = judge(self.my_secret, cpu_guess)
        self._log(f"[CPU] 予想 > {cpu_guess}   Hit={cpu_hit}  Blow={cpu_blow}")

        if cpu_hit == self.digits:
            self._log(
                f"\n💀 残念！CPUが先に正解してしまいました…（答え: {self.my_secret}）"
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
        self.submit_button.config(state="disabled")
        self.guess_entry.config(state="disabled")

        restart_button = tk.Button(
            self.game_frame, text="もう一度遊ぶ", command=self._restart, width=15
        )
        restart_button.pack(pady=10)

    def _restart(self):
        self.game_frame.destroy()
        self._build_setup_frame()


def main():
    root = tk.Tk()
    HitBlowGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
