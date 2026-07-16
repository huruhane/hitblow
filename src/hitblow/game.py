"""ゲームの進行（入力・表示・ループ）。

★ チームで足す機能は **自分の担当の場所**に書く（1機能=1ファイル）。
   下の「ここに足す」場所は3か所（① 開始時 ② 入力コマンド ③ 勝利時）。
   ペアごとに**別の場所**を直すので、並行作業でも衝突しない。
   import も自分の場所の近くに書くこと（ファイル先頭にまとめない＝衝突回避）。
"""

from .core import judge, make_secret
from .item import show_secret_number, can_use_item


def play(digits=3):
    secret = make_secret(digits)
    teki = make_secret(digits)
    print(f"Hit & Blow（{digits} 桁・重複なし）")

    # ===== ① 開始時に足す（難易度・あいさつ など）: ここに書く =====

    tries = 0
    while True:
        # まだアイテムを使える状態なら、使うかどうかを尋ねる
        if can_use_item():
            item = input("アイテムを使いますか？（y/n）: ").strip().lower()
            if item == "y":
                show_secret_number(teki)
                continue  # アイテムを使ったら、一旦ループの先頭に戻す（次は can_use_item() が False になるのでここをスルーします）

        # アイテムを使わない（n）か、すでにアイテム使用済みの場合はこちらに進む
        guess = input("予想 > ").strip()

        # ===== ② 入力コマンドに足す（ヒント など）: ここに書く（import もここに） =====
        if len(guess) != digits or not guess.isdigit():
            print(f"{digits} 桁の数字で入力してね")
            continue

        tries += 1
        hit, blow = judge(secret, guess)
        print(f"  Hit={hit}  Blow={blow}")

        # インデントを下げて else の中に入れます
        if hit == digits:
            # ===== ③ 勝利時に足す（スコア・履歴 など）: ここに書く =====
            print(f"正解！ {tries} 回で当たり（答え {secret}）")
            break
