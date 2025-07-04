# 3. 내용 그리기
    content = card_data.get('content', '')
    if content:
        content_lines = content.split('\n')
        all_lines = []
        
        for line in content_lines:
            if line.strip():
                if line.strip().startswith('•') or line.strip().startswith('-'):
                    wrapped_lines = wrap_text(line, content_font, width - margin * 2 - spacing['padding'])
                else:
                    wrapped_lines = wrap_text(line, content_font, width - margin * 2)
                all_lines.extend(wrapped_lines)
            else:
                all_lines.append("")
        
        # 내용 전체 영역 크기 계산
        line_height = spacing['line_height']
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
        bg_padding = int(spacing['padding'] * 1.3)
        bg_x1 = (width - max_line_width) // 2 - bg_padding
        bg_x2 = (width + max_line_width) // 2 + bg_padding
        bg_y1 = y_position - bg_padding//2
        bg_y2 = y_position + content_height + bg_padding//2
        
        # 화면 하단을 넘지 않도록 조정
        bottom_margin = height // 20
        if bg_y2 > height - bottom_margin:
            # 내용이 너무 길면 폰트 크기 축소
            content_font = get_korean_font(int(font_sizes['content'] * 0.85), 'regular')
            line_height = int(spacing['line_height'] * 0.85)
            
            # 다시 계산
            content_height = 0
            for line in all_lines:
                if line:
                    content_height += line_height
                else:
                    content_height += line_height // 2
            
            bg_y2 = y_position + content_height + bg_padding//2
        
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
                    x = bg_x1 + bg_padding//2
                
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

