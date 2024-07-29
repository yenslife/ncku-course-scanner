import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from rich import print
import chromedriver_autoinstaller
from pyvirtualdisplay import Display # 用來在沒有 GUI 的環境下執行 Selenium，會需要安裝 xvfb，所以只能在 Linux 上執行

from query import query_name, query_id, query_dept, limit_dept

# 若在 Linux 上執行，需要使用 pyvirtualdisplay 來模擬 GUI 環境，不用的話可以註解掉
display = Display(visible=0, size=(800, 800)) 
display.start() 

url = "https://course.ncku.edu.tw/index.php?c=qry_all"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

# 找到所有導航按鈕
nav_menu = soup.find_all('li', class_='btn_dept')

# 使用 Selenium 設定 webdriver
chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path
driver = webdriver.Chrome()
driver.get(url)

course_list = []
for course in nav_menu:
    course_list.append(course.text)
course_list = list(set(course_list))

if limit_dept:
    course_list = [course for course in course_list if any(dept in course for dept in query_dept)]

# 點擊每個按鈕
data = []  # key 為課程，value 為內容
for index, course in enumerate(course_list):
    # 使用 XPath 查找按鈕
    # button_xpath = f"(//li[@class='btn_dept'])[{index + 1}]"
    button_xpath = f"//li[@class='btn_dept'][contains(text(), '{course}')]"
    button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, button_xpath)))

    # 模擬滑鼠點擊按鈕
    driver.execute_script("arguments[0].click();", button)
    
    # 等待頁面內容加載完畢
    time.sleep(2)

    # 取得目前頁面的 HTML
    page_source = driver.find_element(By.XPATH, '/html').get_attribute('outerHTML')
        
    # 可以進一步解析該頁面的內容，例如找到所有課程列表
    soup = BeautifulSoup(page_source, 'lxml')
    # 找到表格
    table = soup.find('table', {'id': 'A9-table'})

    # 找到所有行
    rows = table.find_all('tr')
    for row in rows[1:]:
        columns = row.find_all('td')
        course_data = {}
        course_data['系所名稱'] = columns[0].text.strip()
        course_data['系號-序號'] = columns[1].text.strip()
        course_data['年級'] = columns[2].text.strip()
        course_data['類別'] = columns[3].text.strip()
        course_data['科目名稱'] = columns[4].text.strip().split(' ')[0] # 把科目名稱的後面的東西去掉
        course_data['學分'] = columns[5].text.strip()
        course_data['教師姓名'] = columns[6].text.strip()
        course_data['已選課人數/餘額'] = columns[7].text.strip()
        course_data['時間/教室'] = columns[8].text.strip()
        # course_data['課綱/Moodle'] = columns[9].text.strip() # 用不到
        # 判斷是否有餘額，餘額的 format 為 0/210 代表有餘額，如果沒有餘額會顯示 xx/額滿，所以可以透過 '/' 來判斷是否有餘額
        course_data['是否有餘額'] = '額' not in course_data['已選課人數/餘額']
        data.append(course_data)
    # print(f"正在掃描: {nav_menu[index].text}")
    print(f"已掃描: {course}")
    # 返回主頁，再次進行下一個導航按鈕點擊
    driver.back()
    # 等待頁面加載回主頁完整
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//li[@class="btn_dept"]')))
    
# 關閉瀏覽器
driver.quit()

# 修改 query.py 選擇你想要查詢的課程序號，檢查有沒有餘額
query_result = []
for course in data:
    for id in query_id:
        if id in course['系號-序號']:
            query_result.append(course)
    for name in query_name:
        if name in course['科目名稱']:
            query_result.append(course)

with open("query_result.json", "w", encoding="utf-8") as f:
    json.dump(query_result, f, ensure_ascii=False, indent=4)

def markdown_table_format(data):
    if len(data) == 0:
        return "沒有找到課程"
    table = "|"
    for key in data[0].keys():
        table += f"{key}|"
    table += "\n|"
    for key in data[0].keys():
        table += "---|"
    table += "\n"
    for course in data:
        for value in course.values():
            v = value.replace('\n', ' ') if type(value) == str else value
            v = "✅" if v == True else "😭" if v == False else v
            table += f"{v}|"
        table += "\n"
    return table

print(markdown_table_format(query_result))

with open("query_result.txt", "w", encoding="utf-8") as f:
    f.write(markdown_table_format(query_result))

# import random
# import email.message
# import smtplib
# import os

# GOOGLE_CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']
# EMAIL = os.environ['EMAIL']
# TO_EMAIL = os.environ['TO_EMAIL']

# msg=email.message.EmailMessage()
# msg["From"] = EMAIL
# msg["To"]= TO_EMAIL #input("請輸入email: ")

# verify_code = ''.join(map(str, random.sample(range(0, 9), 6)))
# print("生成的驗證碼：", verify_code)

# msg["Subject"]=f"驗證碼為:{verify_code}"

# server=smtplib.SMTP_SSL("smtp.gmail.com", 465)
# server.login(EMAIL, GOOGLE_CLIENT_SECRET)
# server.send_message(msg)
# server.close()
