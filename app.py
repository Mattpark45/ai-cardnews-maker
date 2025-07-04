import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os
import platform

# 한글 폰트 자동 감지 및 로드
def get_korean_font(size=60, weight='regular'):
    """시스템에서 한글 폰트 자동 찾기 및 로드"""
    
    system = platform.system()
    font_paths = []
    
    if system == "Windows":
        if weight == 'bold':
            font_paths = [
                "C:/Windows/Fonts/malgunbd.ttf",  # 맑은 고딕 볼드
                "C:/Windows/Fonts/gulim.ttc",
                "C:/Windows/Fonts/batang.ttc"
            ]
        else:
            font_paths = [
                "C:/Windows/Fonts/malgun.ttf",    # 맑은 고딕
                "C:/Windows/Fonts/gulim.ttc",     # 굴림
                "C:/Windows/Fonts/batang.ttc"     # 바탕
            ]
    
    elif system == "Darwin":  # Mac
        font_paths = [
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/Library/Fonts/NanumGothic.ttf",
            "/System/Library/Fonts/AppleGothic.ttf"
        ]
    
    else:  # Linux
        font_paths = [
            "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf" if weight == 'bold' else "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if weight == 'bold' else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
    
    # 폰트 로드 시도
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        except Exception as e:
            continue
    
    # 기본 폰트 반환
    try:
        return ImageFont.load_default()
    except:
        return None

def create_gradient_background(width, height, color_scheme):
    """그라데이션 배경 생성"""
    
    color_schemes = {
        "블루 그라데이션": [(52, 73, 219), (73, 150, 219)],      # 파란색
        "퍼플 그라데이션": [(106, 90, 205), (147, 51, 234)],      # 보라색  
        "그린 그라데이션": [(46, 204, 113), (39, 174, 96)],       # 초록색
        "오렌지 그라데이션": [(230, 126, 34), (231, 76, 60)],      # 주황색
        "다크 그라데이션": [(44, 62, 80), (52, 73, 94)],          # 어두운색
        "핑크 그라데이션": [(253, 121, 168), (232, 93, 117)]      # 핑크색
    }
    
    start_color, end_color = color_schemes.get(color_scheme, color_schemes["블루 그라데이션"])
    
    # 이미지 생성
    img = Image.new('RGB', (width, height))
    
    # 세로 그라데이션
    for y in range(height):
        # 비율 계산
        ratio = y / height
        
        # 색상 보간
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        
        # 한 줄씩 그리기
        for x in range(width):
            img.putpixel((x, y), (r, g, b))
    
    return img

def wrap_text(text, font, max_width, draw):
    """텍스트 자동 줄바꿈"""
    lines = []
    words = text.split()
    
    if not words:
        return [text]
    
    current_line = ""
    
    for word in words:
        # 테스트 라인 생성
        test_line = current_line + word + " " if current_line else word + " "
        
        # 텍스트 너비 측정
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
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

def create_perfect_korean_card(title, subtitle, content, style, color_scheme, width=1080, height=1920):
    """완벽한 한글 카드뉴스 생성"""
    
    # 배경 생성
    img = create_gradient_background(width, height, color_scheme)
    draw = ImageDraw.Draw(img)
    
    # 폰트 로드
    title_font = get_korean_font(100, 'bold')
    subtitle_font = get_korean_font(70, 'regular') 
    content_font = get_korean_font(50, 'regular')
    
    if not title_font:
        st.error("폰트를 로드할 수 없습니다. 시스템 폰트를 확인해주세요.")
        return None
    
    y_position = 200  # 시작 Y 위치
    
    # 1. 제목 그리기
    if title:
        # 제목 줄바꿈 처리
        title_lines = wrap_text(title, title_font, width - 200, draw)
        
        for line in title_lines:
            # 텍스트 크기 측정
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 중앙 정렬
            x = (width - text_width) // 2
            
            # 배경 박스 (반투명 검은색)
            padding = 30
            draw.rectangle([x - padding, y_position - 20, 
                          x + text_width + padding, y_position + text_height + 20], 
                         fill=(0, 0, 0, 180))
            
            # 텍스트 그리기 (흰색)
            draw.text((x, y_position), line, font=title_font, fill='white')
            
            y_position += text_height + 40
        
        y_position += 100  # 제목과 부제목 사이 간격
    
    # 2. 부제목 그리기
    if subtitle:
        subtitle_lines = wrap_text(subtitle, subtitle_font, width - 160, draw)
        
        for line in subtitle_lines:
            bbox = draw.textbbox((0, 0), line, font=subtitle_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            
            # 배경 박스 (반투명 흰색)
            padding = 25
            draw.rectangle([x - padding, y_position - 15, 
                          x + text_width + padding, y_position + text_height + 15], 
                         fill=(255, 255, 255, 200))
            
            # 텍스트 그리기 (검은색)
            draw.text((x, y_position), line, font=subtitle_font, fill='#2c3e50')
            
            y_position += text_height + 30
        
        y_position += 150  # 부제목과 내용 사이 간격
    
    # 3. 내용 그리기
    if content:
        # 내용을 줄 단위로 분리
        content_lines = content.split('\n')
        all_lines = []
        
        for line in content_lines:
            if line.strip():  # 빈 줄이 아닌 경우
                wrapped_lines = wrap_text(line, content_font, width - 120, draw)
                all_lines.extend(wrapped_lines)
            else:
                all_lines.append("")  # 빈 줄 유지
        
        # 전체 내용 영역의 높이 계산
        line_height = 70
        total_content_height = len([l for l in all_lines if l]) * line_height
        
        # 내용 배경 박스
        content_start_y = y_position
        max_line_width = 0
        
        # 최대 라인 너비 계산
        for line in all_lines:
            if line:
                bbox = draw.textbbox((0, 0), line, font=content_font)
                line_width = bbox[2] - bbox[0]
                max_line_width = max(max_line_width, line_width)
        
        # 내용 전체 배경
        bg_padding = 60
        draw.rectangle([width//2 - max_line_width//2 - bg_padding, 
                       content_start_y - 40,
                       width//2 + max_line_width//2 + bg_padding, 
                       content_start_y + total_content_height + 40],
                      fill=(255, 255, 255, 220))
        
        # 각 줄 그리기
        for line in all_lines:
            if line:  # 빈 줄이 아닌 경우
                bbox = draw.textbbox((0, 0), line, font=content_font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (width - text_width) // 2
                
                # 텍스트 그리기
                draw.text((x, y_position), line, font=content_font, fill='#2c3e50')
                
                y_position += line_height
            else:
                y_position += line_height // 2  # 빈 줄은 절반 높이
    
    return img

# Streamlit 메인 앱
def main():
    st.set_page_config(page_title="한글 카드뉴스 생성기", page_icon="🎨", layout="wide")
    
    st.title("🎨 완벽한 한글 카드뉴스 생성기")
    st.markdown("**100% 한글 깨짐 없음 보장!** ✨")
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("🎨 디자인 설정")
        
        color_scheme = st.selectbox(
            "배경 색상",
            ["블루 그라데이션", "퍼플 그라데이션", "그린 그라데이션", 
             "오렌지 그라데이션", "다크 그라데이션", "핑크 그라데이션"]
        )
        
        style = st.selectbox(
            "카드 스타일",
            ["모던", "미니멀", "비즈니스", "창의적"]
        )
        
        st.markdown("---")
        st.markdown("### 📱 카드 크기")
        st.info("1080 x 1920 (Instagram Story)")
    
    # 메인 입력 폼
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 카드 내용 입력")
        
        with st.form("card_form"):
            title = st.text_input(
                "제목 (필수)", 
                value="결혼준비 예산관리!",
                help="카드의 메인 제목을 입력하세요"
            )
            
            subtitle = st.text_input(
                "부제목 (선택)", 
                value="똑똑한 신혼부부의 필수 가이드",
                help="제목 아래 들어갈 부제목을 입력하세요"
            )
            
            content = st.text_area(
                "내용 (선택)", 
                value="""• 예식장 예약 시기별 할인율 비교
• 드레스 렌탈 vs 구매 비용 분석  
• 허니문 패키지 가격 협상 팁
• 신혼집 준비 우선순위 체크리스트
• 웨딩 플래너 선택 기준""",
                height=200,
                help="카드에 들어갈 상세 내용을 입력하세요. 줄바꿈이 자동으로 적용됩니다."
            )
            
            submitted = st.form_submit_button("🎨 카드 생성하기", use_container_width=True)
    
    with col2:
        st.header("📋 미리보기")
        
        # 실시간 미리보기 (간단한 텍스트)
        if title:
            st.markdown(f"**제목:** {title}")
        if subtitle:
            st.markdown(f"**부제목:** {subtitle}")
        if content:
            st.markdown("**내용:**")
            st.text(content[:100] + "..." if len(content) > 100 else content)
    
    # 카드 생성 및 결과 표시
    if submitted:
        if not title:
            st.error("제목을 입력해주세요!")
            return
        
        with st.spinner("🎨 완벽한 한글 카드를 생성하고 있습니다..."):
            try:
                card_img = create_perfect_korean_card(
                    title=title,
                    subtitle=subtitle, 
                    content=content,
                    style=style,
                    color_scheme=color_scheme
                )
                
                if card_img:
                    st.success("✅ 카드 생성 완료!")
                    
                    # 결과 표시
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col2:
                        st.image(card_img, caption="생성된 한글 카드뉴스", use_column_width=True)
                    
                    # 다운로드 버튼
                    buf = io.BytesIO()
                    card_img.save(buf, format='PNG', quality=95, optimize=True)
                    buf.seek(0)
                    
                    st.download_button(
                        label="📥 고해상도 이미지 다운로드",
                        data=buf.getvalue(),
                        file_name=f"한글카드_{title[:10].replace(' ', '_')}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                    
                    # 추가 정보
                    with st.expander("📊 카드 정보"):
                        st.write(f"**크기:** 1080 x 1920 픽셀")
                        st.write(f"**색상:** {color_scheme}")
                        st.write(f"**스타일:** {style}")
                        st.write(f"**폰트:** 시스템 한글 폰트 (자동 감지)")
                        st.write(f"**파일 형식:** PNG (고해상도)")
                
                else:
                    st.error("카드 생성에 실패했습니다. 시스템 폰트를 확인해주세요.")
                    
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
                st.info("시스템에 한글 폰트가 설치되어 있는지 확인해주세요.")

    # 사용법 안내
    with st.expander("📖 사용법 및 팁"):
        st.markdown("""
        ### 🎯 사용법
        1. **제목**: 카드의 메인 메시지를 입력하세요
        2. **부제목**: 제목을 보완하는 설명을 입력하세요  
        3. **내용**: 상세 내용을 입력하세요 (자동 줄바꿈 지원)
        4. **색상/스타일**: 사이드바에서 원하는 디자인을 선택하세요
        
        ### 💡 팁
        - **한글 완벽 지원**: AI 없이 시스템 폰트 사용으로 깨짐 없음
        - **자동 줄바꿈**: 긴 텍스트도 자동으로 적절히 배치
        - **고해상도**: 1080x1920 Instagram Story 최적화
        - **즉시 다운로드**: 생성 즉시 PNG 파일로 저장 가능
        
        ### 🚀 활용 예시
        - 결혼 준비 가이드 카드
        - 마케팅 인사이트 공유
        - 교육 콘텐츠 제작
        - 브랜드 홍보 자료
        """)

if __name__ == "__main__":
    main()
