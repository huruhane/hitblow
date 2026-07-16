# enemy.py
import random
from .core import judge

is_enemy_mode = False
cpu_used_guesses = set()


def select_enemy_mode(digits):
    """① 開始時に呼び出す関数: CPU戦にするか選択し、自分の数値を決める"""
    global is_enemy_mode
    choice = input("CPU戦にしますか？（y/n）: ").strip().lower()
    
    if choice == "y":
        is_enemy_mode = True
        print("⚔️ CPU戦モードが有効になりました！交互に交代して入力します。")
        
        # プレイヤーが自分の秘密の数字（CPUに当てさせる数）を決める
        while True:
            my_secret = input(f"CPUに当てさせるあなたの秘密の数字（{digits}桁・重複なし）を入力してください: ").strip()
            # 簡易バリデーション（桁数チェックと数字チェック）
            if len(my_secret) == digits and my_secret.isdigit() and len(set(my_secret)) == digits:
                print(f"あなたの秘密の数字を「{my_secret}」に設定しました。（画面をスクロールして見えなくするか、友達に見られないように注意してください！）\n")
                return my_secret
            print(f"エラー: {digits}桁の重複のない数字を正しく入力してください。")
    else:
        is_enemy_mode = False
        return None


def cpu_turn(digits, secret):
    """② 入力コマンドの後に呼び出す関数: CPUのターンを処理する"""
    global is_enemy_mode, cpu_used_guesses

    if not is_enemy_mode:
        return False

    print("\n[CPUのターン]")

    # 重複のない数字をランダムに生成
    while True:
        nums = list("0123456789")
        random.shuffle(nums)
        cpu_guess = "".join(nums[:digits])

        if cpu_guess not in cpu_used_guesses:
            cpu_used_guesses.add(cpu_guess)
            break

    print(f"CPUの予想 > {cpu_guess}")

    # CPUはプレイヤーが決めた数字（secret）を推理する
    cpu_hit, cpu_blow = judge(secret, cpu_guess)
    print(f"  Hit={cpu_hit}  Blow={cpu_blow}")

    if cpu_hit == digits:
        print(f"💀 残念！CPUが先に正解してしまいました…（答え {secret}）")
        return True

    print("\n[あなたのターン]")
    return False
