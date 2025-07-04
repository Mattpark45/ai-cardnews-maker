import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import io
import os
import requests
from pathlib import Path
import zipfile
import time

# 폰트 다운로드 및 설정
@st.cache_data
def download_korean_fonts():
    """한글 폰트 자동 다운로드 및 설정"""
    
    fonts_dir = Path("fonts")
    fonts_dir.mkdir(exist_ok=True)
    
    # 나눔고딕 폰트 URL (Google Fonts GitHub에서 제공)
    font_urls = {
        "NanumGothic-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf",
        "NanumGothic-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf"
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
    """한글 폰트 로드"""
    
    fonts_dir = Path("fonts")
    
    if weight == 'bold':
        local_font = fonts_dir / "NanumGothic-Bold.ttf"
    else:
        local_font = fonts_dir / "NanumGothic-Regular.ttf"
    
    # 로컬 파일이 있으면 바로 사용
    if local_font.exists():
        try:
            return ImageFont.truetype(str(local_font), size)
        except Exception as e:
            st.warning(f"로컬 폰트 로딩 실패: {e}")
    
    # 없으면 다운로드 시도
    fonts = download_korean_fonts()
    
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

# AI 이미지 생성 (Picsum API 사용 - 실제 서비스에서는 DALL-E, Midjourney API 등 사용)
@st.cache_data
def generate_ai_background(theme, width=1080, height=1920, style="modern"):
    """AI 스타일 배경 이미지 생성 (Picsum Photos API 활용)"""
    
    # 테마별 시드 번호 (일관된 이미지를 위해)
    theme_seeds = {
        "비즈니스": 42,
        "자연": 123,
        "기술": 456,
        "음식": 789,
        "여행": 321,
        "패션": 654,
        "교육": 987,
        "건강": 147,
        "라이프스타일": 258,
        "창의적": 369
    }
    
    seed = theme_seeds.get(theme, 100)
    
    try:
        # Picsum Photos에서 고해상도 이미지 가져오기
        url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
        
        with st.spinner(f"🎨 {theme} 테마 배경 이미지 생성 중..."):
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 이미지 열기
            img = Image.open(io.BytesIO(response.content))
            
            # 스타일 적용
            if style == "blur":
                # 블러 효과
                img = img.filter(ImageFilter.GaussianBlur(radius=8))
            elif style == "dark":
                # 어둡게 처리
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(0.3)
            elif style == "vintage":
                # 빈티지 효과
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(0.7)
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)
            
            return img
            
    except Exception as e:
        st.warning(f"AI 배경 생성 실패: {e}. 그라데이션으로 대체합니다.")
        return None

def create_gradient_background(width, height, color_scheme):
    """그라데이션 배경 생성 (AI 이미지 실패시 백업용)"""
    
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
    
    img = Image.new('RGB', (width, height))
    
    for y in range(height):
        ratio = y / height
        ratio = ratio * ratio * (3.0 - 2.0 * ratio)  # smooth step
        
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        
        for x in range(width):
            img.putpixel((x, y), (r, g, b))
    
    return img

def get_text_dimensions(text, font):
    """텍스트의 정확한 크기 측정"""
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
                lines.append(word)
                current_line = ""
    
    if current_line:
        lines.append(current_line.strip())
    
    return lines

def draw_text_with_shadow(draw, position, text, font, text_color='white', shadow_color=(0, 0, 0, 180), shadow_offset=(3, 3)):
    """그림자 효과가 있는 텍스트 그리기"""
    x, y = position
    
    # 그림자 그리기
    draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=shadow_color)
    
    # 메인 텍스트 그리기
    draw.text((x, y), text, font=font, fill=text_color)

