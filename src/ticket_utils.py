from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time

def select_best_ticket(driver):
    try:
        print("開始選擇票種...")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "zone.area-list")))
        available_tickets = driver.find_elements(By.CSS_SELECTOR, ".select_form_a a")
        print(f"找到 {len(available_tickets)} 個可選擇的票種")

        ticket_info = []
        for ticket in available_tickets:
            ticket_text = ticket.text
            remaining = ''.join(filter(str.isdigit, ticket_text.split('剩餘')[-1]))
            if remaining:
                remaining = int(remaining)
                if remaining > 0:
                    ticket_info.append((ticket, remaining))

        if ticket_info:
            best_ticket, max_remaining = max(ticket_info, key=lambda x: x[1])
            ticket_name = best_ticket.text.split('剩餘')[0].strip()
            if max_remaining > 0:
                print(f"選擇票種: {ticket_name} (剩餘票數: {max_remaining})")
            else:
                print(f"選擇票種: {ticket_name}")
            return best_ticket
        else:
            print("沒有找到可用的票種")
            return None
    except Exception as e:
        print(f"選擇票種時發生錯誤: {e}")
        return None

def click_ticket(driver, ticket):
    driver.execute_script("arguments[0].scrollIntoView(true);", ticket)
    # time.sleep(5)

    click_methods = [
        ticket.click,
        lambda: driver.execute_script("arguments[0].click();", ticket),
        lambda: ActionChains(driver).move_to_element(ticket).click().perform()
    ]

    for click_method in click_methods:
        try:
            click_method()
            print("已點擊票種")
            # time.sleep(10)
            return True
        except Exception as e:
            print(f"點擊方法失敗: {e}")
    
    return False

def select_quantity(driver, desired_quantity=1, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"嘗試選擇 {desired_quantity} 張票... (嘗試次數: {attempt + 1})")
            
            # 等待選擇框出現，增加等待時間
            select_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[id^='TicketForm_ticketPrice_']"))
            )
            print("找到票數選擇框")
            
            # 等待選擇框可交互
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "select[id^='TicketForm_ticketPrice_']"))
            )
            
            # 獲取所有可選擇的選項
            select = Select(select_element)
            options = select.options
            print(f"可選擇的票數選項: {[option.text for option in options]}")
            
            # 選擇最接近所需數量的選項
            closest_option = min(options, key=lambda x: abs(int(x.get_attribute("value")) - desired_quantity))
            print(f"選擇最接近的選項: {closest_option.text}")
            
            # 選擇票數
            select.select_by_value(closest_option.get_attribute("value"))
            print(f"已選擇票數: {closest_option.text}")
            
            # 等待選擇生效
            time.sleep(5)
            
            # 驗證選擇是否成功
            selected_option = select.first_selected_option
            if selected_option.text == closest_option.text:
                print("票數選擇成功確認")
                return True
            else:
                print(f"票數選擇可能未生效，當前選中: {selected_option.text}")
                
        except (TimeoutException, StaleElementReferenceException) as e:
            print(f"選擇張數時發生錯誤: {e}")
            if attempt < max_retries - 1:
                print("重試中...")
                time.sleep(2)
                driver.refresh()
            else:
                print(f"當前頁面 URL: {driver.current_url}")
                print(f"頁面源碼: {driver.page_source}")
                return False

    print("選擇張數失敗，已達到最大重試次數")
    return False
