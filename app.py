import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import requests
from pathlib import Path

# 폰트 다운로드 및 설정
@st.cache_data
def download_korean_fonts():
    """한글 폰트 자동 다운로드 및 설정"""
    
    fonts_dir = Path("fonts")
    fonts_dir.mkdir(exist_ok=True)
    
    # 나눔고딕 폰트 URL (Google Fonts에서 제공)
    font_urls = {
        "NanumGothic-Regular.ttf": "https://github.com/naver/nanumfont/raw/master/TTF/NanumGothic.ttf",
        "NanumGothic-Bold.ttf": "https://github.com/naver/nanumfont/raw/master/TTF/NanumGothicBold.ttf"
    }
    
    downloaded_fonts = {}
    
    for font_name, url in font_urls.items():
        font_path = fonts_dir / font_name
        
        # 이미 존재하면 스킵
        if font_path.exists():
            downloaded_fonts[font_name] = str(font_path)
            continue
            
        try:
            with st.spinner(f"한글 폰트 다운로드 중... ({font_name})"):
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                with open(font_path, 'wb') as f:
                    f.write(response.content)
                    
                downloaded_fonts[font_name] = str(font_path)
                st.success(f"✅ {font_name} 다운로드 완료!")
                
        except Exception as e:
            st.warning(f"⚠️ {font_name} 다운로드 실패: {e}")
            continue
    
    return downloaded_fonts

def get_korean_font(size=60, weight='regular'):
    """한글 폰트 로드 (자동 다운로드 포함)"""
    
    # 폰트 다운로드
    fonts = download_korean_fonts()
    
    # 폰트 선택
    if weight == 'bold' and "NanumGothic-Bold.ttf" in fonts:
        font_path = fonts["NanumGothic-Bold.ttf"]
    elif "NanumGothic-Regular.ttf" in fonts:
        font_path = fonts["NanumGothic-Regular.ttf"]
    else:
        st.error("❌ 한글 폰트를 로드할 수 없습니다!")
        return None
    
    try:
        return ImageFont.truetype(font_path, size)
    except Exception as e:
        st.error(f"폰트 로딩 오류: {e}")
        return None

def create_gradient_background(width, height, color_scheme):
    """그라데이션 배경 생성"""
    
    color_schemes = {
        "블루 그라데이션": [(52, 73, 219), (73, 150, 219)],
        "퍼플 그라데이션": [(106, 90, 205), (147, 51, 234)],
        "그린 그라데이션": [(46, 204, 113), (39, 174, 96)],
        "오렌지 그라데이션": [(230, 126, 34), (231, 76, 60)],
        "다크 그라데이션": [(44, 62, 80), (52, 73, 94)],
        "핑크 그라데이션": [(253, 121, 168), (232, 93, 117)],
        "민트 그라데이션": [(26, 188, 156), (22, 160, 133)],
        "선셋 그라데이션": [(255, 94, 77), (255, 154, 0)]
    }
    
    start_color, end_color = color_schemes.get(color_scheme, color_schemes["블루 그라데이션"])
    
    # 이미지 생성
    img = Image.new('RGB', (width, height))
    
    # 세로 그라데이션
    for y in range(height):
        ratio = y / height
        
        # 색상 보간 (부드러운 그라데이션을 위한 ease-in-out)
        ratio = ratio * ratio * (3.0 - 2.0 * ratio)  # smooth step
        
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        
        # 한 줄씩 그리기
        for x in range(width):
            img.putpixel((x, y), (r, g, b))
    
    return img

def get_text_dimensions(text, font):
    """텍스트의 정확한 크기 측정"""
    # 임시 이미지로 크기 측정
    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def wrap_text(text, font, max_width):
    """개선된 텍스트 자동 줄바꿈"""
    if not text:
        return []
    
    lines = []
    words = text.split()
    
    if not words:
        return [text]
    
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " " if current_line else word + " "
        text_width, _ = get_text_dimensions(test_line.strip(), font)
        
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
                current_line = word + " "
            else:
                # 단어가 너무 길면 강제로 추가
                lines.append(word)
                current_line = ""
    
    if current_line:
        lines.append(current_line.strip())
    
    return lines

