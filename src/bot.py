import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
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
        # time.sleep(5)  # 等待連接穩定

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
            
            if step_name == "同意節目規則":
                print("等待 2 秒...")
                time.sleep(2)
            
            success = action()
            
            if success:
                print(f"成功執行{step_name}")
                # time.sleep(10)
            else:
                if step_name == "同意節目規則" and not success:
                    print("需要重新選擇票數")
                    self.driver.back()
                    # time.sleep(5)
                    continue
                print(f"無法執行{step_name}")
                return False
        
        return True

    def click_buy_ticket_button(self):
        return wait_and_click(self.driver, (By.XPATH, "//a[contains(@href, '/activity/game/')]/div[text()='立即購票']"))

    def click_first_buy_now_button(self):
        return wait_and_click(self.driver, (By.XPATH, "//button[contains(text(), '立即訂購')]"))

    def agree_program_rules(self, max_retries=3, retry_delay=2):
        for attempt in range(max_retries):
            try:
                # 等待按鈕出現
                button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "submitButton"))
                )
                
                # 滾動到按鈕位置
                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(1)  # 等待滾動完成
                
                # 等待按鈕可點擊
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "submitButton"))
                )
                
                # 嘗試不同的點擊方法
                click_methods = [
                    lambda: button.click(),
                    lambda: self.driver.execute_script("arguments[0].click();", button),
                    lambda: ActionChains(self.driver).move_to_element(button).click().perform()
                ]
                
                for click_method in click_methods:
                    try:
                        click_method()
                        print("已點擊同意節目規則按鈕")
                        break
                    except ElementClickInterceptedException:
                        print(f"點擊方法失敗，嘗試下一種方法...")
                        continue
                
                # 檢查是否有警告框
                try:
                    alert = self.driver.switch_to.alert
                    print(f"警告框內容: {alert.text}")
                    alert.accept()
                    return False  # 需要重新選擇票數
                except:
                    pass
                
                return True
            except (TimeoutException, NoSuchElementException) as e:
                print(f"找不到同意節目規則按鈕或按鈕不可點擊，重試中... (嘗試次數：{attempt + 1})")
            
            # 如果不是最後一次嘗試，則等待後重試
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                self.driver.refresh()  # 刷新頁面
        
        print("無法找到或點擊同意節目規則按鈕")
        save_error_screenshot(self.driver)
        return False
