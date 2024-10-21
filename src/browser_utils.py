from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def wait_and_click(driver, locator, timeout=20):
    try:
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(2)  # 等待滾動完成
        element.click()
        return True
    except Exception as e:
        print(f"點擊元素時發生錯誤: {e}")
        return False

def save_error_screenshot(driver):
    try:
        driver.save_screenshot("error_screenshot.png")
        print("已保存錯誤截圖")
    except Exception as se:
        print(f"保存截圖失敗: {se}")
