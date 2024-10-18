import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import ddddocr
from selenium.webdriver.common.alert import Alert

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
        except WebDriverException as e:
            print(f"獲取頁面信息時發生錯誤: {e}")
            return False

    def wait_and_click(self, locator, timeout=20):
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(2)  # 等待滾動完成
            element.click()
            return True
        except Exception as e:
            print(f"點擊元素時發生錯誤: {e}")
            return False

    def select_best_ticket(self):
        try:
            print("開始選擇票種...")
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "zone.area-list")))
            available_tickets = self.driver.find_elements(By.CSS_SELECTOR, ".select_form_a a")
            print(f"找到 {len(available_tickets)} 個可選擇的票種")

            ticket_info = [(ticket, int(''.join(filter(str.isdigit, ticket.text.split('剩餘')[-1]))))
                           for ticket in available_tickets if int(''.join(filter(str.isdigit, ticket.text.split('剩餘')[-1]))) > 0]

            if ticket_info:
                best_ticket, max_remaining = max(ticket_info, key=lambda x: x[1])
                print(f"選擇票種: {best_ticket.text}，剩餘票數: {max_remaining}")
                return best_ticket
            else:
                print("沒有找到可用的票種")
                return None
        except Exception as e:
            print(f"選擇票種時發生錯誤: {e}")
            return None

    def click_ticket(self, ticket):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", ticket)
        time.sleep(5)

        click_methods = [
            ticket.click,
            lambda: self.driver.execute_script("arguments[0].click();", ticket),
            lambda: ActionChains(self.driver).move_to_element(ticket).click().perform()
        ]

        for click_method in click_methods:
            try:
                click_method()
                print("已點擊票種")
                time.sleep(10)
                return True
            except Exception as e:
                print(f"點擊方法失敗: {e}")
        
        return False

    def select_quantity(self, desired_quantity=1):
        try:
            select_element = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[id^='TicketForm_ticketPrice_']"))
            )
            select = Select(select_element)
            options = select.options
            closest_option = min(options, key=lambda x: abs(int(x.get_attribute("value")) - desired_quantity))
            select.select_by_value(closest_option.get_attribute("value"))
            print(f"選擇張數: {closest_option.text}")
            time.sleep(5)  # 等待選擇生效
            return True
        except Exception as e:
            print(f"選擇張數時發生錯誤: {e}")
            self.save_error_screenshot()
            return False

    def save_error_screenshot(self):
        try:
            self.driver.save_screenshot("error_screenshot.png")
            print("已保存錯誤截圖")
        except Exception as se:
            print(f"保存截圖失敗: {se}")

    def input_captcha(self, max_attempts=3):
        for attempt in range(max_attempts):
            try:
                captcha_img = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "TicketForm_verifyCode-image"))
                )
                captcha_img.screenshot("captcha.png")
                
                ocr = ddddocr.DdddOcr()
                with open("captcha.png", "rb") as f:
                    captcha_text = ocr.classification(f.read())
                print(f"識別到的驗證碼: {captcha_text}")
                
                captcha_input = self.driver.find_element(By.ID, "TicketForm_verifyCode")
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                
                if not self.driver.find_elements(By.XPATH, "//div[contains(@class, 'error-message')]"):
                    print(f"驗證碼輸入成功，嘗試次數：{attempt + 1}")
                    return True
                else:
                    print(f"驗證碼輸入錯誤，重試中... (嘗試次數：{attempt + 1})")
                    self.driver.find_element(By.ID, "TicketForm_verifyCode-image").click()
                    time.sleep(2)
            except Exception as e:
                print(f"輸入驗證碼時發生錯誤: {e}")
        
        print("驗證碼輸入失敗，已達到最大嘗試次數")
        return False

    def agree_program_rules(self):
        try:
            button = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "submitButton"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(2)
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "submitButton"))
            )
            self.driver.execute_script("arguments[0].click();", button)
            
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
            self.save_error_screenshot()
            return False

    def click_buy_ticket_button(self):
        try:
            buttons = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/activity/game/')]/div[text()='立即購票']")
            for button in buttons:
                if button.is_displayed():
                    button.click()
                    print("成功點擊立即購票按鈕")
                    return True
            print("沒有找到可見的立即購票按鈕")
            return False
        except Exception as e:
            print(f"點擊立即購票按鈕時發生錯誤: {e}")
            return False

    def click_first_buy_now_button(self):
        try:
            buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '立即訂購')]")
            if buttons and buttons[0].is_displayed():
                buttons[0].click()
                print("成功點擊第一個立即訂購按鈕")
                return True
            print("沒有找到可見的立即訂購按鈕")
            return False
        except Exception as e:
            print(f"點擊立即訂購按鈕時發生錯誤: {e}")
            return False

    def execute_ticket_purchase(self):
        steps = [
            ("立即購票", self.click_buy_ticket_button),
            ("立即訂購", self.click_first_buy_now_button),
            ("選擇票種", lambda: self.click_ticket(self.select_best_ticket())),
            ("選擇張數", lambda: self.select_quantity(1)),
            ("輸入驗證碼", self.input_captcha),
            ("同意條款", lambda: self.wait_and_click((By.ID, "TicketForm_agree"))),
            ("確認張數", lambda: self.wait_and_click((By.XPATH, "//button[@type='submit' and contains(@class, 'btn-primary') and contains(text(), '確認張數')]"))),
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
