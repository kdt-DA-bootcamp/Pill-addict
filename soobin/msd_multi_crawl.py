# 필요한 패키지 설치 (주석):
# pip install selenium
# pip install beautifulsoup4
# pip install webdriver-manager

import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def init_driver(headless=True):
    """Selenium Chrome 드라이버 초기화."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    driver_path = ChromeDriverManager().install()
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scroll_to_bottom(driver, pause=1.0, max_tries=3):
    """
    무한스크롤/동적 로딩 대응. 페이지 바닥까지 반복 스크롤.
    pause: 한 번 스크롤 후 대기 시간(초)
    max_tries: 더 이상 높이 변화가 없으면 중단하기까지 허용 시도 수
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    tries = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            tries += 1
            if tries >= max_tries:
                break
        else:
            tries = 0
        last_height = new_height

def parse_page(url, driver):
    """
    1) url 접속
    2) 스크롤 끝까지
    3) HTML 수집
    4) BeautifulSoup으로 불필요한 태그 제거
    5) 본문 추출
    6) { 'url': url, 'extracted_text': text } 반환
    """
    driver.get(url)
    time.sleep(2)  # 초기 로딩
    scroll_to_bottom(driver, pause=1.0)

    html = driver.page_source

    # Soup 파싱
    soup = BeautifulSoup(html, "html.parser")

    # 불필요 요소(script/style/img) 제거
    for tag in soup(["script","style","img"]):
        tag.decompose()

    # 상단 nav, footer 등 제거 (필요 시)
    for nav in soup.find_all("nav"):
        # breadcrumb 등은 남길 수도 있음
        nav.decompose()
    footers = soup.find_all("footer")
    for ft in footers:
        ft.decompose()

    # 주요 컨텐츠 추출
    main_content = soup.find("article") or soup
    text = main_content.get_text(separator="\n", strip=True)

    return {
        "url": url,
        "extracted_text": text
    }

def main():
    # 수집 대상 URL 목록
    urls = [
        "https://www.msdmanuals.com/ko/home/약물/약물-반응에-영향을-미치는-요인/약물-반응의-개요",
        # 필요한 다른 링크들도 추가
        "https://www.msdmanuals.com/ko/home/특별-주제/식이-보충제-및-비타민/식이-보충제-개요",
        # ...
    ]
    
    driver = init_driver(headless=True)
    results = []

    try:
        for link in urls:
            print(f"크롤링: {link}")
            try:
                data = parse_page(link, driver)
                results.append(data)
            except Exception as e:
                print(f"Error on {link}: {e}")

    finally:
        driver.quit()

    # JSON으로 저장 (여러 URL 결과를 배열 형태)
    with open("msd_multi_pages.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ 완료. 총 {len(results)}개 페이지 크롤링 → 'msd_multi_pages.json' 저장.")

if __name__ == "__main__":
    main()
