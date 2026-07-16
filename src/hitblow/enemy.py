# enemy.py
import random
import itertools
from .core import judge

is_enemy_mode = False
cpu_candidates = []


def select_enemy_mode(digits):
    """① 開始時に呼び出す関数: CPU戦にするか選択し、候補リストを初期化する"""
    global is_enemy_mode, cpu_candidates
    choice = input("CPU戦にしますか？（y/n）: ").strip().lower()
    
    if choice == "y":
        is_enemy_mode = True
        print("⚔️ CPU戦モードが有効になりました！交互に交代して入力します。")
        
        # 0〜9の数字から重複なしでdigits桁の全組み合わせを作成
        all_perms = itertools.permutations("0123456789", digits)
        cpu_candidates = ["".join(p) for p in all_perms]
        
        # プレイヤーが自分の秘密の数字を決める
        while True:
            my_secret = input(f"CPUに当てさせるあなたの秘密の数字（{digits}桁・重複なし）を入力してください: ").strip()
            if len(my_secret) == digits and my_secret.isdigit() and len(set(my_secret)) == digits:
                print(f"あなたの秘密の数字を「{my_secret}」に設定しました。\n")
                return my_secret
            print(f"エラー: {digits}桁の重複のない数字を正しく入力してください。")
    else:
        is_enemy_mode = False
        return None


def cpu_turn(digits, secret):
    """② 入力コマンドの後に呼び出す関数: CPUが推理して次の手を打つ"""
    global is_enemy_mode, cpu_candidates

    if not is_enemy_mode:
        return False

    print("\n[CPUのターン]")
    
    if not cpu_candidates:
        print("🤔 CPU「あれ？あなたの数字に矛盾があるか、私の推論がおかしいです…」")
        return False

    # 1. 候補リストの中からランダムに1つ予想を選ぶ（毎回違う手になります）
    cpu_guess = random.choice(cpu_candidates)
    
    # 💡 「残り候補数」の表示をなくし、すっきりした出力に変更しました
    print(f"CPUの予想 > {cpu_guess}")

    # 2. プレイヤーの数字に対して判定
    cpu_hit, cpu_blow = judge(secret, cpu_guess)
    print(f"  Hit={cpu_hit}  Blow={cpu_blow}")

    # 3. 正解判定
    if cpu_hit == digits:
        print(f"💀 残念！CPUが先に正解してしまいました…（答え {secret}）")
        return True

    # 4. フィルタリング（推理）
    next_candidates = []
    for cand in cpu_candidates:
        h, b = judge(cand, cpu_guess)
        if h == cpu_hit and b == cpu_blow:
            next_candidates.append(cand)
            
    cpu_candidates = next_candidates

    print("\n[あなたのターン]")
    return False