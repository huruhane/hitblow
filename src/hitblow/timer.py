# src/hitblow/timer.py
import time

# ゲーム全体の開始時間を保持する変数
_start_time = 0.0


def start_timer():
    """① 開始時に呼び出して、計測をスタートする関数"""
    global _start_time
    _start_time = time.time()


def show_clear_time(tries, cpu_secret, is_victory=True):
    """③ 勝利時（または決着時）に呼び出して、経過時間を計算・表示する関数"""
    global _start_time
    if _start_time == 0.0:
        print("⚠️ タイマーが開始されていません。")
        return

    end_time = time.time()
    clear_time = end_time - _start_time

    # 分と秒に変換
    minutes = int(clear_time // 60)
    seconds = int(clear_time % 60)

    print("\n========================================")
    if is_victory:
        print(f"🎉 🎉 正解！ あなたの勝利です！ 🎉 🎉")
        print(f"📊 かかったターン数: {tries} 回（答え: {cpu_secret}）")
        if minutes > 0:
            print(f"⏱️ クリア時間: {minutes} 分 {seconds} 秒")
        else:
            print(f"⏱️ クリア時間: {seconds} 秒")
    else:
        # CPUに負けた場合など
        print(f"📊 かかったターン数: {tries} 回 ")
        if minutes > 0:
            print(f"⏱️ 決着までの時間: {minutes} 分 {seconds} 秒")
        else:
            print(f"⏱️ 決着までの時間: {seconds} 秒")
    print("========================================\n")
