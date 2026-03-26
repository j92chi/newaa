import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# 1. 웹페이지 설정
st.set_page_config(page_title="SafeTrip - 제보 지도", layout="wide")

# 2. 십자선 및 지도 스타일 CSS
st.markdown("""
    <style>
    .map-wrapper { position: relative; width: 100%; height: 500px; }
    .floating-crosshair {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        z-index: 9999; pointer-events: none; color: #FF4B4B; font-size: 30px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📍 해외 소매치기 주의 장소 공유")

# 3. 코드 내 데이터 저장소 (여기에 데이터를 추가하면 모든 기기에 반영됩니다)
# 새로운 제보를 확정하려면 아래 리스트에 복사해서 넣으세요.
if 'locations' not in st.session_state:
    st.session_state.locations = [
        {"name": "파리 루브르 박물관", "lat": 48.8606, "lon": 2.3376, "desc": "설문조사단 접근 주의"},
        {"name": "로마 테르미니역", "lat": 41.9009, "lon": 12.5020, "desc": "티켓 머신 근처 소매치기 빈번"},
        {"name": "바르셀로나 람블라스 거리", "lat": 41.3817, "lon": 2.1728, "desc": "오물 뿌리기 수법 주의"}
    ]

# 4. 사이드바: 제보 입력
with st.sidebar:
    st.header("📢 위험 장소 제보")
    with st.form("report_form"):
        new_name = st.text_input("장소 명칭")
        new_lat = st.number_input("위도", value=45.0, format="%.6f")
        new_lon = st.number_input("경도", value=15.0, format="%.6f")
        new_desc = st.text_area("위험 내용")
        submit_button = st.form_submit_button("제보 등록")
        
        if submit_button and new_name:
            st.session_state.locations.append({
                "name": new_name, "lat": new_lat, "lon": new_lon, "desc": new_desc
            })
            st.success("임시 제보 완료! (관리자 승인 후 영구 반영됩니다)")
            st.rerun()

# 5. 지도 표시
st.markdown('<div class="map-wrapper">', unsafe_allow_html=True)
st.markdown('<div class="floating-crosshair">+</div>', unsafe_allow_html=True)

m = folium.Map(location=[45.0, 15.0], zoom_start=4)
for loc in st.session_state.locations:
    folium.Marker(
        location=[loc['lat'], loc['lon']],
        popup=f"<b>{loc['name']}</b><br>{loc['desc']}",
        icon=folium.Icon(color='red', icon='warning', prefix='fa')
    ).add_to(m)

st_folium(m, width="100%", height=500)
st.markdown('</div>', unsafe_allow_html=True)

# 6. 관리자용 데이터 복사 도구 (접이식 메뉴)
with st.expander("🛠️ 관리자 전용: 데이터 영구 저장용 코드 추출"):
    st.write("아래 텍스트를 복사해서 코드의 `st.session_state.locations = [...]` 부분에 덮어쓰세요.")
    # 리스트 형식을 코드로 변환해서 보여줌
    st.code(f"st.session_state.locations = {st.session_state.locations}")

# 7. 하단 데이터 표
st.divider()
st.dataframe(pd.DataFrame(st.session_state.locations), use_container_width=True)
