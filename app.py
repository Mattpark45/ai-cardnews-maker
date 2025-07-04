import streamlit as st
import openai
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import base64

# OpenAI 클라이언트 설정
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_card_news_with_dalle(title, subtitle, content_points, style="professional"):
    """DALL-E 3로 카드뉴스 이미지 생성"""
    
    # 스타일별 프롬프트 설정
    style_prompts = {
        "professional": "Clean corporate presentation style with blue and orange gradients",
        "modern": "Modern minimalist design with bold colors and geometric shapes",
        "creative": "Creative infographic style with illustrations and vibrant colors",
        "elegant": "Elegant business design with subtle colors and sophisticated layout"
    }
    
    # 상세한 프롬프트 생성
    detailed_prompt = f"""
    Create a professional Korean business infographic slide with the following specifications:
    
    Title area: "{title}"
    Subtitle area: "{subtitle}"
    
    Design requirements:
    - {style_prompts.get(style, style_prompts["professional"])}
    - Clean layout with designated areas for Korean text
    - Include business-related visual elements (charts, graphs, icons)
    - Leave space at the top for title and subtitle
    - Professional corporate aesthetic
    - High contrast for text readability
    - No English text in the image
    - Size optimized for social media sharing
    
    Visual elements to include:
    - Business people silhouettes or illustrations
    - Data visualization elements
    - Modern office or technology themes
    - Clean background with subtle patterns
    
    Style: Professional infographic, corporate presentation, clean and modern
    """
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=detailed_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"이미지 생성 중 오류가 발생했습니다: {str(e)}")
        return None

def add_korean_text_to_image(image_url, title, subtitle, content_points):
    """생성된 이미지에 한글 텍스트 오버레이 추가"""
    try:
        # 이미지 다운로드
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content)).convert('RGBA')
        
        # 텍스트 레이어 생성
        txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # 폰트 설정 (기본 폰트 사용)
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            subtitle_font = ImageFont.truetype("arial.ttf", 32)
            content_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
        
        # 텍스트 위치 계산
        img_width, img_height = img.size
        
        # 제목 추가
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (img_width - title_width) // 2
        draw.text((title_x, 80), title, font=title_font, fill=(255, 255, 255, 255))
        
        # 부제목 추가
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (img_width - subtitle_width) // 2
        draw.text((subtitle_x, 150), subtitle, font=subtitle_font, fill=(200, 200, 200, 255))
        
        # 내용 포인트 추가
        y_position = 250
        for i, point in enumerate(content_points[:4]):  # 최대 4개 포인트
            draw.text((100, y_position), f"• {point}", font=content_font, fill=(255, 255, 255, 255))
            y_position += 60
        
        # 레이어 합성
        final_img = Image.alpha_composite(img, txt_layer)
        return final_img.convert('RGB')
        
    except Exception as e:
        st.error(f"텍스트 오버레이 중 오류: {str(e)}")
        return None

# Streamlit 앱 메인 코드
def main():
    st.title("🎨 AI 카드뉴스 생성기 (DALL-E 3)")
    st.write("한글 지원이 개선된 DALL-E 3 버전입니다!")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        style = st.selectbox(
            "디자인 스타일",
            ["professional", "modern", "creative", "elegant"],
            format_func=lambda x: {
                "professional": "🏢 프로페셔널",
                "modern": "✨ 모던",
                "creative": "🎨 크리에이티브",
                "elegant": "💎 엘레간트"
            }[x]
        )
    
    # 메인 입력 폼
    with st.form("card_news_form"):
        st.header("📝 카드뉴스 내용 입력")
        
        title = st.text_input("제목", placeholder="예: 디지털 마케팅 트렌드")
        subtitle = st.text_input("부제목", placeholder="예: 2024년 주목할 IT 기술들")
        
        st.write("**주요 내용 (최대 4개)**")
        content_points = []
        for i in range(4):
            point = st.text_input(f"포인트 {i+1}", key=f"point_{i}")
            if point:
                content_points.append(point)
        
        submitted = st.form_submit_button("🚀 카드뉴스 생성", type="primary")
    
    # 생성 버튼 클릭 시
    if submitted and title and subtitle:
        with st.spinner("✨ AI가 카드뉴스를 생성하고 있습니다..."):
            # 1단계: DALL-E 3로 기본 이미지 생성
            image_url = generate_card_news_with_dalle(title, subtitle, content_points, style)
            
            if image_url:
                # 2단계: 한글 텍스트 오버레이 추가
                final_image = add_korean_text_to_image(image_url, title, subtitle, content_points)
                
                if final_image:
                    st.success("🎉 카드뉴스가 성공적으로 생성되었습니다!")
                    
                    # 이미지 표시
                    st.image(final_image, caption="생성된 카드뉴스", use_container_width=True)
                    
                    # 다운로드 버튼
                    buf = BytesIO()
                    final_image.save(buf, format="PNG")
                    btn = st.download_button(
                        label="📥 이미지 다운로드",
                        data=buf.getvalue(),
                        file_name=f"{title}_카드뉴스.png",
                        mime="image/png"
                    )
                else:
                    st.error("텍스트 오버레이 추가에 실패했습니다.")
            else:
                st.error("이미지 생성에 실패했습니다.")
    
    elif submitted:
        st.warning("⚠️ 제목과 부제목을 입력해주세요!")

if __name__ == "__main__":
    main()
