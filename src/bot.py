import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .browser_utils import wait_and_click, save_error_screenshot
from .ticket_utils import select_best_ticket, click_ticket, select_quantity
from .captcha_utils import input_captcha

class TicketBot:
    def __init__(self, debug_port=9527):
        self.options = Options()
        self.options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        self.driver = None

    def connect_to_browser(self):
        print("嘗試連接到 Chrome 瀏覽器...")
        self.driver = webdriver.Chrome(options=self.options)
        time.sleep(5)  # 等待連接穩定

        try:
            print(f"當前 URL: {self.driver.current_url}")
            print(f"當前頁面標題: {self.driver.title}")
            print("成功連接到 Chrome 瀏覽器")
            return True
        except Exception as e:
            print(f"獲取頁面信息時發生錯誤: {e}")
            return False

    def execute_ticket_purchase(self):
        steps = [
            ("立即購票", self.click_buy_ticket_button),
            ("立即訂購", self.click_first_buy_now_button),
            ("選擇票種", lambda: click_ticket(self.driver, select_best_ticket(self.driver))),
            ("選擇張數", lambda: select_quantity(self.driver, 1)),
            ("輸入驗證碼", lambda: input_captcha(self.driver)),
            ("同意條款", lambda: wait_and_click(self.driver, (By.ID, "TicketForm_agree"))),
            ("確認張數", lambda: wait_and_click(self.driver, (By.XPATH, "//button[@type='submit' and contains(@class, 'btn-primary') and contains(text(), '確認張數')]"))),
            ("同意節目規則", self.agree_program_rules),
        ]

        for step_name, action in steps:
            print(f"開始執行{step_name}...")
            success = action()
            
            if success:
                print(f"成功執行{step_name}")
                time.sleep(10)
            else:
                if step_name == "同意節目規則" and not success:
                    print("需要重新選擇票數")
                    self.driver.back()
                    time.sleep(5)
                    continue
                print(f"無法執行{step_name}")
                return False
        
        return True

    def click_buy_ticket_button(self):
        return wait_and_click(self.driver, (By.XPATH, "//a[contains(@href, '/activity/game/')]/div[text()='立即購票']"))

    def click_first_buy_now_button(self):
        return wait_and_click(self.driver, (By.XPATH, "//button[contains(text(), '立即訂購')]"))

    def agree_program_rules(self):
        try:
            button = wait_and_click(self.driver, (By.ID, "submitButton"))
            if not button:
                return False

            try:
                alert = Alert(self.driver)
                print(f"警告框內容: {alert.text}")
                alert.accept()
                return False  # 需要重新選擇票數
            except:
                pass
            
            print("已點擊同意節目規則按鈕")
            return True
        except Exception as e:
            print(f"同意節目規則時發生錯誤: {e}")
            save_error_screenshot(self.driver)
            return False
