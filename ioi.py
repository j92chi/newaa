import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# 1. 웹페이지 기본 설정
st.set_page_config(page_title="SafeTrip - 해외 소매치기 제보 지도", layout="wide")

# 2. 모바일 십자선 고정 및 지도 스타일 CSS
st.markdown("""
    <style>
    /* 지도 컨테이너 설정 */
    .map-container {
        position: relative;
        width: 100%;
    }
    /* 십자선을 지도 한가운데에 고정 */
    .crosshair {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 1000;
        pointer-events: none; /* 십자선이 터치/클릭을 방해하지 않음 */
        color: #ff4b4b;
        font-size: 30px;
        font-weight: bold;
        text-shadow: 1px 1px 2px white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📍 해외 소매치기 주의 장소 공유 서비스")
st.info("여행객들이 직접 제보한 실시간 위험 지역 지도입니다.")

# 3. 데이터 관리 (세션 저장소 활용)
if 'locations' not in st.session_state:
    st.session_state.locations = [
        {"name": "파리 루브르 박물관", "lat": 48.8606, "lon": 2.3376, "desc": "설문조사단 접근 주의"},
        {"name": "로마 테르미니역", "lat": 41.9009, "lon": 12.5020, "desc": "티켓 머신 근처 소매치기 빈번"},
        {"name": "바르셀로나 람블라스 거리", "lat": 41.3817, "lon": 2.1728, "desc": "오물 뿌리기 수법 주의"}
    ]

# 4. 사이드바: 제보 입력란
with st.sidebar:
    st.header("📢 위험 장소 제보")
    with st.form("report_form"):
        new_name = st.text_input("장소 명칭 (예: 에펠탑 근처)")
        # 모바일 입력 편의를 위해 초기값을 유럽 중심으로 설정
        new_lat = st.number_input("위도 (Latitude)", value=45.0, format="%.6f")
        new_lon = st.number_input("경도 (Longitude)", value=15.0, format="%.6f")
        new_desc = st.text_area("위험 내용/수법")
        submit_button = st.form_submit_button("제보 등록")
        
        if submit_button:
            if new_name:
                st.session_state.locations.append({
                    "name": new_name, "lat": new_lat, "lon": new_lon, "desc": new_desc
                })
                st.success("제보가 완료되었습니다!")
                st.rerun()

# 5. 지도 표시 영역
st.subheader("⚠️ 실시간 위험 지도")

# 십자선이 포함된 컨테이너 시작
st.markdown('<div class="map-container">', unsafe_allow_html=True)

# 지도 생성
m = folium.Map(location=[45.0, 15.0], zoom_start=4, control_scale=True)

# 마커 추가 (.add_to 오타 수정 완료)
for loc in st.session_state.locations:
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        popup=folium.Popup(f"<b>{loc['name']}</b><br>{loc['desc']}", max_width=300),
        tooltip=loc['name'],
        icon=folium.Icon(color='red', icon='warning', prefix='fa')
    ).add_to(m)

# 지도 화면에 출력 및 십자선 오버레이
st_folium(m, width="100%", height=500)
st.markdown('<div class="crosshair">+</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True) # 컨테이너 종료

# 6. 하단 데이터 표
st.divider()
st.subheader("📋 전체 제보 목록")
df = pd.DataFrame(st.session_state.locations)
st.dataframe(df, use_container_width=True)
