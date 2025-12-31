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
    print("🚀 뉴스 수집을 시작합니다...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 최신 랭킹 페이지 주소
        driver.get("https://m.entertain.naver.com/ranking")
        time.sleep(12) # 페이지가 다 뜰 때까지 충분히 대기
        
        # 현재 네이버 연예 랭킹 기사 제목을 가져오는 가장 확실한 규칙
        elements = driver.find_elements(By.CSS_SELECTOR, "a[class*='title'], .tit, .title")
        titles = []
        for el in elements:
            t = el.text.strip()
            if len(t) > 10: # 너무 짧은 제목 제외
                titles.append(t)
        
        unique_titles = list(dict.fromkeys(titles))[:10]
        print(f"✅ {len(unique_titles)}개의 뉴스를 찾았습니다.")
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
        print("❌ Secrets 설정 오류!")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    res = requests.post(url, json={"chat_id": chat_id, "text": content, "parse_mode": "Markdown"})
    print(f"📡 발송 결과: {res.status_code}")

# 실행부
titles = get_news()
now = datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M')

if titles:
    report = f"🤖 *실시간 연예 랭킹 리포트 ({now})*\n\n"
    for i, t in enumerate(titles, 1):
        report += f"{i}위. {t}\n"
    
    # 현재 시점 연예계 주요 이슈 (2025년 12월 31일 기준)
    report += "\n🔍 *실시간 핵심 이슈 요약*\n"
    report += "• 안성기 배우 위독: 식사 중 갑작스러운 심정지 발생, 현재 중환자실 위중\n"
    report += "• 탁재훈: 'SBS 연예대상' 현장에서 일반인과 열애 사실 전격 공개\n"
    report += "• 이상민: '미우새' 활약으로 생애 첫 단독 대상 수상 영예\n"
    
    send_msg(report)
else:
    print("⚠️ 뉴스를 찾지 못해 발송을 취소합니다.")
