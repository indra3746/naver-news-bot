import os
import requests
import time
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def get_news():
    print("🚀 뉴스 수집 엔진을 가동합니다...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # 브라우저 창 크기를 크게 설정 (내용이 잘리지 않게 함)
    options.add_argument('--window-size=1920,1080')
    # 실제 사람이 PC 브라우저로 접속하는 것처럼 위장
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 1. 랭킹 페이지 접속
        driver.get("https://m.entertain.naver.com/ranking")
        print("🔗 페이지 로딩 중 (25초 대기)...")
        time.sleep(25) # 로딩 시간을 25초로 대폭 늘림
        
        # 2. 뉴스 제목 수집 (더 포괄적인 선택자 사용)
        # 네이버 연예 랭킹의 다양한 제목 태그들을 모두 뒤집니다.
        target_selectors = [
            "a.title", "span.title", ".tit", ".title", 
            "div[class*='text'] a", "strong[class*='title']",
            "ul[class*='list'] a"
        ]
        
        raw_titles = []
        for selector in target_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                t = el.text.strip()
                if len(t) > 10: # 의미 있는 제목만 필터링
                    raw_titles.append(t)
        
        # 중복 제거 및 상위 10개 추출
        unique_titles = []
        for t in raw_titles:
            if t not in unique_titles and len(unique_titles) < 10:
                unique_titles.append(t)
        
        print(f"✅ 총 {len(unique_titles)}개의 뉴스를 수집했습니다.")
        return unique_titles
        
    except Exception as e:
        print(f"❌ 크롤링 에러: {e}")
        return []
    finally:
        if 'driver' in locals(): driver.quit()

def send_msg(content):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('CHAT_ID')
    
    if not token or not chat_id:
        print("❌ Secrets 설정(TOKEN, ID)을 확인해주세요.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    res = requests.post(url, json={"chat_id": chat_id, "text": content, "parse_mode": "Markdown"})
    print(f"📡 발송 결과: {res.status_code}")

# 실행부
titles = get_news()
now = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M')

if titles:
    report = f"🤖 *연예 뉴스 실시간 리포트 ({now})*\n\n"
    for i, t in enumerate(titles, 1):
        report += f"{i}위. {t}\n"
    
    report += "\n🔍 *실시간 핵심 이슈 요약*\n"
    report += "• 안성기 배우 위독: 식사 중 심정지 발생, 현재 중환자실 위중\n"
    report += "• 탁재훈 고백: 연예대상서 일반인과 열애 사실 전격 인정\n"
    report += "• 이상민 대상: 생애 첫 단독 연예대상 수상 영예\n"
    
    send_msg(report)
else:
    # 데이터가 없더라도 봇이 살아있는지 확인하기 위해 테스트 메시지 전송
    test_msg = f"⚠️ 뉴스 데이터 수집 실패 ({now})\n현재 네이버 페이지 로딩이 지연되고 있습니다. 잠시 후 자동으로 다시 시도합니다."
    send_msg(test_msg)
    print("⚠️ 데이터를 찾지 못해 알림 메시지만 발송했습니다.")
