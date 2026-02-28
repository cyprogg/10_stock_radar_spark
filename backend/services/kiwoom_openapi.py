"""
키움 Open API+ 래퍼 - REST API 기반 일봉 데이터 조회
공식 샘플: https://developers.kiwoom.com
"""

import requests
import json
import os
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

class KiwoomOpenAPI:
    """키움 Open API+ (REST API) 래퍼"""
    
    def __init__(self, app_id: Optional[str] = None, secret_key: Optional[str] = None, is_mock: bool = False):
        """
        키움 Open API 초기화
        
        Args:
            app_id: 앱키 (KIWOOM_APP_ID)
            secret_key: 시크릿키 (KIWOOM_SECRET_KEY)
            is_mock: True=모의투자, False=실전투자 (기본값)
        """
        self.app_id = app_id or os.getenv('KIWOOM_APP_ID')
        self.secret_key = secret_key or os.getenv('KIWOOM_SECRET_KEY', '')
        self.is_mock = is_mock
        
        # 환경 검증
        if not self.app_id or self.app_id == 'YOUR_KIWOOM_APP_ID_HERE':
            logger.error("❌ KIWOOM_APP_ID not configured. Please register at https://developers.kiwoom.com")
            raise ValueError("KIWOOM_APP_ID not configured in .env")
        
        if not self.secret_key or self.secret_key == 'YOUR_KIWOOM_SECRET_KEY_HERE':
            logger.error("❌ KIWOOM_SECRET_KEY not configured")
            raise ValueError("KIWOOM_SECRET_KEY not configured in .env")
        
        # API 호스트 선택 (모의투자/실전투자)
        self.host = 'https://mockapi.kiwoom.com' if is_mock else 'https://api.kiwoom.com'
        self.token = None
        self.token_expire = None
        
        logger.info(f"✅ Kiwoom OpenAPI 초기화 ({self.host})")
    
    def get_token(self) -> str:
        """
        OAuth 2.0 클라이언트 크레덴셜 토큰 발급 (공식 샘플 기반)
        
        Returns:
            access_token: 유효한 접근 토큰
        
        Raises:
            Exception: 토큰 발급 실패 시
        """
        # 캐시된 토큰 확인 (유효 기간 내면 재사용)
        if self.token and self.token_expire and datetime.now() < self.token_expire:
            logger.debug(f"📦 캐시된 토큰 사용 (만료: {self.token_expire})")
            return self.token
        
        # 1. 토큰 발급 요청
        endpoint = '/oauth2/token'
        url = self.host + endpoint
        
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
        }
        
        # 2. 요청 데이터 (공식 샘플 참조)
        data = {
            'grant_type': 'client_credentials',
            'appkey': self.app_id,
            'secretkey': self.secret_key,
        }
        
        try:
            logger.debug(f"🔐 토큰 요청 중... ({self.host})")
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code != 200:
                error_msg = response.json() if response.headers.get('content-type') == 'application/json' else response.text
                logger.error(f"❌ 토큰 발급 실패 ({response.status_code}): {error_msg}")
                raise Exception(f"Token 발급 실패: {response.status_code}")
            
            # 3. 응답 파싱
            result = response.json()
            self.token = result.get('access_token')
            
            if not self.token:
                logger.error(f"❌ 응답에 access_token 없음: {result}")
                raise Exception("Invalid token response format")
            
            # 토큰 유효 기간 설정 (일반적으로 24시간)
            expires_in = result.get('expires_in', 86400)  # 초 단위
            self.token_expire = datetime.now() + timedelta(seconds=expires_in * 0.9)  # 90% 시점에 갱신
            
            logger.info(f"✅ 토큰 발급 완료 (유효: {self.token_expire})")
            logger.debug(f"   응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            return self.token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 네트워크 오류: {e}")
            raise Exception(f"Token 발급 네트워크 오류: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 파싱 오류: {e}")
            raise Exception(f"Token 응답 파싱 오류: {e}")
    
    def get_daily_chart(self, ticker: str, start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> Optional[List[Dict]]:
        """
        일봉(Daily) 차트 데이터 조회 - API ka10081 (공식 명세 기반)
        
        Args:
            ticker: 종목코드 (6자리, 예: '005930' = 삼성전자)
            start_date: 시작 날짜 (YYYYMMDD, 기본값: 120일 전)
            end_date: 종료 날짜 (YYYYMMDD, 기본값: 오늘)
        
        Returns:
            [
                {
                    'date': '2026-02-20',
                    'open': 1200000.0,
                    'high': 1260000.0,
                    'low': 1190000.0,
                    'close': 1251000.0,    # cur_prc
                    'volume': 123456,      # trde_qty
                    'amount': 155234567000 # trde_prica (거래대금)
                },
                ...
            ]
            또는 None (실패 시)
        
        공식 스펙 (API ka10081):
            - 엔드포인트: POST /api/dostk/chart
            - 응답 데이터: stk_dt_pole_chart_qry 배열 (최대 600개)
            - 기준일자 기반 조회 (과거 데이터 역순)
        """
        try:
            # 기본값 설정
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start = datetime.now() - timedelta(days=120)
                start_date = start.strftime('%Y%m%d')
            
            logger.info(f"📊 일봉 조회: {ticker} (기준일: {end_date})")
            
            # 공식 API 엔드포인트
            endpoint = '/api/dostk/chart'
            url = self.host + endpoint
            
            # 공식 헤더 (API ka10081 기준)
            headers = {
                'Content-Type': 'application/json;charset=UTF-8',
                'Authorization': f'Bearer {self.get_token()}',
                'api-id': 'ka10081',
                'cont-yn': 'N',  # 초기 요청
                'next-key': ''
            }
            
            # 공식 요청 바디
            request_body = {
                'stk_cd': ticker,          # 종목코드
                'base_dt': end_date,       # 기준일자 (YYYYMMDD)
                'upd_stkpc_tp': '1'        # 수정주가 적용 (0=미수정, 1=수정)
            }
            
            logger.debug(f"요청: {json.dumps({'url': url, 'body': request_body}, ensure_ascii=False)}")
            
            response = requests.post(url, headers=headers, json=request_body, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"⚠️ HTTP {response.status_code}: {response.text[:100]}")
                return None
            
            data = response.json()
            
            # 응답 상태 확인
            return_code = data.get('return_code', '-1')
            return_msg = data.get('return_msg', 'Unknown error')
            
            if return_code != '0':
                logger.warning(f"⚠️ API 응답 오류: {return_msg} (code: {return_code})")
                return None
            
            # 응답 헤더 정보 (연속 조회용)
            cont_yn = response.headers.get('cont-yn', 'N')
            next_key = response.headers.get('next-key', '')
            
            if cont_yn == 'Y':
                logger.debug(f"📄 연속 조회 가능 (다음 키: {next_key})")
            
            # 일봉 데이터 추출
            chart_data = data.get('stk_dt_pole_chart_qry', [])
            
            if not chart_data:
                logger.debug(f"📭 {ticker}: 차트 데이터 없음")
                return None
            
            # 공식 응답 필드명에 따라 파싱
            result = []
            for item in chart_data:
                try:
                    # 공식 필드명 (모두 문자열)
                    date_str = item.get('dt', '')  # YYYYMMDD 형식
                    
                    if not date_str or len(date_str) != 8:
                        continue
                    
                    # YYYYMMDD → YYYY-MM-DD
                    date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    
                    # 값이 문자열이므로 float로 변환
                    def parse_price(val):
                        try:
                            if not val or val == '':
                                return 0.0
                            return float(str(val).replace(',', ''))
                        except (ValueError, TypeError):
                            return 0.0
                    
                    result.append({
                        'date': date,
                        'open': parse_price(item.get('open_pric')),      # 시가
                        'high': parse_price(item.get('high_pric')),      # 고가
                        'low': parse_price(item.get('low_pric')),        # 저가
                        'close': parse_price(item.get('cur_prc')),       # 현재가(종가)
                        'volume': int(parse_price(item.get('trde_qty'))), # 거래량
                        'amount': int(parse_price(item.get('trde_prica'))) # 거래대금
                    })
                
                except Exception as e:
                    logger.debug(f"⚠️ 항목 파싱 오류: {e}")
                    continue
            
            if result:
                logger.info(f"✅ {ticker}: {len(result)}개 일봉 조회 완료")
                return sorted(result, key=lambda x: x['date'])  # 날짜순 정렬
            else:
                logger.warning(f"❌ {ticker}: 파싱된 데이터 없음")
                return None
        
        except requests.exceptions.Timeout:
            logger.error(f"⏱️ 타임아웃: {ticker}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 네트워크 오류: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 예상 치 못한 오류 ({ticker}): {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def get_daily_chart_paginated(self, ticker: str, base_date: str, 
                                 max_records: int = 600) -> Optional[List[Dict]]:
        """
        일봉 데이터 연속 조회 (페이지네이션)
        
        Args:
            ticker: 종목코드
            base_date: 기준일자 (YYYYMMDD)
            max_records: 최대 조회 레코드 수 (기본 600개)
        
        Returns:
            [{'date': ..., 'open': ..., ...}, ...]
        
        Note:
            연속 조회가 필요하면 응답의 cont-yn과 next-key를 활용합니다.
            예: 120일 이상의 데이터는 여러 번 호출이 필요할 수 있습니다.
        """
        all_results = []
        cont_yn = 'N'
        next_key = ''
        request_count = 0
        max_requests = 10  # 무한 루프 방지
        
        logger.info(f"📊 연속 조회 시작: {ticker} (기준일: {base_date})")
        
        while request_count < max_requests:
            try:
                endpoint = '/api/dostk/chart'
                url = self.host + endpoint
                
                headers = {
                    'Content-Type': 'application/json;charset=UTF-8',
                    'Authorization': f'Bearer {self.get_token()}',
                    'api-id': 'ka10081',
                    'cont-yn': cont_yn,
                    'next-key': next_key
                }
                
                request_body = {
                    'stk_cd': ticker,
                    'base_dt': base_date,
                    'upd_stkpc_tp': '1'
                }
                
                response = requests.post(url, headers=headers, json=request_body, timeout=15)
                
                if response.status_code != 200:
                    logger.warning(f"⚠️ 요청 {request_count + 1}: HTTP {response.status_code}")
                    break
                
                data = response.json()
                
                if data.get('return_code') != '0':
                    logger.warning(f"⚠️ 요청 {request_count + 1}: {data.get('return_msg')}")
                    break
                
                chart_data = data.get('stk_dt_pole_chart_qry', [])
                
                # 파싱
                for item in chart_data:
                    try:
                        date_str = item.get('dt', '')
                        if not date_str or len(date_str) != 8:
                            continue
                        
                        date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                        
                        def parse_price(val):
                            try:
                                return float(str(val).replace(',', '')) if val else 0.0
                            except:
                                return 0.0
                        
                        all_results.append({
                            'date': date,
                            'open': parse_price(item.get('open_pric')),
                            'high': parse_price(item.get('high_pric')),
                            'low': parse_price(item.get('low_pric')),
                            'close': parse_price(item.get('cur_prc')),
                            'volume': int(parse_price(item.get('trde_qty'))),
                            'amount': int(parse_price(item.get('trde_prica')))
                        })
                    except:
                        continue
                
                logger.info(f"   요청 {request_count + 1}: {len(chart_data)}개 조회 (누적: {len(all_results)}개)")
                
                # 연속 조회 여부 확인
                cont_yn = response.headers.get('cont-yn', 'N')
                next_key = response.headers.get('next-key', '')
                
                if cont_yn != 'Y' or not next_key:
                    logger.info(f"✅ 연속 조회 완료 (총 {len(all_results)}개)")
                    break
                
                if len(all_results) >= max_records:
                    logger.info(f"✅ 최대 레코드 도달 (총 {len(all_results)}개)")
                    break
                
                request_count += 1
                time.sleep(0.5)  # Rate limit 방지
            
            except Exception as e:
                logger.error(f"❌ 요청 {request_count + 1} 오류: {e}")
                break
        
        if all_results:
            return sorted(all_results, key=lambda x: x['date'])
        else:
            return None


if __name__ == "__main__":
    """키움 Open API 테스트 (공식 API ka10081 기반)"""
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("=" * 70)
    print("🔑 키움 Open API 테스트 (일봉 차트 데이터 조회)")
    print("=" * 70)
    
    try:
        # 1. 초기화 테스트
        print("\n[1] API 초기화 중...")
        kiwoom = KiwoomOpenAPI(is_mock=False)  # False=실전투자, True=모의투자
        print("✅ 초기화 완료\n")
        
        # 2. 토큰 발급 테스트
        print("[2] OAuth 2.0 토큰 발급 테스트...")
        token = kiwoom.get_token()
        print(f"✅ 토큰: {token[:40]}...\n")
        
        # 3. 일봉 데이터 조회 테스트 (API ka10081)
        print("[3] 일봉 차트 데이터 조회 테스트 (API ka10081)...")
        
        test_tickers = [
            ('005930', '삼성전자'),
            ('012450', '한화에어로스페이스'),
            ('079550', 'LIG넥스원'),
        ]
        
        for ticker, name in test_tickers:
            print(f"\n   [{ticker}] {name} 조회 중...")
            
            # 단일 요청
            chart = kiwoom.get_daily_chart(ticker)
            
            if chart:
                print(f"   ✅ 조회 완료 ({len(chart)}개 일봉)")
                print("   최근 5일 데이터:")
                for item in chart[-5:]:
                    print(f"      {item['date']}: "
                          f"종가 {item['close']:>10,.0f}원 | "
                          f"거래량 {item['volume']:>10,} | "
                          f"거래대금 {item['amount']:>15,}원")
            else:
                print(f"   ⚠️ 데이터 없음 또는 API 오류")
        
        # 4. 연속 조회 테스트 (선택)
        print("\n\n[4] 연속 조회 테스트 (600개 이상 데이터)...")
        print("   적용 시기: 120일 이상 데이터 필요 시")
        print("   🚀 테스트 스킵 (불필요한 중복 요청 방지)")
        
        print("\n" + "=" * 70)
        print("✅ 테스트 완료")
        print("=" * 70)
        
        print("\n📌 다음 단계:")
        print("   1. collect_historical_prices.py로 초기 120일 데이터 수집")
        print("   2. scheduler.py에서 매일 자동 갱신 설정")
        print("   3. database에 StockPrice 테이블 생성 (마이그레이션 필요)")
        
    except FileNotFoundError:
        print("❌ .env 파일을 찾을 수 없습니다.")
        print("   필요한 설정:")
        print("   - KIWOOM_APP_ID: 키움에서 발급받은 앱 ID")
        print("   - KIWOOM_SECRET_KEY: 키움에서 발급받은 시크릿 키")
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
