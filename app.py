import streamlit as st
import requests
import json
from PIL import Image
import io
import time

# Streamlit 페이지 설정
st.set_page_config(
    page_title="카드뉴스 생성기",
    page_icon="📱",
    layout="wide"
)

st.title("📱 카드뉴스 생성기")
st.markdown("---")

# OpenAI API 키 입력
api_key = st.text_input("OpenAI API 키를 입력하세요:", type="password")

if not api_key:
    st.warning("⚠️ OpenAI API 키를 입력해주세요.")
    st.stop()

# 입력 폼
with st.form("card_news_form"):
    st.markdown("### 📝 카드뉴스 내용 입력")
    
    title = st.text_input("제목:", placeholder="예: 2025 디지털 마케팅 트렌드")
    subtitle = st.text_input("부제목:", placeholder="예: 성공하는 브랜드들의 필수 전략")
    
    st.markdown("**주요 내용 4가지:**")
    content1 = st.text_input("내용 1:", placeholder="첫 번째 주요 포인트")
    content2 = st.text_input("내용 2:", placeholder="두 번째 주요 포인트")
    content3 = st.text_input("내용 3:", placeholder="세 번째 주요 포인트")
    content4 = st.text_input("내용 4:", placeholder="네 번째 주요 포인트")
    
    # 스타일 선택
    style = st.selectbox(
        "디자인 스타일:",
        ["모던", "미니멀", "비즈니스", "창의적", "전문적"]
    )
    
    color_scheme = st.selectbox(
        "컬러 테마:",
        ["블루&오렌지", "그린&화이트", "퍼플&골드", "레드&그레이", "다크&네온"]
    )
    
    submitted = st.form_submit_button("🎨 카드뉴스 생성하기")

# 이미지 생성 함수
def generate_image(prompt, api_key):
    """DALL-E API를 사용하여 이미지 생성"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "quality": "standard"
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            image_url = result['data'][0]['url']
            
            # 이미지 다운로드
            img_response = requests.get(image_url)
            img = Image.open(io.BytesIO(img_response.content))
            return img
        else:
            st.error(f"API 오류: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"이미지 생성 중 오류: {str(e)}")
        return None

# 프롬프트 생성 함수
def create_prompts(title, subtitle, contents, style, color_scheme):
    """5장의 카드뉴스용 프롬프트 생성"""
    
    # 스타일 매핑
    style_map = {
        "모던": "modern, clean, geometric shapes",
        "미니멀": "minimalist, simple, lots of white space",
        "비즈니스": "professional, corporate, sleek",
        "창의적": "creative, artistic, dynamic",
        "전문적": "professional, sophisticated, premium"
    }
    
    color_map = {
        "블루&오렌지": "blue and orange color scheme",
        "그린&화이트": "green and white color scheme", 
        "퍼플&골드": "purple and gold color scheme",
        "레드&그레이": "red and gray color scheme",
        "다크&네온": "dark background with neon accents"
    }
    
    base_style = f"{style_map[style]}, {color_map[color_scheme]}"
    
    prompts = []
    
    # 1. 표지 카드
    cover_prompt = f"""
    Create a {base_style} social media card design for cover page. 
    Main title: "{title}"
    Subtitle: "{subtitle}"
    Design should be eye-catching with large, readable Korean text overlay. 
    Include subtle business/marketing themed background elements.
    Card format, vertical orientation, professional layout.
    """
    prompts.append(("표지", cover_prompt))
    
    # 2-5. 내용 카드들
    for i, content in enumerate(contents, 1):
        content_prompt = f"""
        Create a {base_style} social media card design for content slide {i}.
        Main text: "{content}"
        Design should have large, clear Korean text as the focal point.
        Include relevant icons or illustrations related to digital marketing.
        Card format, vertical orientation, clean and readable layout.
        Text should be prominent and easy to read.
        """
        prompts.append((f"내용 {i}", content_prompt))
    
    return prompts

# 메인 로직
if submitted:
    if not all([title, subtitle, content1, content2, content3, content4]):
        st.error("⚠️ 모든 필드를 입력해주세요!")
    else:
        contents = [content1, content2, content3, content4]
        
        st.markdown("## 🎨 카드뉴스 생성 중...")
        
        # 프롬프트 생성
        prompts = create_prompts(title, subtitle, contents, style, color_scheme)
        
        # 진행 상황 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 이미지들을 저장할 리스트
        generated_images = []
        
        # 5장의 카드 생성
        for i, (card_name, prompt) in enumerate(prompts):
            status_text.text(f"🎨 {card_name} 생성 중... ({i+1}/5)")
            
            # 이미지 생성
            img = generate_image(prompt, api_key)
            
            if img:
                generated_images.append((card_name, img))
                st.success(f"✅ {card_name} 완성!")
            else:
                st.error(f"❌ {card_name} 생성 실패")
                
            # 진행률 업데이트
            progress_bar.progress((i + 1) / 5)
            
            # API 호출 간격 (Rate limit 방지)
            if i < 4:  # 마지막이 아니면 대기
                time.sleep(2)
        
        progress_bar.progress(1.0)
        status_text.text("🎉 모든 카드 생성 완료!")
        
        # 결과 표시
        if generated_images:
            st.markdown("## 📱 생성된 카드뉴스")
            st.markdown("---")
            
            # 탭으로 각 카드 표시
            tab_names = [name for name, _ in generated_images]
            tabs = st.tabs(tab_names)
            
            for i, (tab, (card_name, img)) in enumerate(zip(tabs, generated_images)):
                with tab:
                    st.image(img, caption=f"{card_name}", use_column_width=True)
                    
                    # 다운로드 버튼
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label=f"💾 {card_name} 다운로드",
                        data=byte_im,
                        file_name=f"card_{i+1}_{card_name}.png",
                        mime="image/png"
                    )
            
            # 전체 다운로드 옵션
            st.markdown("### 📦 전체 다운로드")
            if st.button("🗂️ 모든 카드 ZIP으로 다운로드"):
                import zipfile
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for i, (card_name, img) in enumerate(generated_images):
                        img_buffer = io.BytesIO()
                        img.save(img_buffer, format='PNG')
                        zip_file.writestr(f"card_{i+1}_{card_name}.png", img_buffer.getvalue())
                
                st.download_button(
                    label="📁 ZIP 파일 다운로드",
                    data=zip_buffer.getvalue(),
                    file_name=f"카드뉴스_{title}.zip",
                    mime="application/zip"
                )

# 사이드바 정보
with st.sidebar:
    st.markdown("## ℹ️ 사용 방법")
    st.markdown("""
    1. **OpenAI API 키** 입력
    2. **제목과 부제목** 작성
    3. **주요 내용 4가지** 입력
    4. **스타일과 컬러** 선택
    5. **생성하기** 버튼 클릭
    
    ---
    
    ### 📋 생성되는 카드
    - **표지 카드** (제목 + 부제목)
    - **내용 카드 4장** (각각의 주요 포인트)
    
    ### ⏱️ 소요 시간
    - 약 **2-3분** (5장 생성)
    
    ### 💡 팁
    - 내용은 **간결하고 명확**하게
    - 한글 텍스트가 **잘 보이도록** 설계됨
    """)
    
    st.markdown("---")
    st.markdown("**Made with ❤️ by Monica**")
