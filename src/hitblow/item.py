global can_use
can_use = True


def show_secret_number(secret):
    """秘密の数字を1桁ランダムに表示する（アイテム使用時）。"""
    import random  # 衝突を避けるため関数内でインポート

    # secret が数値の場合は文字列に変換して、文字の位置を扱えるようにする
    secret_str = str(secret)

    # 0 から「桁数-1」までのインデックスをランダムに1つ選ぶ
    idx = random.randint(0, len(secret_str) - 1)

    # 選んだ桁の数字を取得
    selected_digit = secret_str[idx]

    # プレイヤーに分かりやすいよう「○番目の数字」として表示 (1始まりにするため +1)
    print(f"ヒント: 数字の一つは「 {selected_digit} 」です。")

    global can_use
    can_use = False  # アイテムは1回だけ使えるようにする


def can_use_item():
    """アイテムが使えるかどうかを判定する。"""
    global can_use
    return can_use
