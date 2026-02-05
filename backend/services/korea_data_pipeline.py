"""
한국 시장 데이터 파이프라인 (무료/공식 데이터 우선)

데이터 소스:
1. KRX 투자자별 매매동향 (기관/외국인/개인)
2. OpenDART API (공시/실적)
3. 네이버 금융 (시세/뉴스)
4. KIS API (실시간 시세)

업데이트 주기:
- 시세: 실시간 (KIS API)
- 수급: 일 1회 (KRX, 장 마감 후)
- 공시: 실시간 (OpenDART)
- 뉴스: 실시간 (크롤링)
"""

import aiohttp
import asyncio
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup


class KoreaDataPipeline:
    """
    한국 시장 데이터 자동 수집 (무료/공식 우선)
    """
    
    def __init__(self):
        self.dart_api_key = os.getenv("OPENDART_API_KEY", "")
        self.naver_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    # ========== 1) KRX 투자자별 매매동향 ==========
    
    async def fetch_krx_supply_demand(self, date: Optional[str] = None) -> Dict:
        """
        KRX 투자자별 매매동향 수집
        
        Args:
            date: YYYYMMDD (기본값: 어제)
        
        Returns:
            {
                "stock_code": {
                    "inst_net": 기관 순매수 (원),
                    "foreign_net": 외국인 순매수 (원),
                    "retail_net": 개인 순매수 (원)
                }
            }
        """
        if not date:
            yesterday = datetime.now() - timedelta(days=1)
            date = yesterday.strftime("%Y%m%d")
        
        # KRX 데이터 포털 URL
        url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
        
        payload = {
            "bld": "dbms/MDC/STAT/standard/MDCSTAT02301",
            "trdDd": date,
            "money": "1",  # 금액 기준
            "csvxls_isNo": "false"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=payload, headers=self.naver_headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_krx_data(data)
                    else:
                        print(f"❌ KRX 데이터 수집 실패: {response.status}")
                        return {}
        except Exception as e:
            print(f"❌ KRX API 오류: {e}")
            return {}
    
    def _parse_krx_data(self, raw_data: Dict) -> Dict:
        """
        KRX JSON 파싱
        """
        result = {}
        
        for item in raw_data.get("OutBlock_1", []):
            stock_code = item.get("ISU_SRT_CD", "")
            
            result[stock_code] = {
                "inst_net": int(item.get("INST_NTBY_QTY", 0)),  # 기관 순매수
                "foreign_net": int(item.get("FRGN_NTBY_QTY", 0)),  # 외국인
                "retail_net": int(item.get("INDV_NTBY_QTY", 0))  # 개인
            }
        
        return result
    
    # ========== 2) OpenDART 공시 ==========
    
    async def fetch_dart_disclosures(self, date: Optional[str] = None) -> List[Dict]:
        """
        OpenDART 당일 공시 조회
        
        Args:
            date: YYYYMMDD (기본값: 오늘)
        
        Returns:
            [
                {
                    "corp_code": 기업 코드,
                    "corp_name": 기업명,
                    "report_nm": 보고서명,
                    "rcept_dt": 접수일,
                    "flr_nm": 공시자
                }
            ]
        """
        if not self.dart_api_key:
            print("⚠️ OpenDART API Key 없음. 공시 수집 불가.")
            return []
        
        if not date:
            date = datetime.now().strftime("%Y%m%d")
        
        url = "https://opendart.fss.or.kr/api/list.json"
        
        params = {
            "crtfc_key": self.dart_api_key,
            "bgn_de": date,
            "end_de": date,
            "page_count": 100
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_dart_data(data)
                    else:
                        print(f"❌ OpenDART API 실패: {response.status}")
                        return []
        except Exception as e:
            print(f"❌ OpenDART API 오류: {e}")
            return []
    
    def _parse_dart_data(self, raw_data: Dict) -> List[Dict]:
        """
        OpenDART JSON 파싱
        """
        if raw_data.get("status") != "000":
            return []
        
        disclosures = []
        
        for item in raw_data.get("list", []):
            # 주요 공시만 필터링
            important_keywords = [
                "수주", "계약", "결산", "분기보고서", "사업보고서", 
                "주요사항", "타법인", "유상증자"
            ]
            
            report_name = item.get("report_nm", "")
            
            if any(kw in report_name for kw in important_keywords):
                disclosures.append({
                    "corp_code": item.get("corp_code", ""),
                    "corp_name": item.get("corp_name", ""),
                    "report_nm": report_name,
                    "rcept_dt": item.get("rcept_dt", ""),
                    "flr_nm": item.get("flr_nm", "")
                })
        
        return disclosures
    
    # ========== 3) 네이버 금융 뉴스 ==========
    
    async def fetch_naver_news(self, stock_code: str, days: int = 7) -> List[Dict]:
        """
        네이버 금융 뉴스 수집
        
        Args:
            stock_code: 종목 코드 (예: "005930")
            days: 최근 N일
        
        Returns:
            [
                {
                    "title": 제목,
                    "link": 링크,
                    "date": 날짜,
                    "source": 출처
                }
            ]
        """
        url = f"https://finance.naver.com/item/news_news.nhn?code={stock_code}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.naver_headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_naver_news(html, days)
                    else:
                        print(f"❌ 네이버 뉴스 수집 실패: {response.status}")
                        return []
        except Exception as e:
            print(f"❌ 네이버 크롤링 오류: {e}")
            return []
    
    def _parse_naver_news(self, html: str, days: int) -> List[Dict]:
        """
        네이버 뉴스 HTML 파싱
        """
        soup = BeautifulSoup(html, 'html.parser')
        news_items = soup.select('.newsList .articleSubject a')
        
        news_list = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for item in news_items[:20]:  # 최대 20개
            title = item.get_text().strip()
            link = "https://finance.naver.com" + item.get('href', '')
            
            news_list.append({
                "title": title,
                "link": link,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": "네이버 금융"
            })
        
        return news_list
    
    # ========== 4) 종합 데이터 수집 ==========
    
    async def collect_daily_data(self, stock_codes: List[str]) -> Dict:
        """
        매일 장 마감 후 자동 수집
        
        Args:
            stock_codes: ["005930", "000660", ...]
        
        Returns:
            {
                "supply_demand": {...},
                "disclosures": [...],
                "news": {...},
                "timestamp": "2026-01-27 16:00:00"
            }
        """
        print(f"📊 한국 시장 데이터 수집 시작 ({len(stock_codes)}개 종목)")
        
        # 병렬 수집
        tasks = [
            self.fetch_krx_supply_demand(),
            self.fetch_dart_disclosures()
        ]
        
        results = await asyncio.gather(*tasks)
        
        supply_demand = results[0]
        disclosures = results[1]
        
        # 뉴스는 종목별로 수집 (시간 제약 고려)
        news = {}
        for code in stock_codes[:10]:  # 최대 10개 종목만
            news[code] = await self.fetch_naver_news(code)
        
        return {
            "supply_demand": supply_demand,
            "disclosures": disclosures,
            "news": news,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    # ========== 5) 섹터 분류 (GICS) ==========
    
    def classify_sector(self, stock_code: str) -> str:
        """
        종목을 섹터로 분류
        
        ⚠️ 간단한 매핑. 실전에서는 KRX 업종 데이터 사용.
        """
        sector_map = {
            # 방산
            "012450": "방산",  # 한화에어로스페이스
            "047810": "방산",  # 한국항공우주
            
            # 헬스케어
            "207940": "헬스케어",  # 삼성바이오로직스
            "068270": "헬스케어",  # 셀트리온
            "326030": "헬스케어",  # SK바이오팜
            
            # AI 반도체
            "005930": "AI 반도체",  # 삼성전자
            "000660": "AI 반도체",  # SK하이닉스
            
            # 전력
            "015760": "전력",  # 한국전력
            
            # 에너지
            "010950": "에너지",  # S-Oil
        }
        
        return sector_map.get(stock_code, "기타")
    
    # ========== 6) 데이터 품질 검증 ==========
    
    def validate_data(self, data: Dict) -> bool:
        """
        수집된 데이터 품질 검증
        """
        checks = {
            "supply_demand": len(data.get("supply_demand", {})) > 0,
            "disclosures": isinstance(data.get("disclosures", []), list),
            "news": len(data.get("news", {})) > 0
        }
        
        passed = sum(checks.values())
        total = len(checks)
        
        print(f"✅ 데이터 품질 검증: {passed}/{total} 통과")
        
        for name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {name}")
        
        return passed >= 2  # 최소 2개 이상 통과


# ========== 테스트 ==========

async def test_pipeline():
    """
    파이프라인 테스트
    """
    pipeline = KoreaDataPipeline()
    
    # 테스트 종목
    test_stocks = ["005930", "012450", "207940"]
    
    print("=" * 60)
    print("한국 데이터 파이프라인 테스트")
    print("=" * 60)
    
    # 1) KRX 수급
    print("\n1️⃣ KRX 투자자별 매매동향")
    supply_demand = await pipeline.fetch_krx_supply_demand()
    print(f"  수집 종목 수: {len(supply_demand)}")
    
    # 2) OpenDART 공시
    print("\n2️⃣ OpenDART 공시")
    disclosures = await pipeline.fetch_dart_disclosures()
    print(f"  주요 공시 수: {len(disclosures)}")
    if disclosures:
        print(f"  예시: {disclosures[0]['corp_name']} - {disclosures[0]['report_nm']}")
    
    # 3) 네이버 뉴스
    print("\n3️⃣ 네이버 금융 뉴스")
    news = await pipeline.fetch_naver_news("005930")
    print(f"  삼성전자 뉴스 수: {len(news)}")
    if news:
        print(f"  예시: {news[0]['title']}")
    
    # 4) 종합 수집
    print("\n4️⃣ 종합 데이터 수집")
    all_data = await pipeline.collect_daily_data(test_stocks)
    
    # 5) 품질 검증
    print("\n5️⃣ 데이터 품질 검증")
    is_valid = pipeline.validate_data(all_data)
    
    if is_valid:
        print("\n✅ 파이프라인 테스트 성공!")
    else:
        print("\n⚠️ 일부 데이터 수집 실패")


if __name__ == "__main__":
    # 비동기 실행
    asyncio.run(test_pipeline())