def draw_text_with_shadow(draw, position, text, font, text_color='white', shadow_color=(0, 0, 0, 128), shadow_offset=(2, 2)):
    """그림자 효과가 있는 텍스트 그리기"""
    x, y = position
    
    # 그림자 그리기
    draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=shadow_color)
    
    # 메인 텍스트 그리기
    draw.text((x, y), text, font=font, fill=text_color)

def create_perfect_korean_card(title, subtitle, content, color_scheme, width=1080, height=1920):
    """완벽한 한글 카드뉴스 생성"""
    
    # 배경 생성
    img = create_gradient_background(width, height, color_scheme)
    draw = ImageDraw.Draw(img)
    
    # 폰트 로드
    title_font = get_korean_font(90, 'bold')
    subtitle_font = get_korean_font(60, 'regular') 
    content_font = get_korean_font(45, 'regular')
    
    if not title_font:
        return None
    
    margin = 80
    y_position = 150
    
    # 1. 제목 그리기
    if title:
        title_lines = wrap_text(title, title_font, width - margin * 2)
        
        for i, line in enumerate(title_lines):
            text_width, text_height = get_text_dimensions(line, title_font)
            x = (width - text_width) // 2
            
            # 제목 배경 (둥근 모서리 효과)
            padding = 40
            bg_color = (0, 0, 0, 160)  # 반투명 검은색
            
            # 배경 사각형
            draw.rectangle([x - padding, y_position - 15, 
                          x + text_width + padding, y_position + text_height + 15], 
                         fill=bg_color)
            
            # 텍스트 그리기 (그림자 효과)
            draw_text_with_shadow(draw, (x, y_position), line, title_font, 'white')
            
            y_position += text_height + 20
        
        y_position += 80
    
    # 2. 부제목 그리기
    if subtitle:
        subtitle_lines = wrap_text(subtitle, subtitle_font, width - margin * 2)
        
        for line in subtitle_lines:
            text_width, text_height = get_text_dimensions(line, subtitle_font)
            x = (width - text_width) // 2
            
            # 부제목 배경
            padding = 30
            bg_color = (255, 255, 255, 220)  # 반투명 흰색
            
            draw.rectangle([x - padding, y_position - 10, 
                          x + text_width + padding, y_position + text_height + 10], 
                         fill=bg_color)
            
            # 텍스트 그리기
            draw.text((x, y_position), line, font=subtitle_font, fill='#2c3e50')
            
            y_position += text_height + 15
        
        y_position += 120
    
    # 3. 내용 그리기
    if content:
        # 내용을 줄 단위로 분리
        content_lines = content.split('\n')
        all_lines = []
        
        for line in content_lines:
            if line.strip():
                if line.strip().startswith('•') or line.strip().startswith('-'):
                    # 불릿 포인트 처리
                    wrapped_lines = wrap_text(line, content_font, width - margin * 2 - 40)
                else:
                    wrapped_lines = wrap_text(line, content_font, width - margin * 2)
                all_lines.extend(wrapped_lines)
            else:
                all_lines.append("")  # 빈 줄 유지
        
        # 내용 전체 영역 크기 계산
        line_height = 65
        max_line_width = 0
        content_height = 0
        
        for line in all_lines:
            if line:
                line_width, _ = get_text_dimensions(line, content_font)
                max_line_width = max(max_line_width, line_width)
                content_height += line_height
            else:
                content_height += line_height // 2
        
        # 내용 전체 배경
        bg_padding = 50
        bg_x1 = (width - max_line_width) // 2 - bg_padding
        bg_x2 = (width + max_line_width) // 2 + bg_padding
        bg_y1 = y_position - 30
        bg_y2 = y_position + content_height + 30
        
        # 배경 그리기 (둥근 모서리 느낌)
        draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=(255, 255, 255, 230))
        
        # 각 줄 그리기
        for line in all_lines:
            if line:
                # 불릿 포인트 스타일링
                if line.strip().startswith('•'):
                    line = line.replace('•', '●')  # 더 진한 불릿
                elif line.strip().startswith('-'):
                    line = line.replace('-', '●')
                
                text_width, text_height = get_text_dimensions(line, content_font)
                x = (width - text_width) // 2
                
                # 불릿 포인트면 왼쪽 정렬
                if line.strip().startswith('●'):
                    x = bg_x1 + 30
                
                # 텍스트 그리기
                draw.text((x, y_position), line, font=content_font, fill='#2c3e50')
                y_position += line_height
            else:
                y_position += line_height // 2
    
    return img

