from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time

def wait_and_click(driver, locator, timeout=20, retries=3):
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(1)  # 等待滾動完成
            
            # 嘗試不同的點擊方法
            click_methods = [
                lambda: element.click(),
                lambda: driver.execute_script("arguments[0].click();", element),
                lambda: ActionChains(driver).move_to_element(element).click().perform()
            ]
            
            for click_method in click_methods:
                try:
                    click_method()
                    return True
                except ElementClickInterceptedException:
                    print(f"點擊方法失敗，嘗試下一種方法...")
                    continue
            
            print(f"所有點擊方法都失敗，重試中... (嘗試次數：{attempt + 1})")
        except (TimeoutException, ElementClickInterceptedException) as e:
            print(f"等待或點擊元素時發生錯誤: {e}")
            if attempt < retries - 1:
                print(f"重試中... (嘗試次數：{attempt + 1})")
                time.sleep(2)

def save_error_screenshot(driver):
    try:
        driver.save_screenshot("error_screenshot.png")
        print("已保存錯誤截圖")
    except Exception as se:
        print(f"保存截圖失敗: {se}")
