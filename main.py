from src.bot import TicketBot

def main():
    bot = TicketBot()
    if bot.connect_to_browser():
        if bot.execute_ticket_purchase():
            print("購票流程執行完成")
        else:
            print("購票流程執行失敗")
    
    input("按 Enter 鍵退出程序...")

if __name__ == "__main__":
    main()
