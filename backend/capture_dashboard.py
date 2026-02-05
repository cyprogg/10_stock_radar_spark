#!/usr/bin/env python3
"""
대시보드 스크린샷 캡처
Decision Stream 대시보드를 1920x1080 해상도로 캡처하여 output 폴더에 저장
"""

from playwright.sync_api import sync_playwright
from datetime import datetime
from pathlib import Path

def capture_dashboard():
    """대시보드 스크린샷 캡처"""
    # 출력 디렉토리 생성
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 파일명 생성 (YYYYMMDD 형식)
    today = datetime.now().strftime("%Y%m%d")
    out_path = output_dir / f"dashboard_{today}.png"
    
    print(f"[대시보드 캡처 시작] {out_path}")
    
    with sync_playwright() as p:
        # Chromium 브라우저 실행
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        
        # 대시보드 페이지 로드
        page.goto("http://127.0.0.1:8125")
        
        # 페이지 로딩 대기 (3초)
        page.wait_for_timeout(3000)
        
        # 스크린샷 캡처
        page.screenshot(path=str(out_path), full_page=False)
        
        # 브라우저 종료
        browser.close()
    
    print(f"[완료] 스크린샷 저장: {out_path}")
    return str(out_path)

if __name__ == "__main__":
    capture_dashboard()
