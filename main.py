from src.bot import TicketBot
import datetime
import time
import pytz

def wait_until_start_time(target_time):
    taipei_tz = pytz.timezone('Asia/Taipei')
    while True:
        current_time = datetime.datetime.now(taipei_tz)
        if current_time >= target_time:
            print(f"目標時間到達，開始執行程序 (當前時間: {current_time.strftime('%Y-%m-%d %H:%M:%S')})")
            break
        time_left = (target_time - current_time).total_seconds()
        print(f"距離程序開始還有 {time_left:.0f} 秒 (當前時間: {current_time.strftime('%Y-%m-%d %H:%M:%S')})")
        time.sleep(1)  # 每秒更新一次

def main():
    taipei_tz = pytz.timezone('Asia/Taipei')
    # 設定目標時間為 10/23 12:00 PM （UTC+8）
    target_time = taipei_tz.localize(datetime.datetime(2024, 10, 23, 12, 0, 0))
    
    print(f"程序將在 {target_time.strftime('%Y-%m-%d %H:%M:%S')} 開始執行")
    wait_until_start_time(target_time)

    bot = TicketBot()
    if bot.connect_to_browser():
        if bot.execute_ticket_purchase():
            print("購票流程執行完成")
        else:
            print("購票流程執行失敗")
    
    input("按 Enter 鍵退出程序...")

if __name__ == "__main__":
    main()
