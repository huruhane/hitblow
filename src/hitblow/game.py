from .core import judge, make_secret
from .item import show_secret_number, can_use_item


def play(digits=3):
    # 1. 最初にお互いの数字の「デフォルト（初期値）」を決める
    cpu_secret = make_secret(digits)  # プレイヤーが当てる相手の数字
    my_secret = make_secret(digits)   # CPUが当てる自分の数字（通常時はランダム）
    
    # アイテム用の数字（通常時は cpu_secret と同じにしておく）
    teki = cpu_secret
    
    print(f"Hit & Blow（{digits} 桁・重複なし）")

    # ===== ① 開始時に足す（難いに度・あいさつ など）: ここに書く =====
    from .enemy import select_enemy_mode
    from .timer import start_timer
    
    # CPU戦の場合、自分で決めた数値を入力する
    user_custom_secret = select_enemy_mode(digits)
    
    # 💡 CPU戦モードなら、CPUが当てる対象（my_secret）を入力された数値に差し替える
    if user_custom_secret is not None:
        my_secret = user_custom_secret

    start_timer()
    
    tries = 0
    while True:
        # まだアイテムを使える状態なら、使うかどうかを尋ねる
        if can_use_item():
            # --- ここから修正部分 ---
            item_loop = True
            while item_loop:
                # yかnを強制するようにプロンプトを少し変更
                item = input("アイテムを使いますか？【相手の数値が一つわかる】（y/n）: ").strip().lower()

                if item == "y":
                    show_secret_number(teki)
                    # continue すると、can_use_item() がFalseになり、
                    # 下の guess の入力に進むので、アイテムループだけを抜ける
                    item_loop = False
                    # さらに continue して while True を先頭に戻す
                    # (これでcan_use_itemがFalseと判定され、下の予想に進む)
                    continue 

                elif item == "n" or item == "": # "" はEnterのみの場合
                    # アイテムを使わない。guessの入力へ進む。
                    item_loop = False
                    # そのままこのブロックを抜けて、下の予想に進む
                else:
                    # y, n, "" 以外の場合は再度ループ
                    print("エラー: 'y' または 'n' を入力してください。")
            # --- ここまで修正部分 ---

        # アイテムを使わない（n）か、すでにアイテム使用済みの場合はこちらに進む
        # (item="y" の後の continue によって、ここに到達しないケースもある)
        # もしアイテムを使った直後に続けて予想させたい場合は、
        # ここに到達できるようにitemループを制御します。
        # 今の play関数の構造上、アイテム使用後に continue すると、
        # `tries += 1` などが一度飛ばされます。

        guess = input("予想 > ").strip()

        if len(guess) != digits or not guess.isdigit():
            print(f"{digits} 桁の数字で入力してね")
            continue

        tries += 1
        
        # 💡 【プレイヤーの判定】
        # プレイヤーは、CPUの数字（cpu_secret）を推理して当てにいきます
        hit, blow = judge(cpu_secret, guess) 
        print(f"  Hit={hit}  Blow={blow}")

        if hit == digits:
            # ===== ③ 勝利時に足す（スコア・履歴 など）: ここに書く =====
            from .timer import show_clear_time
            show_clear_time(tries, cpu_secret, is_victory=True)
            break

        # ===== ② 入力コマンドに足す（ヒント など）: ここに書く（import もここに） =====
        from .enemy import cpu_turn

        # 💡 【CPUのターン】
        # CPUは、プレイヤーの数字（my_secret）を推理して当てにいきます
        if cpu_turn(digits, my_secret):
            # CPUが正解してしまった場合
            from .timer import show_clear_time
            show_clear_time(tries, cpu_secret, is_victory=False)
            break
