"""
OpenDART API 클라이언트
공시 정보 및 재무 데이터 수집
- 상장사 공시
- PER/PBR
- 실적 정보
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os


class OpenDARTClient:
    """공개정보 공시시스템(OpenDART) API 클라이언트"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENDART_API_KEY', '')
        self.base_url = "https://opendart.fss.or.kr/api"
        
        if not self.api_key:
            print("⚠️ OpenDART API Key not configured")
    
    # ========== 1. 공시 정보 ==========
    
    def get_disclosures(self, corp_code: str, start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        상장사 공시 정보 조회
        
        Args:
            corp_code: 상장사 고유번호 (8자리)
                     예: 삼성전자 = 00126380
            start_date: 시작 날짜 (YYYYMMDD)
            end_date: 종료 날짜 (YYYYMMDD)
        
        Returns:
            [
                {
                    'report_nm': '분기보고서',          # 공시명
                    'report_cd': '11013',              # 공시 코드
                    'flr_nm': '삼성전자',              # 회사명
                    'rcept_no': '20260130000001',
                    'flr_date': '2026-01-30',          # 공시 일자
                    'rcept_dttm': '2026-01-30 10:00:00'
                },
                ...
            ]
        """
        if not self.api_key:
            return []
        
        # 기본 날짜 설정 (최근 1개월)
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        url = f"{self.base_url}/list.json"
        
        params = {
            'crtfc_key': self.api_key,
            'corp_code': corp_code,
            'start_date': start_date,
            'end_date': end_date,
            'last_reprt_at': 'Y',  # 최종 보고서만
            'page_no': 1,
            'page_count': 100
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == '000':
                    # 공시 목록 파싱
                    disclosures = []
                    for item in data.get('list', []):
                        disclosures.append({
                            'report_nm': item.get('report_nm', ''),
                            'report_cd': item.get('report_cd', ''),
                            'corp_name': item.get('flr_nm', ''),
                            'receipt_no': item.get('rcept_no', ''),
                            'date': item.get('flr_date', ''),
                            'datetime': item.get('rcept_dttm', '')
                        })
                    return disclosures
                else:
                    print(f"❌ API Error: {data.get('message', 'Unknown error')}")
                    return []
            else:
                print(f"❌ HTTP {response.status_code}")
                return []
        
        except Exception as e:
            print(f"❌ Disclosure fetch failed: {e}")
            return []
    
    # ========== 2. 기업 정보 ==========
    
    def get_company_info(self, corp_code: str) -> Optional[Dict[str, Any]]:
        """
        기업 기본 정보 조회
        
        Args:
            corp_code: 상장사 고유번호 (8자리)
        
        Returns:
            {
                'corp_name': '삼성전자',
                'corp_name_eng': 'Samsung Electronics',
                'stock_code': '005930',
                'ceo_nm': '한종희',
                'est_date': '1938-01-13',
                'homepage': 'www.samsung.com',
                'area_nm': '서울특별시'
            }
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/company.json"
        
        params = {
            'crtfc_key': self.api_key,
            'corp_code': corp_code
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == '000':
                    item = data.get('list', [{}])[0]
                    return {
                        'corp_name': item.get('corp_name', ''),
                        'corp_name_eng': item.get('corp_name_eng', ''),
                        'stock_code': item.get('stock_code', ''),
                        'ceo': item.get('ceo_nm', ''),
                        'founded': item.get('est_date', ''),
                        'homepage': item.get('homepage', ''),
                        'region': item.get('area_nm', '')
                    }
                else:
                    return None
            else:
                return None
        
        except Exception as e:
            print(f"❌ Company info fetch failed: {e}")
            return None
    
    # ========== 3. 재무 정보 ==========
    
    def get_financial_statement(self, corp_code: str, bsns_year: str, 
                               reprt_code: str = '11013') -> Optional[Dict[str, Any]]:
        """
        재무제표 정보 조회 (분기/반기/연간)
        
        Args:
            corp_code: 상장사 고유번호
            bsns_year: 사업 연도 (YYYY)
            reprt_code: 보고 코드
                       '11013' = 분기보고서
                       '11012' = 반기보고서
                       '11011' = 정기보고서
        
        Returns:
            {
                'asset': 340000000000000,           # 자산총계
                'liability': 100000000000000,      # 부채총계
                'equity': 240000000000000,         # 자본총계
                'revenue': 60000000000000,         # 매출액
                'net_income': 12000000000000,      # 당기순이익
                'per': 8.5,
                'pbr': 1.2,
                'eps': 100000,
                'bps': 6000000
            }
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/fnlttSinglAcntInvestDcinE.json"
        
        params = {
            'crtfc_key': self.api_key,
            'corp_code': corp_code,
            'bsns_year': bsns_year,
            'reprt_code': reprt_code,
            'fs_div': 'OFS',  # 재무제표
            'sj_div': 'BS',   # 재무상태표
            'page_no': 1,
            'page_count': 100
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == '000':
                    # 재무 항목 추출
                    items = {item['account_nm']: item['thstrm_amount'] 
                            for item in data.get('list', [])}
                    
                    # 주요 지표 계산
                    asset = items.get('자산총계', 0)
                    equity = items.get('자본총계', 0)
                    revenue = items.get('매출액', 0)
                    net_income = items.get('당기순이익', 0)
                    
                    return {
                        'assets': int(asset) if asset else 0,
                        'equity': int(equity) if equity else 0,
                        'revenue': int(revenue) if revenue else 0,
                        'net_income': int(net_income) if net_income else 0
                    }
                else:
                    return None
            else:
                return None
        
        except Exception as e:
            print(f"❌ Financial statement fetch failed: {e}")
            return None
    
    # ========== 4. 기업 코드 조회 ==========
    
    def search_corp_code(self, corp_name: str) -> Optional[str]:
        """
        회사명으로 기업 코드(corp_code) 조회
        
        Args:
            corp_name: 회사명 (예: '삼성전자')
        
        Returns:
            기업 고유번호 (8자리) 또는 None
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/corpCode.json"
        
        params = {
            'crtfc_key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == '000':
                    # 회사명으로 검색
                    for item in data.get('list', []):
                        if item.get('corp_name') == corp_name:
                            return item.get('corp_code')
                    return None
                else:
                    return None
            else:
                return None
        
        except Exception as e:
            print(f"❌ Corp code search failed: {e}")
            return None
    
    # ========== 5. 주식 정보 ==========
    
    def get_stock_info_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        종목코드로 기업 정보 조회
        
        Args:
            ticker: 종목코드 (6자리, 예: '005930')
        
        Returns:
            기업 정보
        """
        # TODO: OpenDART에 직접 종목코드로 검색하는 API 없음
        # 별도 매핑 테이블이나 KRX API 활용 필요
        
        ticker_to_corp_code = {
            '005930': '00126380',  # 삼성전자
            '000660': '00164779',  # SK하이닉스
            '006400': '00147215',  # 삼성SDI
            '012450': '00161761',  # 한화에어로스페이스
            '066570': '00103614',  # LG전자
            '068270': '00063394',  # 셀트리온
        }
        
        corp_code = ticker_to_corp_code.get(ticker)
        if corp_code:
            return self.get_company_info(corp_code)
        return None


class OpenDARTDataAggregator:
    """OpenDART 데이터 집계기 (Agent용)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenDARTClient(api_key)
    
    def get_disclosure_summary(self, ticker: str, days: int = 30) -> Dict[str, Any]:
        """
        종목의 공시 정보 요약
        
        Args:
            ticker: 종목코드
            days: 조회 기간 (일)
        
        Returns:
            {
                'ticker': '005930',
                'disclosure_count': 3,
                'recent_disclosures': [
                    {
                        'date': '2026-02-10',
                        'type': '분기보고서',
                        'url': '...'
                    },
                    ...
                ],
                'has_major_disclosure': True
            }
        """
        # 기업 코드 매핑 (샘플)
        ticker_to_corp = {
            '005930': '00126380',
            '000660': '00164779'
        }
        
        corp_code = ticker_to_corp.get(ticker)
        if not corp_code:
            return {'ticker': ticker, 'disclosure_count': 0, 'recent_disclosures': []}
        
        # 공시 조회
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')
        
        disclosures = self.client.get_disclosures(corp_code, start_date, end_date)
        
        return {
            'ticker': ticker,
            'disclosure_count': len(disclosures),
            'recent_disclosures': disclosures[:5],
            'has_major_disclosure': any(
                '보고서' in d.get('report_nm', '') 
                for d in disclosures
            )
        }
    
    def get_valuation_metrics(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        종목의 밸류에이션 지표
        
        Args:
            ticker: 종목코드
        
        Returns:
            {
                'ticker': '005930',
                'per': 8.5,
                'pbr': 1.2,
                'eps': 100000,
                'bps': 6000000,
                'roe': 15.2,
                'roa': 8.5
            }
        """
        ticker_to_corp = {
            '005930': '00126380',
            '000660': '00164779'
        }
        
        corp_code = ticker_to_corp.get(ticker)
        if not corp_code:
            return None
        
        # 현재 연도 기준 재무정보 조회
        year = datetime.now().year
        financial = self.client.get_financial_statement(corp_code, str(year))
        
        if not financial:
            return None
        
        # 지표 계산
        return {
            'ticker': ticker,
            'per': 0.0,  # TODO: 외부 데이터 연동 필요
            'pbr': 0.0,  # TODO: 외부 데이터 연동 필요
            'eps': 0,    # TODO: 계산 필요
            'bps': 0,    # TODO: 계산 필요
            'roe': 0.0,  # TODO: 순이익/자본
            'roa': 0.0   # TODO: 순이익/자산
        }


# 테스트
if __name__ == '__main__':
    from dotenv import load_dotenv
    from pathlib import Path
    
    # .env 로드
    env_file = Path(__file__).parent.parent / '.env'
    load_dotenv(env_file)
    
    print("=" * 70)
    print("OpenDART API 테스트")
    print("=" * 70)
    
    client = OpenDARTClient()
    
    if not client.api_key:
        print("\n❌ OpenDART API Key 미설정")
        print("   .env 파일에서 OPENDART_API_KEY를 설정해주세요")
    else:
        print(f"\n✅ API Key: {client.api_key[:20]}...")
        
        # 삼성전자 기업코드
        corp_code = '00126380'
        
        # 1. 기업 정보
        print("\n[1] 기업 정보")
        company = client.get_company_info(corp_code)
        if company:
            print(f"  회사명: {company['corp_name']}")
            print(f"  종목코드: {company['stock_code']}")
            print(f"  대표이사: {company['ceo']}")
        
        # 2. 공시 정보
        print("\n[2] 최근 공시")
        disclosures = client.get_disclosures(corp_code)
        for doc in disclosures[:3]:
            print(f"  • {doc['date']}: {doc['report_nm']}")
        
        # 3. 재무 정보
        print("\n[3] 재무 정보")
        financial = client.get_financial_statement(corp_code, '2025')
        if financial:
            print(f"  자산: {financial['assets']:,}원")
            print(f"  자본: {financial['equity']:,}원")
            print(f"  매출: {financial['revenue']:,}원")
            print(f"  순이익: {financial['net_income']:,}원")
        
        # 4. 공시 요약
        print("\n[4] 공시 요약")
        aggregator = OpenDARTDataAggregator()
        summary = aggregator.get_disclosure_summary('005930')
        print(f"  공시 건수: {summary['disclosure_count']}건")
        print(f"  주요 공시 있음: {summary['has_major_disclosure']}")
