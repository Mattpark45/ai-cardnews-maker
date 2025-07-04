import streamlit as st
import requests
import time
import os

st.set_page_config(
    page_title="AI 카드뉴스 메이커",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 AI 카드뉴스 메이커")
st.subheader("텍스트 입력 → 자동 카드뉴스 생성")

# API 키 (Streamlit secrets에서 가져오기)
leonardo_api_key = st.secrets.get("LEONARDO_API_KEY", "")

def generate_image(prompt):
    if not leonardo_api_key:
        st.error("Leonardo API 키가 설정되지 않았습니다.")
        return None
        
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    
    headers = {
        "Authorization": f"Bearer {leonardo_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": f"Professional card news design: {prompt}, modern, clean, marketing style",
        "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",
        "width": 1024,
        "height": 1024,
        "num_images": 1
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            generation_id = response.json()["sdGenerationJob"]["generationId"]
            
            # 결과 대기
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(30):  # 최대 30번 체크 (90초)
                result_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
                result = requests.get(result_url, headers=headers)
                
                if result.status_code == 200:
                    status = result.json()["generations_by_pk"]["status"]
                    status_text.text(f"상태: {status}")
                    progress_bar.progress((i + 1) / 30)
                    
                    if status == "COMPLETE":
                        image_url = result.json()["generations_by_pk"]["generated_images"][0]["url"]
                        status_text.text("✅ 완료!")
                        progress_bar.progress(1.0)
                        return image_url
                        
                time.sleep(3)
                
        return None
    except Exception as e:
        st.error(f"오류 발생: {str(e)}")
        return None

# 메인 UI
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 입력")
    
    platform = st.selectbox(
        "플랫폼 선택",
        ["Instagram", "Facebook", "LinkedIn", "Twitter"]
    )
    
    industry = st.selectbox(
        "업종 선택",
        ["교육", "이커머스", "HR", "마케팅", "IT", "일반"]
    )
    
    user_prompt = st.text_area(
        "카드뉴스 내용을 입력하세요",
        placeholder="예: 디지털 마케팅 성과 향상을 위한 5가지 팁",
        height=150
    )
    
    generate_btn = st.button("🚀 카드뉴스 생성", type="primary", use_container_width=True)

with col2:
    st.header("🎨 결과")
    
    if generate_btn and user_prompt:
        with st.spinner("AI가 카드뉴스를 생성하고 있습니다..."):
            # 프롬프트 개선
            enhanced_prompt = f"{platform} card news about {user_prompt} for {industry} industry"
            
            # 이미지 생성
            image_url = generate_image(enhanced_prompt)
            
            if image_url:
                st.image(image_url, caption="생성된 카드뉴스")
                st.success("✅ 카드뉴스 생성 완료!")
                
                # 다운로드 링크
                st.markdown(f"[📥 이미지 다운로드]({image_url})")
            else:
                st.error("이미지 생성에 실패했습니다.")
    
    elif generate_btn:
        st.warning("내용을 입력해주세요!")

# 사이드바
with st.sidebar:
    st.header("ℹ️ 사용법")
    st.markdown("""
    1. **플랫폼**과 **업종**을 선택하세요
    2. **카드뉴스 내용**을 입력하세요
    3. **생성 버튼**을 클릭하세요
    4. 생성된 이미지를 다운로드하세요
    """)
    
    st.header("🎯 예시")
    st.markdown("""
    - "새해 마케팅 전략 5가지"
    - "HR 채용 트렌드 2025"
    - "이커머스 성장 비법"
    """)
