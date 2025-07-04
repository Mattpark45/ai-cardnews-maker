import streamlit as st
from openai import OpenAI
import requests
import json
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap
from io import BytesIO
import os

# 페이지 설정
st.set_page_config(
    page_title="AI 카드뉴스 생성기",
    page_icon="🎨",
    layout="wide"
)

# OpenAI 클라이언트 초기화
openai_api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
leonardo_api_key = st.secrets.get("LEONARDO_API_KEY") or os.getenv("LEONARDO_API_KEY")

if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
else:
    client = None

def create_content_structure(topic, industry, platform):
    """GPT를 사용해 캐러셀 콘텐츠 구조 생성"""
    
    platform_specs = {
        "Instagram": "시각적 임팩트 중심, 해시태그 활용, 젊은 층 타겟",
        "LinkedIn": "전문성과 인사이트 중심, B2B 네트워킹, 비즈니스 톤",
        "Facebook": "스토리텔링 중심, 다양한 연령층, 공감대 형성"
    }
    
    prompt = f"""
    주제: {topic}
    업종: {industry}
    플랫폼: {platform}
    
    {platform_specs.get(platform, "")}
    
    위 조건에 맞는 카드뉴스 캐러셀을 5장으로 구성해주세요.
    
    다음 JSON 형식으로 응답해주세요:
    {{
        "slides": [
            {{
                "slide_number": 1,
                "type": "title",
                "title": "메인 제목 (20자 이내)",
                "subtitle": "부제목 (30자 이내)",
                "visual_prompt": "이미지 생성을 위한 영어 프롬프트",
                "background_color": "색상코드"
            }},
            {{
                "slide_number": 2,
                "type": "content",
                "title": "핵심 포인트 1 (15자 이내)",
                "content": "설명 내용 (50자 이내)",
                "visual_prompt": "이미지 생성을 위한 영어 프롬프트",
                "background_color": "색상코드"
            }},
            {{
                "slide_number": 3,
                "type": "content", 
                "title": "핵심 포인트 2 (15자 이내)",
                "content": "설명 내용 (50자 이내)",
                "visual_prompt": "이미지 생성을 위한 영어 프롬프트",
                "background_color": "색상코드"
            }},
            {{
                "slide_number": 4,
                "type": "content",
                "title": "핵심 포인트 3 (15자 이내)", 
                "content": "설명 내용 (50자 이내)",
                "visual_prompt": "이미지 생성을 위한 영어 프롬프트",
                "background_color": "색상코드"
            }},
            {{
                "slide_number": 5,
                "type": "cta",
                "title": "마무리 메시지 (20자 이내)",
                "cta_text": "행동 유도 문구 (15자 이내)",
                "visual_prompt": "이미지 생성을 위한 영어 프롬프트",
                "background_color": "색상코드"
            }}
        ]
    }}
    
    주의사항:
    - 모든 텍스트는 한국어로
    - visual_prompt는 영어로 작성
    - 글자 수 제한을 엄격히 준수
    - {platform}에 최적화된 톤앤매너 사용
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        # JSON 파싱
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        json_str = content[start_idx:end_idx]
        
        return json.loads(json_str)
    
    except Exception as e:
        st.error(f"콘텐츠 구조 생성 오류: {str(e)}")
        return None

def generate_background_image(prompt):
    """Leonardo AI로 배경 이미지 생성"""
    
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    
    payload = {
        "height": 1080,
        "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",
        "prompt": f"{prompt}, high quality, professional design, clean layout, modern style",
        "width": 1080,
        "num_images": 1,
        "presetStyle": "DYNAMIC",
        "scheduler": "DPM_SOLVER",
        "public": False,
        "promptMagic": True
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {leonardo_api_key}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            generation_id = response.json()["sdGenerationJob"]["generationId"]
            
            # 생성 완료 대기
            for _ in range(30):  # 최대 30초 대기
                check_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
                check_response = requests.get(check_url, headers=headers)
                
                if check_response.status_code == 200:
                    result = check_response.json()
                    if result["generations_by_pk"]["status"] == "COMPLETE":
                        image_url = result["generations_by_pk"]["generated_images"][0]["url"]
                        return image_url
                
                time.sleep(2)
        
        return None
        
    except Exception as e:
        st.error(f"이미지 생성 오류: {str(e)}")
        return None

def get_platform_specs(platform):
    """플랫폼별 스펙 반환"""
    specs = {
        "Instagram": {
            "size": (1080, 1080),
            "title_font_size": 48,
            "content_font_size": 32,
            "subtitle_font_size": 36,
            "cta_font_size": 28,
            "padding": 80,
            "title_color": "#FFFFFF",
            "content_color": "#F0F0F0",
            "overlay_opacity": 0.6
        },
        "LinkedIn": {
            "size": (1200, 627),
            "title_font_size": 44,
            "content_font_size": 28,
            "subtitle_font_size": 32,
            "cta_font_size": 24,
            "padding": 60,
            "title_color": "#FFFFFF",
            "content_color": "#E8E8E8",
            "overlay_opacity": 0.7
        },
        "Facebook": {
            "size": (1200, 630),
            "title_font_size": 46,
            "content_font_size": 30,
            "subtitle_font_size": 34,
            "cta_font_size": 26,
            "padding": 70,
            "title_color": "#FFFFFF", 
            "content_color": "#F5F5F5",
            "overlay_opacity": 0.65
        }
    }
    
    return specs.get(platform, specs["Instagram"])

def wrap_text(text, font, max_width):
    """텍스트를 지정된 폭에 맞게 줄바꿈"""
    lines = []
    
    # 단어별로 분할 (한국어 고려)
    words = text.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                lines.append(word)
    
    if current_line:
        lines.append(current_line)
    
    return lines

def create_cardnews_image(slide_data, platform):
    """텍스트가 포함된 카드뉴스 이미지 생성"""
    
    specs = get_platform_specs(platform)
    
    # 배경 이미지 생성
    bg_url = generate_background_image(slide_data["visual_prompt"])
    
    if not bg_url:
        # 기본 그라데이션 배경 생성
        img = Image.new('RGB', specs["size"], color=slide_data.get("background_color", "#667eea"))
    else:
        try:
            response = requests.get(bg_url)
            img = Image.open(BytesIO(response.content))
            img = img.resize(specs["size"], Image.Resampling.LANCZOS)
        except:
            img = Image.new('RGB', specs["size"], color=slide_data.get("background_color", "#667eea"))
    
    # 오버레이 추가 (가독성을 위해)
    overlay = Image.new('RGBA', specs["size"], (0, 0, 0, int(255 * specs["overlay_opacity"])))
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.convert('RGB')
    
    draw = ImageDraw.Draw(img)
    
    # 폰트 설정 (시스템 폰트 사용)
    try:
        title_font = ImageFont.truetype("malgun.ttf", specs["title_font_size"])
        content_font = ImageFont.truetype("malgun.ttf", specs["content_font_size"]) 
        subtitle_font = ImageFont.truetype("malgun.ttf", specs["subtitle_font_size"])
        cta_font = ImageFont.truetype("malgun.ttf", specs["cta_font_size"])
    except:
        try:
            title_font = ImageFont.truetype("NanumGothic.ttf", specs["title_font_size"])
            content_font = ImageFont.truetype("NanumGothic.ttf", specs["content_font_size"])
            subtitle_font = ImageFont.truetype("NanumGothic.ttf", specs["subtitle_font_size"])
            cta_font = ImageFont.truetype("NanumGothic.ttf", specs["cta_font_size"])
        except:
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            cta_font = ImageFont.load_default()
    
    # 텍스트 배치
    y_position = specs["padding"]
    max_text_width = specs["size"][0] - (specs["padding"] * 2)
    
    # 슬라이드 타입별 텍스트 배치
    if slide_data["type"] == "title":
        # 제목 슬라이드
        title_lines = wrap_text(slide_data["title"], title_font, max_text_width)
        
        for line in title_lines:
            bbox = title_font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x_position = (specs["size"][0] - text_width) // 2
            
            draw.text((x_position, y_position), line, 
                     fill=specs["title_color"], font=title_font)
            y_position += bbox[3] - bbox[1] + 20
        
        # 부제목
        if "subtitle" in slide_data:
            y_position += 40
            subtitle_lines = wrap_text(slide_data["subtitle"], subtitle_font, max_text_width)
            
            for line in subtitle_lines:
                bbox = subtitle_font.getbbox(line)
                text_width = bbox[2] - bbox[0]
                x_position = (specs["size"][0] - text_width) // 2
                
                draw.text((x_position, y_position), line,
                         fill=specs["content_color"], font=subtitle_font)
                y_position += bbox[3] - bbox[1] + 15
    
    elif slide_data["type"] == "content":
        # 콘텐츠 슬라이드
        title_lines = wrap_text(slide_data["title"], title_font, max_text_width)
        
        for line in title_lines:
            bbox = title_font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x_position = (specs["size"][0] - text_width) // 2
            
            draw.text((x_position, y_position), line,
                     fill=specs["title_color"], font=title_font)
            y_position += bbox[3] - bbox[1] + 30
        
        # 콘텐츠
        y_position += 60
        content_lines = wrap_text(slide_data["content"], content_font, max_text_width)
        
        for line in content_lines:
            bbox = content_font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x_position = (specs["size"][0] - text_width) // 2
            
            draw.text((x_position, y_position), line,
                     fill=specs["content_color"], font=content_font)
            y_position += bbox[3] - bbox[1] + 20
    
    elif slide_data["type"] == "cta":
        # CTA 슬라이드
        title_lines = wrap_text(slide_data["title"], title_font, max_text_width)
        
        for line in title_lines:
            bbox = title_font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x_position = (specs["size"][0] - text_width) // 2
            
            draw.text((x_position, y_position), line,
                     fill=specs["title_color"], font=title_font)
            y_position += bbox[3] - bbox[1] + 40
        
        # CTA 텍스트
        if "cta_text" in slide_data:
            y_position += 80
            cta_lines = wrap_text(slide_data["cta_text"], cta_font, max_text_width)
            
            for line in cta_lines:
                bbox = cta_font.getbbox(line)
                text_width = bbox[2] - bbox[0]
                x_position = (specs["size"][0] - text_width) // 2
                
                # CTA 버튼 스타일 배경
                button_padding = 20
                button_width = text_width + (button_padding * 2)
                button_height = bbox[3] - bbox[1] + (button_padding * 2)
                button_x = x_position - button_padding
                button_y = y_position - button_padding
                
                draw.rounded_rectangle(
                    [button_x, button_y, button_x + button_width, button_y + button_height],
                    radius=25, fill="#FF6B6B"
                )
                
                draw.text((x_position, y_position), line,
                         fill="#FFFFFF", font=cta_font)
                y_position += bbox[3] - bbox[1] + 20
    
    return img

def generate_cardnews_series(topic, industry, platform):
    """완전한 카드뉴스 시리즈 생성"""
    
    # 1. 콘텐츠 구조 생성
    with st.spinner("콘텐츠 구조를 생성하고 있습니다..."):
        content_structure = create_content_structure(topic, industry, platform)
    
    if not content_structure:
        return None
    
    # 2. 각 슬라이드 이미지 생성
    cardnews_images = []
    
    for i, slide in enumerate(content_structure["slides"]):
        with st.spinner(f"카드뉴스 {i+1}/5 생성 중..."):
            img = create_cardnews_image(slide, platform)
            cardnews_images.append(img)
    
    return cardnews_images, content_structure

# Streamlit UI
def main():
    st.title("🎨 AI 카드뉴스 생성기")
    st.markdown("**주제와 업종을 입력하면 완성된 카드뉴스 캐러셀을 생성합니다!**")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # API 키 확인
        if not client:
            st.error("OpenAI API 키가 설정되지 않았습니다.")
            st.stop()
        
        if not leonardo_api_key:
            st.error("Leonardo AI API 키가 설정되지 않았습니다.")
            st.stop()
        
        st.success("✅ API 키 설정 완료")
    
    # 메인 입력 폼
    col1, col2 = st.columns(2)
    
    with col1:
        topic = st.text_input(
            "📝 주제",
            placeholder="예: 디지털 마케팅 트렌드",
            help="카드뉴스로 만들고 싶은 주제를 입력하세요"
        )
    
    with col2:
        industry = st.selectbox(
            "🏢 업종",
            ["IT/테크", "마케팅/광고", "교육", "금융", "의료/헬스케어", 
             "패션/뷰티", "음식/요리", "여행", "부동산", "기타"]
        )
    
    platform = st.selectbox(
        "📱 플랫폼",
        ["Instagram", "LinkedIn", "Facebook"],
        help="각 플랫폼에 최적화된 사이즈와 톤앤매너로 생성됩니다"
    )
    
    # 생성 버튼
    if st.button("🚀 카드뉴스 생성", type="primary", use_container_width=True):
        if not topic:
            st.warning("주제를 입력해주세요!")
            return
        
        # 카드뉴스 생성
        result = generate_cardnews_series(topic, industry, platform)
        
        if result:
            images, content_structure = result
            
            st.success("✅ 카드뉴스 생성 완료!")
            
            # 결과 표시
            st.header("📱 생성된 카드뉴스")
            
            # 탭으로 구분
            tabs = st.tabs([f"슬라이드 {i+1}" for i in range(len(images))])
            
            for i, (tab, img) in enumerate(zip(tabs, images)):
                with tab:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.image(img, use_column_width=True)
                    
                    with col2:
                        slide_info = content_structure["slides"][i]
                        st.markdown(f"**타입:** {slide_info['type']}")
                        st.markdown(f"**제목:** {slide_info['title']}")
                        
                        if slide_info["type"] == "title" and "subtitle" in slide_info:
                            st.markdown(f"**부제목:** {slide_info['subtitle']}")
                        elif slide_info["type"] == "content":
                            st.markdown(f"**내용:** {slide_info['content']}")
                        elif slide_info["type"] == "cta" and "cta_text" in slide_info:
                            st.markdown(f"**CTA:** {slide_info['cta_text']}")
                        
                        # 다운로드 버튼
                        buf = BytesIO()
                        img.save(buf, format='PNG')
                        st.download_button(
                            label=f"슬라이드 {i+1} 다운로드",
                            data=buf.getvalue(),
                            file_name=f"cardnews_slide_{i+1}.png",
                            mime="image/png"
                        )
            
            # 전체 콘텐츠 구조 표시
            with st.expander("📋 생성된 콘텐츠 구조"):
                st.json(content_structure)
        
        else:
            st.error("카드뉴스 생성에 실패했습니다. 다시 시도해주세요.")

if __name__ == "__main__":
    main()
