from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ddddocr
import time

def input_captcha(driver, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            captcha_img = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "TicketForm_verifyCode-image"))
            )
            captcha_img.screenshot("captcha.png")
            
            ocr = ddddocr.DdddOcr()
            with open("captcha.png", "rb") as f:
                captcha_text = ocr.classification(f.read())
            print(f"識別到的驗證碼: {captcha_text}")
            
            captcha_input = driver.find_element(By.ID, "TicketForm_verifyCode")
            captcha_input.clear()
            captcha_input.send_keys(captcha_text)
            
            if not driver.find_elements(By.XPATH, "//div[contains(@class, 'error-message')]"):
                print(f"驗證碼輸入成功，嘗試次數：{attempt + 1}")
                return True
            else:
                print(f"��證碼輸入錯誤，重試中... (嘗試次數：{attempt + 1})")
                driver.find_element(By.ID, "TicketForm_verifyCode-image").click()
                # time.sleep(2)
        except Exception as e:
            print(f"輸入驗證碼時發生錯誤: {e}")
    
    print("驗證碼輸入失敗，已達到最大嘗試次數")
    return False
