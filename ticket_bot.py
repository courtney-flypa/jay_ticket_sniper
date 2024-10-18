import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException, StaleElementReferenceException
from PIL import Image
import pytesseract
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

    def select_first_available_ticket(self):
        try:
            print("開始選擇票種...")
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "zone.area-list")))
            print("區域列表已加載")

            available_tickets = self.driver.find_elements(By.CSS_SELECTOR, ".select_form_a a")
            print(f"找到 {len(available_tickets)} 個可選擇的票種")

            # 創建一個列表，存儲每個票種及其剩餘票數
            ticket_info = []
            for ticket in available_tickets:
                ticket_text = ticket.text
                remaining_tickets = int(''.join(filter(str.isdigit, ticket_text.split('剩餘')[-1])))
                if remaining_tickets > 0:
                    ticket_info.append((ticket, remaining_tickets))

            if ticket_info:
                # 選擇剩餘票數最多的票種
                best_ticket, max_remaining = max(ticket_info, key=lambda x: x[1])
                print(f"選擇票種: {best_ticket.text}，剩餘票數: {max_remaining}")
                self.click_ticket(best_ticket)
                return self.select_quantity(1)  # 選擇 1 張票
            else:
                print("沒有找到可用的票種")
                return False
        except Exception as e:
            print(f"選擇票種時發生錯誤: {e}")
            return False

    def click_ticket(self, ticket):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", ticket)
        time.sleep(5)

        for click_method in [ticket.click, lambda: self.driver.execute_script("arguments[0].click();", ticket), lambda: ActionChains(self.driver).move_to_element(ticket).click().perform()]:
            try:
                click_method()
                print("已點擊票種")
                time.sleep(10)
                return
            except Exception as e:
                print(f"點擊方法失敗: {e}")

    def select_quantity(self, desired_quantity=1):
        try:
            select_element = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[id^='TicketForm_ticketPrice_']"))
            )
            print("找到張數選擇下拉框")
            
            select = Select(select_element)
            options = select.options
            print(f"可選擇的張數選項: {[option.text for option in options]}")
            
            # 尋找最接近 desired_quantity 的選項
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
                
                # 使用 ddddocr 識別驗證碼
                ocr = ddddocr.DdddOcr()
                with open("captcha.png", "rb") as f:
                    img_bytes = f.read()
                captcha_text = ocr.classification(img_bytes)
                print(f"識別到的驗證碼: {captcha_text}")
                
                captcha_input = self.driver.find_element(By.ID, "TicketForm_verifyCode")
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)
                print(f"已輸入驗證碼: {captcha_text}")
                
                # 輸入驗證碼後，檢查是否出現錯誤提示
                error_message = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'error-message')]")
                if not error_message:
                    print(f"驗證碼輸入成功，嘗試次數：{attempt + 1}")
                    return True
                else:
                    print(f"驗證碼輸入錯誤，重試中... (嘗試次數：{attempt + 1})")
                    # 重新加載驗證碼圖片
                    self.driver.find_element(By.ID, "TicketForm_verifyCode-image").click()
                    time.sleep(2)
            except Exception as e:
                print(f"輸入驗證碼時發生錯誤: {e}")
        
        print("驗證碼輸入失敗，已達到最大嘗試次數")
        return False

    def agree_terms(self):
        return self.wait_and_click((By.ID, "TicketForm_agree"))

    def confirm_ticket_quantity(self):
        return self.wait_and_click((By.XPATH, "//button[@type='submit' and contains(@class, 'btn-primary') and contains(text(), '確認張數')]"))

    def agree_program_rules(self):
        try:
            # 找到按鈕元素
            button = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "submitButton"))
            )
            
            # 滾動到按鈕元素
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            
            # 等待一下，確保頁面滾動完成
            time.sleep(2)
            
            # 再次等待按鈕可點擊
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "submitButton"))
            )
            
            # 使用 JavaScript 點擊按鈕
            self.driver.execute_script("arguments[0].click();", button)
            
            # 處理可能出現的警告框
            try:
                alert = Alert(self.driver)
                alert_text = alert.text
                print(f"警告框內容: {alert_text}")
                alert.accept()
                return False  # 返回 False 表示需要重新選擇票數
            except:
                pass  # 如果沒有警告框，繼續執行
            
            print("已點擊同意節目規則按鈕")
            return True
        except Exception as e:
            print(f"同意節目規則時發生錯誤: {e}")
            self.save_error_screenshot()
            return False

    def click_buy_ticket_button(self):
        try:
            # 嘗試找到所有可能的"立即購票"按鈕
            buttons = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/activity/game/')]/div[text()='立即購票']")
            
            if buttons:
                # 如果找到多個按鈕，選擇第一個可見的
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
            # 嘗試找到所有的"立即訂購"按鈕
            buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), '立即訂購')]")
            
            if buttons:
                # 選擇第一個"立即訂購"按鈕
                first_button = buttons[0]
                if first_button.is_displayed():
                    first_button.click()
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
            ("選擇票種", self.select_first_available_ticket),
            ("輸入驗證碼", self.input_captcha),
            ("同意條款", self.agree_terms),
            ("確認張數", self.confirm_ticket_quantity),
            ("同意節目規則", self.agree_program_rules),
        ]

        for step_name, action in steps:
            print(f"開始執行{step_name}...")
            if callable(action):
                success = action()
            else:
                success = self.wait_and_click(action)
            
            if success:
                print(f"成功執行{step_name}")
                time.sleep(10)  # 增加等待時間到 10 秒
            else:
                if step_name == "同意節目規則" and not success:
                    print("需要重新選擇票數")
                    # 返回選擇票種步驟
                    self.driver.back()
                    time.sleep(5)
                    if not self.select_first_available_ticket():
                        print("重新選擇票種失敗")
                        return False
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
