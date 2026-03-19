import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# 1. 웹페이지 기본 설정
st.set_page_config(page_title="SafeTrip - 해외 소매치기 제보 지도", layout="wide")

st.title("📍 해외 소매치기 주의 장소 공유 서비스")
st.info("지도를 움직여 제보할 위치를 화면 중앙의 🔴 마커에 맞춰주세요.")

# 2. 데이터 관리 (세션 저장소 활용)
if 'locations' not in st.session_state:
    st.session_state.locations = [
        {"name": "파리 루브르 박물관", "lat": 48.8606, "lon": 2.3376, "desc": "설문조사단 접근 주의"},
        {"name": "로마 테르미니역", "lat": 41.9009, "lon": 12.5020, "desc": "티켓 머신 근처 소매치기 빈번"},
        {"name": "바르셀로나 람블라스 거리", "lat": 41.3817, "lon": 2.1728, "desc": "오물 뿌리기 수법 주의"}
    ]

# 초기 지도 중심 설정 (마지막 제보 위치 혹은 기본값)
if 'map_center' not in st.session_state:
    st.session_state.map_center = [48.8566, 2.3522]  # 파리 기준

# 3. 지도 표시 영역 및 위치 캡처
st.subheader("⚠️ 실시간 위험 지도 및 위치 선택")

# 지도 위에 고정된 마커 아이콘을 표시하기 위한 CSS (지도가 움직여도 화면 중앙에 고정)
st.markdown(
    """
    <style>
    .center-marker {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -100%);
        z-index: 1000;
        pointer-events: none;
        font-size: 30px;
    }
    .map-container {
        position: relative;
    }
    </style>
    """, unsafe_allow_html=True
)

# 지도 생성
m = folium.Map(location=st.session_state.map_center, zoom_start=13)

# 기존 제보된 마커들 표시
for loc in st.session_state.locations:
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        popup=folium.Popup(f"<b>{loc['name']}</b><br>{loc['desc']}", max_width=300),
        tooltip=loc['name'],
        icon=folium.Icon(color='red', icon='warning', prefix='fa')
    ).add_to(m)

# 지도 출력 및 변화 감지
with st.container():
    # 지도 컨테이너 안에 십자 마커 배치
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    map_data = st_folium(m, width="100%", height=500, key="main_map")
    # 지도 정중앙에 고정될 시각적 표시 (이모지 혹은 아이콘)
    st.markdown('<div class="center-marker">📍</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 지도가 움직였을 때 현재 중심 좌표 가져오기
current_lat = st.session_state.map_center[0]
current_lon = st.session_state.map_center[1]

if map_data['center']:
    current_lat = map_data['center']['lat']
    current_lon = map_data['center']['lng']

# 4. 사이드바: 현재 중앙 좌표 기반 제보 입력란
with st.sidebar:
    st.header("📢 위험 장소 제보")
    st.write("지도 중앙의 좌표가 자동으로 입력됩니다.")
    
    with st.form("report_form"):
        new_name = st.text_input("장소 명칭 (예: 에펠탑 근처)")
        # 지도 중심 좌표를 표시 (수정 가능하게 하려면 number_input 유지, 아니면 text로 고정)
        st.write(f"**선택된 위도:** `{current_lat:.6f}`")
        st.write(f"**선택된 경도:** `{current_lon:.6f}`")
        new_desc = st.text_area("위험 내용/수법")
        
        submit_button = st.form_submit_button("현재 위치로 제보 등록")
        
        if submit_button:
            if new_name:
                st.session_state.locations.append({
                    "name": new_name, 
                    "lat": current_lat, 
                    "lon": current_lon, 
                    "desc": new_desc
                })
                # 등록 후 지도가 해당 위치를 유지하도록 세션 업데이트
                st.session_state.map_center = [current_lat, current_lon]
                st.success("제보가 완료되었습니다!")
                st.rerun()

# 5. 하단 데이터 표
st.divider()
st.subheader("📋 전체 제보 목록")
df = pd.DataFrame(st.session_state.locations)
st.dataframe(df, use_container_width=True)