def create_carousel_card(card_data, card_number, total_cards, background_type="ai", theme="비즈니스", width=1080, height=1920):
    """캐러셀용 개별 카드 생성"""
    
    # 배경 생성
    if background_type == "ai":
        img = generate_ai_background(theme, width, height, style="blur")
        if img is None:
            # AI 생성 실패시 그라데이션으로 대체
            img = create_gradient_background(width, height, "다크 그라데이션")
            # 오버레이 추가
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 120))
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    else:
        img = create_gradient_background(width, height, theme)
    
    # 어두운 오버레이 추가 (텍스트 가독성 향상)
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    draw = ImageDraw.Draw(img)
    
    # 폰트 로드
    title_font = get_korean_font(85, 'bold')
    subtitle_font = get_korean_font(55, 'regular') 
    content_font = get_korean_font(42, 'regular')
    page_font = get_korean_font(35, 'regular')
    
    if not title_font:
        return None
    
    margin = 80
    y_position = 120
    
    # 페이지 번호 표시 (우상단)
    page_text = f"{card_number}/{total_cards}"
    page_width, page_height = get_text_dimensions(page_text, page_font)
    draw.rectangle([width - page_width - 60, 40, width - 20, 40 + page_height + 20], 
                  fill=(255, 255, 255, 200))
    draw.text((width - page_width - 40, 50), page_text, font=page_font, fill='#2c3e50')
    
    # 1. 제목 그리기
    title = card_data.get('title', '')
    if title:
        title_lines = wrap_text(title, title_font, width - margin * 2)
        
        for i, line in enumerate(title_lines):
            text_width, text_height = get_text_dimensions(line, title_font)
            x = (width - text_width) // 2
            
            # 제목 배경
            padding = 40
            draw.rectangle([x - padding, y_position - 15, 
                          x + text_width + padding, y_position + text_height + 15], 
                         fill=(0, 0, 0, 160))
            
            # 텍스트 그리기 (그림자 효과)
            draw_text_with_shadow(draw, (x, y_position), line, title_font, 'white')
            
            y_position += text_height + 20
        
        y_position += 60
    
    # 2. 부제목 그리기
    subtitle = card_data.get('subtitle', '')
    if subtitle:
        subtitle_lines = wrap_text(subtitle, subtitle_font, width - margin * 2)
        
        for line in subtitle_lines:
            text_width, text_height = get_text_dimensions(line, subtitle_font)
            x = (width - text_width) // 2
            
            # 부제목 배경
            padding = 30
            draw.rectangle([x - padding, y_position - 10, 
                          x + text_width + padding, y_position + text_height + 10], 
                         fill=(255, 255, 255, 220))
            
            draw.text((x, y_position), line, font=subtitle_font, fill='#2c3e50')
            
            y_position += text_height + 15
        
        y_position += 100
    
    # 3. 내용 그리기
    content = card_data.get('content', '')
    if content:
        content_lines = content.split('\n')
        all_lines = []
        
        for line in content_lines:
            if line.strip():
                if line.strip().startswith('•') or line.strip().startswith('-'):
                    wrapped_lines = wrap_text(line, content_font, width - margin * 2 - 40)
                else:
                    wrapped_lines = wrap_text(line, content_font, width - margin * 2)
                all_lines.extend(wrapped_lines)
            else:
                all_lines.append("")
        
        # 내용 전체 영역 크기 계산
        line_height = 60
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
        
        # 반투명 배경
        draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=(255, 255, 255, 240))
        
        # 각 줄 그리기
        for line in all_lines:
            if line:
                # 불릿 포인트 스타일링
                if line.strip().startswith('•'):
                    line = line.replace('•', '●')
                elif line.strip().startswith('-'):
                    line = line.replace('-', '●')
                
                text_width, text_height = get_text_dimensions(line, content_font)
                x = (width - text_width) // 2
                
                # 불릿 포인트면 왼쪽 정렬
                if line.strip().startswith('●'):
                    x = bg_x1 + 30
                
                draw.text((x, y_position), line, font=content_font, fill='#2c3e50')
                y_position += line_height
            else:
                y_position += line_height // 2
    
    return img