# Streamlit 메인 앱
def main():
    st.set_page_config(
        page_title="한글 카드뉴스 생성기", 
        page_icon="🎨", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 스타일링
    st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #2c3e50;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-title">🎨 한글 카드뉴스 생성기</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">완벽한 한글 렌더링으로 전문적인 카드뉴스를 만들어보세요!</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("🎨 디자인 설정")
        
        color_scheme = st.selectbox(
            "🌈 배경 색상",
            ["블루 그라데이션", "퍼플 그라데이션", "그린 그라데이션", 
             "오렌지 그라데이션", "다크 그라데이션", "핑크 그라데이션",
             "민트 그라데이션", "선셋 그라데이션"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 📱 카드 정보")
        st.info("**크기:** 1080 x 1920px\n**최적화:** Instagram Story")
        
        st.markdown("### 🔤 폰트 정보")
        st.success("**나눔고딕** 자동 다운로드\n한글 완벽 지원 보장!")
    
    # 메인 콘텐츠
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.header("✏️ 카드 내용 입력")
        
        with st.form("card_form", clear_on_submit=False):
            title = st.text_input(
                "📌 제목 (필수)", 
                value="똑똑한 예산관리!",
                help="카드의 메인 제목을 입력하세요",
                placeholder="예: 결혼준비 완벽 가이드"
            )
            
            subtitle = st.text_input(
                "📝 부제목 (선택)", 
                value="신혼부부를 위한 필수 팁",
                help="제목 아래 들어갈 부제목을 입력하세요",
                placeholder="예: 전문가가 알려주는 비밀"
            )
            
            content = st.text_area(
                "📄 내용 (선택)", 
                value="""● 예식장 예약 시기별 할인율 비교
● 드레스 렌탈 vs 구매 비용 분석  
● 허니문 패키지 가격 협상 팁
● 신혼집 준비 우선순위 체크리스트
● 웨딩 플래너 선택 기준""",
                height=250,
                help="카드에 들어갈 상세 내용을 입력하세요. '●' 또는 '-'로 시작하면 불릿 포인트가 됩니다.",
                placeholder="● 첫 번째 팁\n● 두 번째 팁\n● 세 번째 팁"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button("🎨 카드 생성하기", use_container_width=True, type="primary")
            with col_btn2:
                clear_form = st.form_submit_button("🗑️ 초기화", use_container_width=True)
    
    with col2:
        st.header("👀 미리보기")
        
        # 입력 내용 미리보기
        with st.container():
            if title:
                st.markdown(f"**📌 제목:** {title}")
            if subtitle:
                st.markdown(f"**📝 부제목:** {subtitle}")
            if content:
                st.markdown("**📄 내용:**")
                preview_content = content[:150] + "..." if len(content) > 150 else content
                st.text(preview_content)
        
        # 통계 정보
        if any([title, subtitle, content]):
            st.markdown("---")
            st.markdown("### 📊 텍스트 통계")
            
            total_chars = len(title or "") + len(subtitle or "") + len(content or "")
            lines_count = len(content.split('\n')) if content else 0
            
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("총 글자수", total_chars)
            with col_stat2:
                st.metric("내용 줄수", lines_count)
    
    # 카드 생성 처리
    if clear_form:
        st.rerun()
    
    if submitted:
        if not title:
            st.error("❌ 제목을 입력해주세요!")
            return
        
        with st.spinner("🎨 전문적인 한글 카드를 생성하고 있습니다..."):
            try:
                card_img = create_perfect_korean_card(
                    title=title,
                    subtitle=subtitle, 
                    content=content,
                    color_scheme=color_scheme
                )
                
                if card_img:
                    st.success("✅ 카드 생성 완료!")
                    
                    # 결과 표시
                    st.markdown("---")
                    st.markdown("### 🎯 생성된 카드뉴스")
                    
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col2:
                        st.image(card_img, caption="생성된 한글 카드뉴스", use_container_width=True)
                    
                    # 다운로드 섹션
                    col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                    with col_dl2:
                        # 이미지를 바이트로 변환
                        buf = io.BytesIO()
                        card_img.save(buf, format='PNG', quality=100, optimize=True)
                        buf.seek(0)
                        
                        # 파일명 생성
                        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        safe_title = safe_title[:20].replace(' ', '_')
                        filename = f"한글카드_{safe_title}.png"
                        
                        st.download_button(
                            label="📥 고해상도 PNG 다운로드",
                            data=buf.getvalue(),
                            file_name=filename,
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    # 카드 정보
                    with st.expander("📊 생성된 카드 상세 정보"):
                        col_info1, col_info2 = st.columns(2)
                        
                        with col_info1:
                            st.write("**🖼️ 이미지 정보**")
                            st.write(f"• 크기: 1080 x 1920 픽셀")
                            st.write(f"• 형식: PNG (무손실)")
                            st.write(f"• 용량: {len(buf.getvalue()) / 1024:.1f} KB")
                        
                        with col_info2:
                            st.write("**🎨 디자인 정보**")
                            st.write(f"• 색상: {color_scheme}")
                            st.write(f"• 폰트: 나눔고딕")
                            st.write(f"• 최적화: Instagram Story")
                
                else:
                    st.error("❌ 카드 생성에 실패했습니다.")
                    st.info("💡 네트워크 연결을 확인하거나 잠시 후 다시 시도해주세요.")
                    
            except Exception as e:
                st.error(f"❌ 오류가 발생했습니다: {str(e)}")
                with st.expander("🔍 오류 상세 정보"):
                    st.code(str(e))

    # 도움말 섹션
    with st.expander("📖 사용법 및 팁"):
        tab1, tab2, tab3 = st.tabs(["🚀 빠른 시작", "💡 고급 팁", "🛠️ 기술 정보"])
        
        with tab1:
            st.markdown("""
            ### 🎯 3단계로 카드 만들기
            
            1. **제목 입력** - 카드의 핵심 메시지
            2. **내용 추가** - 불릿 포인트(● 또는 -)로 구성
            3. **생성 & 다운로드** - 즉시 PNG 파일로 저장
            
            ### ✨ 예시 템플릿
            
            **📌 제목:** "5분 만에 마스터하는 투자 기초"
            
            **📝 부제목:** "초보자도 쉽게 따라할 수 있는"
            
            **📄 내용:**
            ```
            ● 적금과 주식의 차이점 이해하기
            ● 리스크 관리의 기본 원칙
            ● 분산투자로 안전하게 시작하기
            ● 장기투자 vs 단기투자 비교
            ● 전문가가 추천하는 첫 투자 상품
            ```
            """)
        
        with tab2:
            st.markdown("""
            ### 🎨 디자인 최적화 팁
            
            - **제목**: 10-15자 이내로 임팩트 있게
            - **부제목**: 제목을 보완하는 한 줄 설명
            - **내용**: 3-7개 불릿 포인트가 최적
            - **색상**: 콘텐츠 성격에 맞는 색상 선택
            
            ### 📱 플랫폼별 활용법
            
            - **Instagram Story**: 1080x1920 그대로 사용
            - **Facebook 포스트**: 크기 조정 없이 바로 업로드
            - **블로그**: 썸네일 이미지로 활용
            - **프레젠테이션**: PPT 슬라이드로 삽입
            
            ### 💯 전문적인 카드 만들기
            
            - 일관된 톤앤매너 유지
            - 간결하고 명확한 메시지
            - 시각적 계층 구조 고려
            - 타겟 오디언스에 맞는 언어 사용
            """)
        
        with tab3:
            st.markdown("""
            ### 🛠️ 기술 스펙
            
            - **이미지 크기**: 1080 x 1920 픽셀
            - **폰트**: 나눔고딕 (자동 다운로드)
            - **파일 형식**: PNG (무손실 압축)
            - **색상 공간**: RGB
            - **텍스트 인코딩**: UTF-8 (완벽한 한글 지원)
            
            ### 🔧 폰트 시스템
            
            - GitHub에서 나눔고딕 자동 다운로드
            - 시스템 폰트 의존성 없음
            - 크로스 플랫폼 호환
            - 라이선스: SIL Open Font License
            
            ### 🚀 성능 최적화
            
            - 폰트 캐싱으로 빠른 재생성
            - 메모리 효율적인 이미지 처리
            - 실시간 미리보기
            - 배치 처리 지원 준비
            """)

if __name__ == "__main__":
    main()
