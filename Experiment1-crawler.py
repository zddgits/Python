import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import re
import pandas as pd
import time


# 获得滑块验证的滑动轨迹
def get_track(distance):
    track = []
    current = 0
    mid = distance * 3 / 4
    t = random.randint(16, 24) / 10
    v = 0
    while current < distance:
        if current < mid:
            a = 2
        else:
            a = -3
        v0 = v
        v = v0 + a * t
        move = v0 * t + 1 / 2 * a * t * t
        current += move
        track.append(round(move))
    return track

# 获取数据
def extract_data(html_code):
    # 目标数据的正则表达式
    html_code = html_code.replace('<br>', '')
    html_code = html_code.replace('</b>', '')
    html_code = html_code.replace('<b>', '')
    html_code = html_code.replace('<p>', '')
    html_code = html_code.replace('</p>', '')
    p_job_name = '<h1 title="(.*?)">'

    p_job_msg = '<div class="bmsg job_msg inbox">(.*?)<div class="mt10">'

    # 利用findall()函数提取目标数据
    job_name = re.findall(p_job_name, html_code, re.S)
    job_msg = re.findall(p_job_msg, html_code, re.S)

    # 将几个目标数据列表转换为一个字典
    data_dt = {}
    if len(job_name) != 0 and len(p_job_msg) != 0:
        data_dt = {'工作名称': job_name, '职位信息': job_msg}
    # 用上面的字典创建一个DataFrame
    return pd.DataFrame(data_dt)

# 获得页面
def get_pages(keyword, start, end):
    # p_link='a data-v-4f9a87fb="" href="(.*?)" target="_blank" class="el">'
    # 声明要模拟的浏览器是Chrome,并启用无界面浏览模式
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option("detach", True)
    browser = webdriver.Chrome(options=chrome_options)
    browser.maximize_window()

    # 通过get()函数控制浏览器发起请求，访问网址,获取源码
    url = 'https://www.51job.com/'
    browser.get(url)
    # 模拟人操作浏览器，输入搜索关键词，点击搜索按钮
    browser.find_element(By.XPATH, '//*[@id="kwdselectid"]').clear()
    browser.find_element(By.XPATH, '//*[@id="kwdselectid"]').send_keys(keyword)
    browser.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div/button').click()
    time.sleep(2)
    all_data = pd.DataFrame()
    for page in range(start, end + 1):
        time.sleep(2)
        clicks = browser.find_elements(By.CLASS_NAME, 'jname')
        for click in clicks:
            browser.execute_script("arguments[0].click();", click)
            time.sleep(1.1)
            windows = browser.window_handles
            browser.switch_to.window(windows[-1])
            str = browser.title
            slider = None
            track_list = get_track(320)
            if str == '滑动验证页面':
                slider = browser.find_element(By.XPATH, '//*[@id="nc_1_n1z"]')
            if slider is not None:
                action = ActionChains(browser)
                action.click_and_hold(slider).perform()
                for track in track_list:
                    action.move_by_offset(xoffset=track, yoffset=0).perform()
                # 模拟人工滑动超过缺口位置返回至缺口的情况，数据来源于人工滑动轨迹，同时还加入了随机数，都是为了更贴近人工滑动轨迹
                # 放开圆球
                action.pause(random.randint(1, 3) / 10).release().perform()
            time.sleep(0.2)
            all_data = all_data.append(extract_data(browser.page_source))
            browser.close()
            browser.switch_to.window(windows[0])
        # 模拟人操作浏览器，输入搜索关键词，点击搜索按钮
        browser.find_element(By.XPATH, '//*[@id="jump_page"]').clear()
        browser.find_element(By.XPATH, '//*[@id="jump_page"]').send_keys(page)
        browser.find_element(By.XPATH,
                             '//*[@id="app"]/div/div[2]/div/div/div[2]/div/div[2]/div/div[3]/div/div/span[3]').click()

    browser.quit()

    # 将DataFrame保存为Excel
    all_data.to_excel('java工程师.xlsx', index=False)


get_pages('java工程师', 2, 5)