def split_content_into_cards(title, subtitle, content, max_cards=5):
    """콘텐츠를 여러 카드로 분할"""
    
    cards = []
    
    # 첫 번째 카드 (타이틀 카드)
    cards.append({
        'title': title,
        'subtitle': subtitle,
        'content': ''
    })
    
    if not content:
        return cards
    
    # 내용을 줄 단위로 분리
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # 각 카드당 최대 줄 수
    max_lines_per_card = max(1, len(lines) // (max_cards - 1))
    
    current_card_lines = []
    
    for i, line in enumerate(lines):
        current_card_lines.append(line)
        
        # 카드가 가득 찼거나 마지막 줄인 경우
        if len(current_card_lines) >= max_lines_per_card or i == len(lines) - 1:
            if len(cards) < max_cards:
                # 카드 제목 생성 (첫 번째 불릿 포인트에서 추출)
                card_title = ""
                if current_card_lines:
                    first_line = current_card_lines[0]
                    if first_line.startswith('•') or first_line.startswith('-'):
                        card_title = first_line[1:].strip()[:20] + "..."
                    else:
                        card_title = f"{title} - {len(cards)}"
                
                cards.append({
                    'title': card_title,
                    'subtitle': '',
                    'content': '\n'.join(current_card_lines)
                })
                
                current_card_lines = []
    
    return cards[:max_cards]

def create_carousel_zip(cards_data, background_type, theme):
    """캐러셀 카드들을 ZIP 파일로 생성"""
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        
        for i, card_data in enumerate(cards_data, 1):
            # 각 카드 생성
            card_img = create_carousel_card(
                card_data, 
                i, 
                len(cards_data), 
                background_type, 
                theme
            )
            
            if card_img:
                # 이미지를 바이트로 변환
                img_buffer = io.BytesIO()
                card_img.save(img_buffer, format='PNG', quality=100, optimize=True)
                img_buffer.seek(0)
                
                # ZIP에 추가
                filename = f"카드_{i:02d}_{card_data['title'][:10].replace(' ', '_')}.png"
                zip_file.writestr(filename, img_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer

# Streamlit 메인 앱
def main():
    st.set_page_config(
        page_title="한글 캐러셀 카드뉴스 생성기", 
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
    
    st.markdown('<h1 class="main-title">🎠 한글 캐러셀 카드뉴스 생성기</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI 배경과 완벽한 한글 렌더링으로 전문적인 캐러셀 카드뉴스를 만들어보세요!</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("🎨 디자인 설정")
        
        background_type = st.selectbox(
            "🖼️ 배경 타입",
            ["ai", "gradient"],
            format_func=lambda x: "🤖 AI 생성 이미지" if x == "ai" else "🌈 그라데이션"
        )
        
        if background_type == "ai":
            theme = st.selectbox(
                "🎯 AI 배경 테마",
                ["비즈니스", "자연", "기술", "음식", "여행", "패션", "교육", "건강", "라이프스타일", "창의적"]
            )
        else:
            theme = st.selectbox(
                "🌈 그라데이션 색상",
                ["블루 그라데이션", "퍼플 그라데이션", "그린 그라데이션", 
                 "오렌지 그라데이션", "다크 그라데이션", "핑크 그라데이션",
                 "민트 그라데이션", "선셋 그라데이션"]
            )
        
        max_cards = st.slider("📱 최대 카드 수", 3, 8, 5)
        
        st.markdown("---")
        st.markdown("### 📱 카드 정보")
        st.info("**크기:** 1080 x 1920px\n**최적화:** Instagram Carousel\n**형식:** PNG (고해상도)")
        
        if background_type == "ai":
            st.markdown("### 🤖 AI 배경")
            st.success("**Picsum Photos API** 활용\n실제 서비스 품질의 배경 이미지")
        
        st.markdown("### 🔤 폰트 정보")
        st.success("**나눔고딕** 자동 다운로드\n한글 완벽 지원 보장!")
    
    # 메인 콘텐츠
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.header("✏️ 캐러셀 내용 입력")
        
        with st.form("carousel_form", clear_on_submit=False):
            title = st.text_input(
                "📌 메인 제목 (필수)", 
                value="완벽한 예산관리 가이드",
                help="캐러셀 전체의 메인 제목입니다",
                placeholder="예: 결혼준비 완벽 가이드"
            )
            
            subtitle = st.text_input(
                "📝 부제목 (선택)", 
                value="신혼부부를 위한 단계별 팁",
                help="첫 번째 카드에 들어갈 부제목입니다",
                placeholder="예: 전문가가 알려주는 비밀"
            )
            
            content = st.text_area(
                "📄 상세 내용 (자동으로 여러 카드로 분할됩니다)", 
                value="""• 예식장 예약 시기별 할인율 비교 분석
• 드레스 렌탈 vs 구매 비용 상세 계산법  
• 허니문 패키지 가격 협상 전략 공개
• 신혼집 준비 우선순위 체크리스트 완전판
• 웨딩 플래너 선택 기준과 비용 절약법
• 하객 관리와 예산 배분의 황금 비율
• 웨딩드레스 피팅 일정과 체중 관리 팁
• 결혼식 당일 응급상황 대처 매뉴얼""",
                height=300,
                help="내용이 자동으로 여러 카드로 분할됩니다. '●' 또는 '-'로 시작하면 불릿 포인트가 됩니다.",
                placeholder="● 첫 번째 팁\n● 두 번째 팁\n● 세 번째 팁..."
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button("🎠 캐러셀 생성하기", use_container_width=True, type="primary")
            with col_btn2:
                clear_form = st.form_submit_button("🗑️ 초기화", use_container_width=True)
    
    with col2:
        st.header("👀 캐러셀 미리보기")
        
        if title:
            # 콘텐츠를 카드로 분할해서 미리보기
            cards_preview = split_content_into_cards(title, subtitle, content, max_cards)
            
            st.markdown(f"**📱 총 {len(cards_preview)}장의 카드가 생성됩니다**")
            st.markdown("---")
            
            for i, card in enumerate(cards_preview, 1):
                with st.expander(f"🎴 카드 {i}: {card['title'][:20]}..."):
                    st.markdown(f"**제목:** {card['title']}")
                    if card['subtitle']:
                        st.markdown(f"**부제목:** {card['subtitle']}")
                    if card['content']:
                        content_preview = card['content'][:100] + "..." if len(card['content']) > 100 else card['content']
                        st.text(content_preview)
        
        # 통계 정보
        if any([title, subtitle, content]):
            st.markdown("---")
            st.markdown("### 📊 캐러셀 통계")
            
            total_chars = len(title or "") + len(subtitle or "") + len(content or "")
            content_lines = len([line for line in content.split('\n') if line.strip()]) if content else 0
            
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("총 글자수", total_chars)
            with col_stat2:
                st.metric("내용 항목", content_lines)
    
    # 캐러셀 생성 처리
    if clear_form:
        st.rerun()
    
    if submitted:
        if not title:
            st.error("❌ 메인 제목을 입력해주세요!")
            return
        
        # 콘텐츠를 카드로 분할
        cards_data = split_content_into_cards(title, subtitle, content, max_cards)
        
        with st.spinner(f"🎠 {len(cards_data)}장의 전문적인 캐러셀 카드를 생성하고 있습니다..."):
            try:
                # 개별 카드들을 먼저 미리보기로 표시
                st.success(f"✅ {len(cards_data)}장의 캐러셀 카드 생성 완료!")
                
                # 결과 표시
                st.markdown("---")
                st.markdown("### 🎯 생성된 캐러셀 카드뉴스")
                
                # 카드들을 가로로 표시
                cols = st.columns(min(len(cards_data), 3))
                generated_cards = []
                
                for i, card_data in enumerate(cards_data):
                    card_img = create_carousel_card(
                        card_data, 
                        i + 1, 
                        len(cards_data), 
                        background_type, 
                        theme
                    )
                    
                    if card_img:
                        generated_cards.append((card_img, card_data))
                        
                        # 3개씩 가로로 배치
                        with cols[i % 3]:
                            st.image(card_img, caption=f"카드 {i+1}: {card_data['title'][:15]}...", use_container_width=True)
                
                if generated_cards:
                    # ZIP 파일 생성
                    with st.spinner("📦 ZIP 파일 생성 중..."):
                        zip_buffer = create_carousel_zip(cards_data, background_type, theme)
                    
                    # 다운로드 섹션
                    col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                    with col_dl2:
                        # 파일명 생성
                        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        safe_title = safe_title[:20].replace(' ', '_')
                        zip_filename = f"캐러셀_{safe_title}_{len(cards_data)}장.zip"
                        
                        st.download_button(
                            label=f"📦 캐러셀 전체 다운로드 ({len(cards_data)}장 ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=zip_filename,
                            mime="application/zip",
                            use_container_width=True
                        )
                    
                    # 개별 카드 다운로드 옵션
                    with st.expander("📥 개별 카드 다운로드"):
                        for i, (card_img, card_data) in enumerate(generated_cards):
                            col_individual1, col_individual2 = st.columns([2, 1])
                            
                            with col_individual1:
                                st.markdown(f"**카드 {i+1}:** {card_data['title']}")
                            
                            with col_individual2:
                                # 개별 카드 이미지를 바이트로 변환
                                individual_buffer = io.BytesIO()
                                card_img.save(individual_buffer, format='PNG', quality=100, optimize=True)
                                individual_buffer.seek(0)
                                
                                individual_filename = f"카드_{i+1:02d}_{card_data['title'][:10].replace(' ', '_')}.png"
                                
                                st.download_button(
                                    label="PNG 다운로드",
                                    data=individual_buffer.getvalue(),
                                    file_name=individual_filename,
                                    mime="image/png",
                                    key=f"download_{i}"
                                )
                    
                    # 캐러셀 정보
                    with st.expander("📊 생성된 캐러셀 상세 정보"):
                        col_info1, col_info2 = st.columns(2)
                        
                        with col_info1:
                            st.write("**🖼️ 캐러셀 정보**")
                            st.write(f"• 총 카드 수: {len(cards_data)}장")
                            st.write(f"• 카드 크기: 1080 x 1920 픽셀")
                            st.write(f"• 형식: PNG (무손실 고화질)")
                            st.write(f"• ZIP 용량: {len(zip_buffer.getvalue()) / 1024:.1f} KB")
                        
                        with col_info2:
                            st.write("**🎨 디자인 정보**")
                            st.write(f"• 배경: {'AI 생성 이미지' if background_type == 'ai' else '그라데이션'}")
                            st.write(f"• 테마: {theme}")
                            st.write(f"• 폰트: 나눔고딕")
                            st.write(f"• 최적화: Instagram Carousel")
                        
                        # 사용법 안내
                        st.markdown("---")
                        st.markdown("**📱 Instagram 캐러셀 업로드 방법:**")
                        st.markdown("1. ZIP 파일 다운로드 및 압축 해제")
                        st.markdown("2. Instagram 앱에서 '+' 버튼 클릭")
                        st.markdown("3. '캐러셀' 선택 후 카드들을 순서대로 선택")
                        st.markdown("4. 필터 및 편집 후 게시")
                
                else:
                    st.error("❌ 캐러셀 카드 생성에 실패했습니다.")
                    st.info("💡 네트워크 연결을 확인하거나 잠시 후 다시 시도해주세요.")
                    
            except Exception as e:
                st.error(f"❌ 오류가 발생했습니다: {str(e)}")
                with st.expander("🔍 오류 상세 정보"):
                    st.code(str(e))

    # 도움말 섹션
    with st.expander("📖 캐러셀 카드뉴스 완전 가이드"):
        tab1, tab2, tab3, tab4 = st.tabs(["🚀 빠른 시작", "🎨 디자인 팁", "📱 활용법", "🛠️ 기술 정보"])
        
        with tab1:
            st.markdown("""
            ### 🎯 4단계로 캐러셀 만들기
            
            1. **메인 제목 입력** - 캐러셀 전체의 핵심 메시지
            2. **상세 내용 입력** - 자동으로 여러 카드로 분할됩니다
            3. **배경 & 테마 선택** - AI 이미지 또는 그라데이션
            4. **생성 & 다운로드** - ZIP 파일로 모든 카드 한 번에 저장
            
            ### ✨ 캐러셀 템플릿 예시
            
            **📌 메인 제목:** "성공하는 창업자의 5가지 습관"
            
            **📝 부제목:** "실리콘밸리 CEO들의 비밀"
            
            **📄 상세 내용:**
            ```
            • 매일 새벽 5시 기상으로 하루를 시작하기
            • 독서와 학습에 하루 2시간 이상 투자하기
            • 네트워킹을 위한 주 3회 이상 미팅 참석
            • 실패를 두려워하지 않는 도전 정신 기르기
            • 고객 피드백을 즉시 제품에 반영하는 애자일 사고
            • 팀원들과의 투명한 소통으로 신뢰 구축하기
            • 데이터 기반 의사결정으로 감정적 판단 배제
            • 장기 비전과 단기 목표의 균형잡힌 로드맵
            ```
            
            **결과:** 8개 항목이 자동으로 5장의 아름다운 캐러셀 카드로 변환됩니다!
            """)
        
        with tab2:
            st.markdown("""
            ### 🎨 효과적인 캐러셀 디자인 가이드
            
            #### 📝 텍스트 최적화
            - **메인 제목**: 15-25자 이내, 임팩트 있는 키워드 포함
            - **부제목**: 제목을 보완하는 구체적 설명
            - **내용**: 3-8개 불릿 포인트로 구성
            - **각 포인트**: 한 줄당 15-30자 권장
            
            #### 🎯 테마별 배경 선택 가이드
            - **비즈니스**: 전문적이고 신뢰감 있는 이미지
            - **라이프스타일**: 밝고 따뜻한 느낌의 이미지  
            - **기술**: 모던하고 미래지향적인 이미지
            - **교육**: 깔끔하고 집중도 높은 이미지
            - **음식**: 맛있고 시각적으로 매력적인 이미지
            
            #### 🌈 색상 조합 팁
            - **그라데이션**: 브랜드 컬러와 조화로운 색상 선택
            - **AI 배경**: 콘텐츠 성격에 맞는 테마 선택
            - **텍스트**: 흰색/검은색으로 명확한 대비 유지
            
            #### 📐 레이아웃 최적화
            - 제목은 상단 1/3 영역에 배치
            - 내용은 중앙에서 하단 2/3 활용
            - 여백을 충분히 두어 깔끔한 느낌 연출
            """)
        
        with tab3:
            st.markdown("""
            ### 📱 플랫폼별 캐러셀 활용 전략
            
            #### 📸 Instagram 캐러셀
            - **최적 카드 수**: 3-5장 (스와이프 피로도 고려)
            - **첫 번째 카드**: 강력한 훅으로 관심 유도
            - **마지막 카드**: CTA(Call to Action) 포함
            - **해시태그**: 관련성 높은 태그 10-15개
            
            #### 📘 Facebook 포스트
            - **스토리텔링**: 각 카드가 연결된 이야기 구성
            - **참여 유도**: 질문이나 의견 요청으로 마무리
            - **타이밍**: 타겟 오디언스 활동 시간대 게시
            
            #### 💼 LinkedIn 콘텐츠
            - **전문성**: 비즈니스 인사이트나 전문 지식 공유
            - **데이터 활용**: 통계나 차트로 신뢰도 증대
            - **네트워킹**: 업계 전문가 태그로 도달 범위 확대
            
            #### 🎬 YouTube 커뮤니티
            - **영상 보완**: 메인 영상의 핵심 내용 요약
            - **예고편**: 다음 영상 내용 미리보기
            - **Q&A**: 댓글 질문에 대한 시각적 답변
            
            ### 🚀 마케팅 활용 아이디어
            
            #### 📊 비즈니스 인사이트
            - 시장 동향 분석 카드뉴스
            - 업계 통계 시각화
            - 경쟁사 분석 리포트
            
            #### 📚 교육 콘텐츠
            - 단계별 튜토리얼
            - 팁과 노하우 공유
            - 용어 정리 사전
            
            #### 🎯 제품/서비스 홍보
            - 기능 소개 카드뉴스
            - 고객 후기 스토리
            - 특가 혜택 안내
            """)
        
        with tab4:
            st.markdown("""
            ### 🛠️ 기술 스펙 및 최적화
            
            #### 📐 이미지 규격
            - **해상도**: 1080 x 1920 픽셀 (Full HD)
            - **비율**: 9:16 (세로형, 모바일 최적화)
            - **파일 형식**: PNG (무손실 압축)
            - **색상 공간**: sRGB (웹 표준)
            - **DPI**: 72 (웹 최적화)
            
            #### 🔤 폰트 시스템
            - **메인 폰트**: 나눔고딕 (Nanum Gothic)
            - **라이선스**: SIL Open Font License
            - **지원 언어**: 한국어, 영어, 숫자
            - **가독성**: 모바일 화면 최적화
            - **다운로드**: Google Fonts API 자동 연동
            
            #### 🤖 AI 배경 생성
            - **API**: Picsum Photos (고품질 이미지)
            - **처리**: 블러, 다크닝, 빈티지 필터 적용
            - **캐싱**: Streamlit 자동 캐시로 빠른 로딩
            - **폴백**: AI 실패시 그라데이션 자동 대체
            
            #### ⚡ 성능 최적화
            - **메모리**: 효율적인 이미지 처리
            - **속도**: 폰트 캐싱으로 빠른 생성
            - **안정성**: 다단계 오류 처리
            - **확장성**: 최대 8장까지 캐러셀 지원
            
            #### 📦 파일 출력
            - **ZIP 압축**: 모든 카드를 한 번에 다운로드
            - **개별 파일**: PNG 형태로 각각 저장 가능
            - **파일명**: 자동 생성 (한글 지원)
            - **압축률**: 최적화된 ZIP 압축
            
            ### 🔧 문제 해결 가이드
            
            #### 폰트 로딩 실패
            - 네트워크 연결 확인
            - VPN 사용시 일시 해제
            - 페이지 새로고침 후 재시도
            
            #### AI 배경 생성 실패  
            - 자동으로 그라데이션 대체
            - 테마 변경 후 재시도
            - 네트워크 상태 확인
            
            #### 텍스트 깨짐 현상
            - 특수문자 사용 최소화
            - 줄바꿈 문자 확인
            - 지원되지 않는 이모지 제거
            """)

if __name__ == "__main__":
    main()