def create_carousel_zip(cards_data, background_type, theme, width=1080, height=1920):
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
                theme,
                width,
                height
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
        
        # 플랫폼별 사이즈 선택
        platform = st.selectbox(
            "📱 플랫폼 선택",
            ["Instagram Carousel", "YouTube Thumbnail", "Naver Blog", "Facebook Post", "Custom Size"],
            help="각 플랫폼에 최적화된 크기로 카드를 생성합니다"
        )
        
        # 플랫폼별 사이즈 정의
        platform_sizes = {
            "Instagram Carousel": (1080, 1080, "정사각형 - Instagram 캐러셀 최적화"),
            "YouTube Thumbnail": (1280, 720, "16:9 - YouTube 썸네일 표준"),
            "Naver Blog": (800, 600, "4:3 - 네이버 블로그 썸네일"),
            "Facebook Post": (1200, 630, "1.91:1 - Facebook 링크 미리보기"),
            "Custom Size": (1080, 1920, "사용자 정의")
        }
        
        width, height, size_description = platform_sizes[platform]
        
        # 커스텀 사이즈인 경우 사용자 입력 받기
        if platform == "Custom Size":
            col1, col2 = st.columns(2)
            with col1:
                width = st.number_input("너비 (px)", min_value=400, max_value=2000, value=1080, step=10)
            with col2:
                height = st.number_input("높이 (px)", min_value=400, max_value=2000, value=1920, step=10)
            size_description = f"{width} x {height}px"
        
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
        st.info(f"**크기:** {width} x {height}px\n**설명:** {size_description}\n**형식:** PNG (고해상도)")
        
        # 플랫폼별 사용 팁
        platform_tips = {
            "Instagram Carousel": "• 최대 10장까지 업로드 가능\n• 정사각형으로 일관성 있는 피드\n• 스와이프로 순서대로 확인",
            "YouTube Thumbnail": "• 1280x720 권장 해상도\n• 16:9 비율로 플레이어에 최적화\n• 텍스트는 크고 명확하게",
            "Naver Blog": "• 포스팅 썸네일로 활용\n• 4:3 비율로 미리보기 최적화\n• SEO 효과 기대",
            "Facebook Post": "• 링크 미리보기 최적화\n• 1.91:1 비율 권장\n• 뉴스피드에서 눈에 띄는 크기",
            "Custom Size": "• 원하는 크기로 자유 설정\n• 다양한 용도로 활용 가능\n• 인쇄물 제작도 고려"
        }
        
        with st.expander(f"💡 {platform} 활용 팁"):
            st.write(platform_tips[platform])
        
        if background_type == "ai":
            st.markdown("### 🤖 AI 배경 시스템")
            st.success("**다중 API 지원**\n• Pollinations AI (최고품질)\n• 카드별 맞춤 이미지\n• 콘텐츠 기반 키워드 추출")
        
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
        
        with st.spinner(f"🎠 {len(cards_data)}장의 전문적인 {platform} 카드를 생성하고 있습니다..."):
            try:
                # 개별 카드들을 먼저 미리보기로 표시
                st.success(f"✅ {len(cards_data)}장의 {platform} 카드 생성 완료!")
                
                # 결과 표시
                st.markdown("---")
                st.markdown(f"### 🎯 생성된 {platform} 카드뉴스")
                
                # 카드들을 가로로 표시
                cols = st.columns(min(len(cards_data), 3))
                generated_cards = []
                
                for i, card_data in enumerate(cards_data):
                    try:
                        st.info(f"카드 {i+1} 생성 중...")
                        
                        card_img = create_carousel_card(
                            card_data, 
                            i + 1, 
                            len(cards_data), 
                            background_type, 
                            theme,
                            width,  # 선택한 플랫폼의 너비
                            height  # 선택한 플랫폼의 높이
                        )
                        
                        if card_img:
                            generated_cards.append((card_img, card_data))
                            
                            # 3개씩 가로로 배치
                            with cols[i % 3]:
                                st.image(card_img, caption=f"카드 {i+1}: {card_data['title'][:15]}...", use_container_width=True)
                                st.success(f"✅ 카드 {i+1} 완성!")
                        else:
                            st.error(f"❌ 카드 {i+1} 생성 실패")
                            
                    except Exception as card_error:
                        st.error(f"❌ 카드 {i+1} 생성 오류: {str(card_error)}")
                        st.code(f"상세 오류: {repr(card_error)}")
                        continue
                
                if generated_cards:
                    # ZIP 파일 생성 (플랫폼별 크기 적용)
                    with st.spinner("📦 ZIP 파일 생성 중..."):
                        zip_buffer = create_carousel_zip(cards_data, background_type, theme, width, height)
                    
                    # 다운로드 섹션
                    col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                    with col_dl2:
                        # 파일명 생성
                        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        safe_title = safe_title[:20].replace(' ', '_')
                        zip_filename = f"{platform.replace(' ', '_')}_{safe_title}_{len(cards_data)}장.zip"
                        
                        st.download_button(
                            label=f"📦 {platform} 전체 다운로드 ({len(cards_data)}장 ZIP)",
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
                    with st.expander("📊 생성된 카드뉴스 상세 정보"):
                        col_info1, col_info2 = st.columns(2)
                        
                        with col_info1:
                            st.write("**🖼️ 카드 정보**")
                            st.write(f"• 총 카드 수: {len(cards_data)}장")
                            st.write(f"• 카드 크기: {width} x {height} 픽셀")
                            st.write(f"• 플랫폼: {platform}")
                            st.write(f"• 형식: PNG (무손실 고화질)")
                            st.write(f"• ZIP 용량: {len(zip_buffer.getvalue()) / 1024:.1f} KB")
                        
                        with col_info2:
                            st.write("**🎨 디자인 정보**")
                            st.write(f"• 배경: {'AI 생성 이미지' if background_type == 'ai' else '그라데이션'}")
                            st.write(f"• 테마: {theme}")
                            st.write(f"• 폰트: 나눔고딕 (플랫폼 최적화)")
                            st.write(f"• 최적화: {size_description}")
                        
                        # 플랫폼별 사용법 안내
                        st.markdown("---")
                        platform_guides = {
                            "Instagram Carousel": "**📸 Instagram 업로드 방법:**\n1. Instagram 앱에서 '+' 버튼 클릭\n2. '캐러셀' 선택 후 카드들을 순서대로 선택\n3. 필터 및 편집 후 게시",
                            "YouTube Thumbnail": "**📺 YouTube 썸네일 설정:**\n1. YouTube Studio에서 동영상 선택\n2. '세부정보' 탭에서 썸네일 업로드\n3. 생성된 이미지 중 선택하여 적용",
                            "Naver Blog": "**📝 네이버 블로그 활용:**\n1. 포스팅 작성 시 대표 이미지로 설정\n2. 본문 내 이미지로 삽입\n3. 썸네일로 노출되어 클릭률 향상",
                            "Facebook Post": "**📘 Facebook 포스트 활용:**\n1. 페이지 또는 개인 계정에서 포스트 작성\n2. 이미지 첨부로 카드뉴스 업로드\n3. 캐러셀 형태로 여러 장 업로드 가능",
                            "Custom Size": "**🔧 커스텀 사이즈 활용:**\n1. 인쇄물 제작 시 활용 가능\n2. 웹사이트 배너로 사용\n3. 프레젠테이션 슬라이드로 활용"
                        }
                        
                        st.markdown(platform_guides.get(platform, "다양한 용도로 활용 가능합니다."))
                
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
            
            1. **플랫폼 선택** - Instagram, YouTube, 네이버 블로그 등
            2. **메인 제목 입력** - 캐러셀 전체의 핵심 메시지
            3. **상세 내용 입력** - 자동으로 여러 카드로 분할됩니다
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
            ```
            
            **결과:** 5개 항목이 자동으로 5장의 아름다운 캐러셀 카드로 변환됩니다!
            """)
        
        with tab2:
            st.markdown("""
            ### 🎨 효과적인 캐러셀 디자인 가이드
            
            #### 📝 텍스트 최적화
            - **메인 제목**: 15-25자 이내, 임팩트 있는 키워드 포함
            - **부제목**: 제목을 보완하는 구체적 설명
            - **내용**: 3-8개 불릿 포인트로 구성
            - **각 포인트**: 한 줄당 15-30자 권장
            
            #### 🎯 플랫폼별 최적화
            - **Instagram**: 정사각형 비율로 피드 일관성
            - **YouTube**: 16:9 비율로 썸네일 최적화
            - **네이버 블로그**: 4:3 비율로 포스팅 썸네일
            - **Facebook**: 1.91:1 비율로 링크 미리보기
            
            #### 🤖 AI 배경 활용
            - **비즈니스**: 전문적이고 신뢰감 있는 이미지
            - **자연**: 힐링과 평온함을 주는 배경
            - **기술**: 미래지향적이고 혁신적인 느낌
            - **라이프스타일**: 일상적이고 친근한 분위기
            """)
        
        with tab3:
            st.markdown("""
            ###import streamlit as st
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

def get_optimized_font_sizes(width, height):
    """플랫폼 크기에 따른 최적 폰트 크기 계산"""
    
    # 기준 크기 (Instagram Story 1080x1920)
    base_width, base_height = 1080, 1920
    base_title_size = 75
    base_subtitle_size = 48
    base_content_size = 38
    base_page_size = 30
    
    # 크기 비율 계산 (면적 기준)
    area_ratio = (width * height) / (base_width * base_height)
    size_multiplier = area_ratio ** 0.5  # 제곱근으로 적절한 스케일링
    
    # 최소/최대 제한
    size_multiplier = max(0.6, min(1.5, size_multiplier))
    
    return {
        'title': int(base_title_size * size_multiplier),
        'subtitle': int(base_subtitle_size * size_multiplier),
        'content': int(base_content_size * size_multiplier),
        'page': int(base_page_size * size_multiplier)
    }

def get_optimized_spacing(width, height):
    """플랫폼 크기에 따른 최적 간격 계산"""
    
    # 기준 간격값들
    base_margin = 60
    base_y_start = 100
    base_padding = 30
    
    # 크기에 따른 스케일링
    area_ratio = (width * height) / (1080 * 1920)
    scale = area_ratio ** 0.5
    scale = max(0.7, min(1.3, scale))
    
    return {
        'margin': int(base_margin * scale),
        'y_start': int(base_y_start * scale),
        'padding': int(base_padding * scale),
        'line_height': int(50 * scale),
        'section_gap': int(40 * scale)
    }

# AI 이미지 생성 함수들
def extract_keywords_from_content(card_content):
    """카드 내용에서 이미지 생성용 키워드 추출"""
    
    # 한글 키워드를 영어로 매핑
    korean_to_english = {
        "예산": "budget money finance",
        "관리": "management organization",
        "결혼": "wedding marriage",
        "예식": "ceremony celebration",
        "드레스": "dress fashion elegant",
        "허니문": "honeymoon travel romantic",
        "신혼집": "home house interior",
        "웨딩": "wedding bride groom",
        "투자": "investment finance business",
        "주식": "stock market finance",
        "부동산": "real estate property",
        "창업": "startup business entrepreneur",
        "마케팅": "marketing business strategy",
        "건강": "health wellness fitness",
        "요리": "cooking food kitchen",
        "여행": "travel adventure journey",
        "교육": "education learning study",
        "기술": "technology innovation digital",
        "패션": "fashion style trendy",
        "뷰티": "beauty cosmetics skincare"
    }
    
    keywords = []
    content_lower = card_content.lower()
    
    for korean, english in korean_to_english.items():
        if korean in content_lower:
            keywords.append(english)
    
    return " ".join(keywords[:3])  # 최대 3개 키워드만 사용

@st.cache_data
def generate_ai_background_advanced(card_content, card_number, theme="비즈니스", width=1080, height=1920, style="modern"):
    """고품질 AI 배경 이미지 생성 (카드별 맞춤형)"""
    
    # 카드 내용에서 키워드 추출
    content_keywords = extract_keywords_from_content(card_content)
    
    # 테마별 기본 프롬프트
    theme_prompts = {
        "비즈니스": "professional business office modern clean minimal",
        "자연": "nature landscape beautiful serene peaceful outdoor",
        "기술": "technology futuristic digital modern innovation tech",
        "음식": "food cooking kitchen restaurant culinary delicious",
        "여행": "travel destination adventure scenic beautiful landscape",
        "패션": "fashion style elegant modern trendy lifestyle",
        "교육": "education learning study books knowledge academic",
        "건강": "health wellness fitness lifestyle clean minimalist",
        "라이프스타일": "lifestyle modern cozy comfortable home living",
        "창의적": "creative artistic colorful vibrant inspiring abstract"
    }
    
    base_prompt = theme_prompts.get(theme, "modern minimalist professional")
    
    # 카드별 고유 프롬프트 생성
    card_specific_prompt = f"{base_prompt} {content_keywords} card{card_number}"
    
    # 다양한 AI 이미지 API 시도 (우선순위대로)
    ai_apis = [
        ("pollinations", generate_pollinations_image),
        ("lorem_picsum_varied", generate_varied_picsum),
        ("unsplash_source", generate_unsplash_source),
        ("placeholder_pics", generate_placeholder_pics)
    ]
    
    for api_name, api_function in ai_apis:
        try:
            with st.spinner(f"🎨 {api_name}로 '{theme}' 테마 배경 생성 중... (카드 {card_number})"):
                img = api_function(card_specific_prompt, width, height, card_number)
                
                if img:
                    # 스타일 후처리 적용
                    img = apply_image_effects(img, style)
                    st.success(f"✅ {api_name}으로 카드 {card_number} 배경 생성 완료!")
                    return img
                    
        except Exception as e:
            st.warning(f"⚠️ {api_name} 실패: {e}")
            continue
    
    # 모든 API 실패시 고급 그라데이션으로 대체
    st.warning(f"모든 AI API 실패. 고급 그라데이션으로 대체합니다.")
    return create_advanced_gradient(width, height, theme, card_number)

def generate_pollinations_image(prompt, width, height, card_number):
    """Pollinations AI API로 고품질 이미지 생성"""
    try:
        # Pollinations API 엔드포인트
        base_url = "https://image.pollinations.ai/prompt/"
        
        # 프롬프트 최적화 (안전한 인코딩)
        optimized_prompt = f"{prompt} high quality professional photography 4k ultra detailed"
        # URL 인코딩
        import urllib.parse
        optimized_prompt = urllib.parse.quote(optimized_prompt)
        
        # 카드별 시드 생성 (다른 이미지를 위해)
        seed = abs(hash(f"{prompt}_{card_number}")) % 10000
        
        # API URL 구성
        api_url = f"{base_url}{optimized_prompt}?width={width}&height={height}&seed={seed}&enhance=true&model=flux"
        
        # 이미지 요청
        response = requests.get(api_url, timeout=45)
        response.raise_for_status()
        
        # 이미지 검증 및 변환
        img = Image.open(io.BytesIO(response.content))
        
        # 이미지 크기 검증
        if img.size != (width, height):
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # RGB 모드로 확실히 변환
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        return img
        
    except Exception as e:
        st.warning(f"Pollinations API 오류: {e}")
        return None

def generate_varied_picsum(prompt, width, height, card_number):
    """다양한 Picsum 이미지 생성 (카드별 다름)"""
    try:
        # 프롬프트와 카드 번호로 시드 생성
        seed = abs(hash(f"{prompt}_{card_number}")) % 1000
        
        # 다양한 이미지를 위해 카테고리별 시드 범위 설정
        category_seeds = {
            "business": range(100, 200),
            "nature": range(200, 300),
            "technology": range(300, 400),
            "food": range(400, 500),
            "lifestyle": range(500, 600),
            "wedding": range(600, 700),
            "finance": range(700, 800)
        }
        
        # 프롬프트에서 카테고리 감지
        category = "business"  # 기본값
        for cat in category_seeds.keys():
            if cat in prompt.lower():
                category = cat
                break
        
        # 해당 카테고리의 시드 범위에서 선택
        seed_range = category_seeds[category]
        actual_seed = seed_range.start + (seed % len(seed_range))
        
        # Picsum API 호출
        url = f"https://picsum.photos/seed/{actual_seed}/{width}/{height}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 이미지 처리
        img = Image.open(io.BytesIO(response.content))
        
        # 크기 및 모드 검증
        if img.size != (width, height):
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        return img
        
    except Exception as e:
        st.warning(f"Varied Picsum 오류: {e}")
        return None

def generate_unsplash_source(prompt, width, height, card_number):
    """Unsplash Source API로 테마별 이미지 생성"""
    try:
        # 프롬프트에서 검색어 추출 (안전하게)
        search_terms = [term.strip() for term in prompt.replace(" ", ",").split(",") if term.strip()][:3]
        search_query = ",".join(search_terms) if search_terms else "business"
        
        # Unsplash Source API
        url = f"https://source.unsplash.com/{width}x{height}/?{search_query}"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 이미지 처리
        img = Image.open(io.BytesIO(response.content))
        
        # 크기 및 모드 검증
        if img.size != (width, height):
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        return img
        
    except Exception as e:
        st.warning(f"Unsplash Source 오류: {e}")
        return None

def generate_placeholder_pics(prompt, width, height, card_number):
    """안전한 플레이스홀더 이미지 생성"""
    try:
        # 카드별 다른 색상 조합
        colors = [
            "#4A90E2",  # 파란색
            "#7ED321",  # 초록색
            "#F5A623",  # 주황색
            "#BD10E0",  # 보라색
            "#B8E986",  # 연두색
        ]
        
        bg_color = colors[card_number % len(colors)]
        
        # 간단한 색상 배경 생성
        img = Image.new('RGB', (width, height), bg_color)
        
        return img
        
    except Exception as e:
        st.warning(f"Placeholder 생성 오류: {e}")
        return None

def apply_image_effects(img, style):
    """이미지에 스타일 효과 적용 (안전한 처리)"""
    if not img:
        return img
    
    try:
        # RGB 모드 확인 및 변환
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if style == "blur":
            # 블러 효과 (텍스트 가독성 향상)
            img = img.filter(ImageFilter.GaussianBlur(radius=12))
        elif style == "dark":
            # 어둡게 처리
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.4)
        elif style == "vintage":
            # 빈티지 효과
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(0.8)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
        elif style == "modern":
            # 모던 효과 (대비 증가)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)
        
        # 최종 RGB 모드 확인
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        return img
        
    except Exception as e:
        st.warning(f"이미지 효과 적용 실패: {e}")
        # 실패시 원본 이미지를 RGB로 변환해서 반환
        try:
            return img.convert('RGB')
        except:
            return img

def create_advanced_gradient(width, height, theme, card_number):
    """고급 그라데이션 배경 생성 (카드별 다름)"""
    
    # 테마별 다양한 색상 조합
    theme_colors = {
        "비즈니스": [
            [(30, 60, 114), (42, 82, 152)],
            [(67, 56, 202), (147, 51, 234)],
            [(30, 58, 138), (59, 130, 246)]
        ],
        "자연": [
            [(34, 197, 94), (22, 163, 74)],
            [(16, 185, 129), (5, 150, 105)],
            [(101, 163, 13), (77, 124, 15)]
        ],
        "기술": [
            [(30, 41, 59), (55, 65, 81)],
            [(15, 23, 42), (30, 41, 59)],
            [(51, 65, 85), (71, 85, 105)]
        ],
        "블루 그라데이션": [
            [(52, 73, 219), (73, 150, 219)],
            [(30, 60, 114), (42, 82, 152)],
            [(67, 56, 202), (147, 51, 234)]
        ],
        "퍼플 그라데이션": [
            [(106, 90, 205), (147, 51, 234)],
            [(67, 56, 202), (147, 51, 234)],
            [(139, 69, 19), (202, 138, 4)]
        ],
        "그린 그라데이션": [
            [(46, 204, 113), (39, 174, 96)],
            [(34, 197, 94), (22, 163, 74)],
            [(16, 185, 129), (5, 150, 105)]
        ],
        "오렌지 그라데이션": [
            [(230, 126, 34), (231, 76, 60)],
            [(251, 146, 60), (249, 115, 22)],
            [(202, 138, 4), (161, 98, 7)]
        ],
        "다크 그라데이션": [
            [(44, 62, 80), (52, 73, 94)],
            [(30, 41, 59), (55, 65, 81)],
            [(15, 23, 42), (30, 41, 59)]
        ],
        "핑크 그라데이션": [
            [(253, 121, 168), (232, 93, 117)],
            [(244, 114, 182), (219, 39, 119)],
            [(236, 72, 153), (190, 24, 93)]
        ],
        "민트 그라데이션": [
            [(26, 188, 156), (22, 160, 133)],
            [(16, 185, 129), (5, 150, 105)],
            [(45, 212, 191), (20, 184, 166)]
        ],
        "선셋 그라데이션": [
            [(255, 94, 77), (255, 154, 0)],
            [(251, 146, 60), (249, 115, 22)],
            [(245, 101, 101), (254, 178, 178)]
        ]
    }
    
    # 기본 색상
    default_colors = [
        [(52, 73, 219), (73, 150, 219)],
        [(106, 90, 205), (147, 51, 234)],
        [(46, 204, 113), (39, 174, 96)]
    ]
    
    colors = theme_colors.get(theme, default_colors)
    start_color, end_color = colors[card_number % len(colors)]
    
    img = Image.new('RGB', (width, height))
    
    # 대각선 그라데이션 효과
    for y in range(height):
        for x in range(width):
            # 대각선 비율 계산
            ratio_y = y / height
            ratio_x = x / width
            ratio = (ratio_y + ratio_x) / 2
            
            # 부드러운 그라데이션
            ratio = ratio * ratio * (3.0 - 2.0 * ratio)
            
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            
            img.putpixel((x, y), (r, g, b))
    
    return img

def get_text_dimensions(text, font):
    """텍스트의 정확한 크기 측정"""
    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def wrap_text(text, font, max_width):
    """개선된 텍스트 자동 줄바꿈 (한글 최적화)"""
    if not text:
        return []
    
    lines = []
    
    # 한글 특성상 단어 단위보다는 글자 단위로 처리하는 것이 더 효과적
    current_line = ""
    
    for char in text:
        test_line = current_line + char
        text_width, _ = get_text_dimensions(test_line, font)
        
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = char
            else:
                # 한 글자도 들어가지 않는 경우 (거의 없겠지만)
                lines.append(char)
                current_line = ""
    
    if current_line:
        lines.append(current_line)
    
    # 빈 라인 제거
    lines = [line for line in lines if line.strip()]
    
    return lines

def draw_text_with_shadow(draw, position, text, font, text_color='white', shadow_color=(0, 0, 0, 180), shadow_offset=(3, 3)):
    """그림자 효과가 있는 텍스트 그리기"""
    x, y = position
    
    # 그림자 그리기
    draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=shadow_color)
    
    # 메인 텍스트 그리기
    draw.text((x, y), text, font=font, fill=text_color)

def create_carousel_card(card_data, card_number, total_cards, background_type="ai", theme="비즈니스", width=1080, height=1920):
    """캐러셀용 개별 카드 생성 (플랫폼별 크기 최적화)"""
    
    # 카드 내용 조합 (키워드 추출용)
    card_content = f"{card_data.get('title', '')} {card_data.get('subtitle', '')} {card_data.get('content', '')}"
    
    # 배경 생성 (카드별 다른 이미지)
    if background_type == "ai":
        img = generate_ai_background_advanced(
            card_content=card_content,
            card_number=card_number,
            theme=theme, 
            width=width, 
            height=height, 
            style="blur"
        )
        if img is None:
            # AI 생성 실패시 고급 그라데이션으로 대체
            img = create_advanced_gradient(width, height, theme, card_number)
    else:
        # 그라데이션도 카드별로 다르게
        img = create_advanced_gradient(width, height, theme, card_number)
    
    # 이미지 모드 통일 (RGB로 변환)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # 텍스트 가독성을 위한 어두운 효과
    try:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.7)  # 30% 어둡게
    except Exception as e:
        st.warning(f"이미지 어둡게 처리 실패: {e}")
    
    draw = ImageDraw.Draw(img)
    
    # 플랫폼별 최적화된 폰트 크기 및 간격 계산
    font_sizes = get_optimized_font_sizes(width, height)
    spacing = get_optimized_spacing(width, height)
    
    # 폰트 로드 (플랫폼별 최적화)
    title_font = get_korean_font(font_sizes['title'], 'bold')
    subtitle_font = get_korean_font(font_sizes['subtitle'], 'regular')
    content_font = get_korean_font(font_sizes['content'], 'regular')
    page_font = get_korean_font(font_sizes['page'], 'regular')
    
    if not title_font:
        return None
    
    margin = spacing['margin']
    y_position = spacing['y_start']
    
    # 페이지 번호 표시 (우상단)
    page_text = f"{card_number}/{total_cards}"
    page_width, page_height = get_text_dimensions(page_text, page_font)
    page_margin = max(15, width // 72)
    
    draw.rectangle([width - page_width - page_margin*2, page_margin, 
                   width - page_margin//2, page_margin + page_height + page_margin], 
                  fill=(255, 255, 255, 200))
    draw.text((width - page_width - page_margin, page_margin + page_margin//2), 
              page_text, font=page_font, fill='#2c3e50')
    
    # 1. 제목 그리기
    title = card_data.get('title', '')
    if title:
        title_lines = wrap_text(title, title_font, width - margin * 2)
        
        for line in title_lines:
            text_width, text_height = get_text_dimensions(line, title_font)
            x = (width - text_width) // 2
            
            # 제목 배경
            padding = spacing['padding']
            draw.rectangle([x - padding, y_position - padding//2, 
                          x + text_width + padding, y_position + text_height + padding//2], 
                         fill=(0, 0, 0, 160))
            
            # 텍스트 그리기 (그림자 효과)
            shadow_offset = (max(2, width//540), max(2, height//960))
            draw_text_with_shadow(draw, (x, y_position), line, title_font, 'white', 
                                shadow_offset=shadow_offset)
            
            y_position += text_height + spacing['line_height']//3
        
        y_position += spacing['section_gap']
    
    # 2. 부제목 그리기
    subtitle = card_data.get('subtitle', '')
    if subtitle:
        subtitle_lines = wrap_text(subtitle, subtitle_font, width - margin * 2)
        
        for line in subtitle_lines:
            text_width, text_height = get_text_dimensions(line, subtitle_font)
            x = (width - text_width) // 2
            
            # 부제목 배경
            padding = int(spacing['padding'] * 0.8)
            draw.rectangle([x - padding, y_position - padding//2, 
                          x + text_width + padding, y_position + text_height + padding//2], 
                         fill=(255, 255, 255, 220))
            
            draw.text((x, y_position), line, font=subtitle_font, fill='#2c3e50')
            
            y_position += text_height + spacing['line_height']//4
        
        y_position += int(spacing['section_gap'] * 1.5)
    
    # 3. 내용 그리기
    content = card_data.get('content', '')
    if content:
        content_
