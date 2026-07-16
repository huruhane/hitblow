from .core import judge, make_secret
from .item import show_secret_number, can_use_item


def play(digits=3):
    secret = make_secret(digits) # 本来はプレイヤーが当てる相手の数字
    teki = make_secret(digits)   # アイテム用のダミーなど
    print(f"Hit & Blow（{digits} 桁・重複なし）")

    # ===== ① 開始時に足す（難易度・あいさつ など）: ここに書く =====
    from .enemy import select_enemy_mode

    # CPU戦の場合、自分で決めた数値を my_secret として受け取る
    my_secret = select_enemy_mode(digits)
    
    # 💡 CPU戦モードなら、CPUが当てる対象（プレイヤーの秘密の数）を自分で決めた数値にする
    if my_secret is not None:
        # 変数名がややこしいですが、現状の game.py の末尾で `cpu_turn(digits, secret)` に渡しているため、
        # ここで `secret` の中身をプレイヤーが自分で決めた数値に書き換えます。
        secret = my_secret

    tries = 0
    while True:
        # まだアイテムを使える状態なら、使うかどうかを尋ねる
        if can_use_item():
            item = input("アイテムを使いますか？（y/n）: ").strip().lower()
            if item == "y":
                show_secret_number(teki)
                continue

        # アイテムを使わない（n）か、すでにアイテム使用済みの場合はこちらに進む
        guess = input("予想 > ").strip()

        if len(guess) != digits or not guess.isdigit():
            print(f"{digits} 桁の数字で入力してね")
            continue

        tries += 1
        
        # 💡 注意: 現状のコードのままだと、プレイヤーも自分の決めた数字（secret）を当てるゲームになってしまいます。
        # もし「プレイヤーはCPUの数字（teki）を当てたい」場合は、ここの第1引数を teki に変更してください。
        hit, blow = judge(secret, guess) 
        print(f"  Hit={hit}  Blow={blow}")

        if hit == digits:
            # ===== ③ 勝利時に足す（スコア・履歴 など）: ここに書く =====
            print(f"正解！ {tries} 回で当たり（答え {secret}）")
            break

        # ===== ② 入力コマンドに足す（ヒント など）: ここに書く（import もここに） =====
        from .enemy import cpu_turn

        # CPUは、プレイヤーが自分で決めた数字（secret）を狙う
        if cpu_turn(digits, secret):
            break