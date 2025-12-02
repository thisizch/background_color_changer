import streamlit as st
from PIL import Image, ImageFilter
import io

TARGET_WIDTH = 1200
TARGET_HEIGHT = 2600


def make_wallpaper(image: Image.Image, method: str = "Blurred background") -> Image.Image:
    """원본 비율은 유지하면서 1200x2600 배경화면으로 확장."""
    # RGB로 통일
    img = image.convert("RGB")

    # 전경(원본) 이미지: 비율 유지한 채로 축소
    foreground = img.copy()
    foreground.thumbnail((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)

    # 배경 이미지 생성
    if method == "Blurred background":
        # 원본을 전체 크기로 키운 뒤 블러
        background = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)
        background = background.filter(ImageFilter.GaussianBlur(radius=50))
    else:
        # 평균 색상으로 단색 배경
        avg_color = img.resize((1, 1), Image.LANCZOS).getpixel((0, 0))
        background = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), avg_color)

    # 전경 이미지를 가운데에 붙이기
    x = (TARGET_WIDTH - foreground.width) // 2
    y = (TARGET_HEIGHT - foreground.height) // 2
    background.paste(foreground, (x, y))

    return background


def main():
    st.set_page_config(page_title="배경화면 리사이저 1200x2600", layout="centered")
    st.title("📱 휴대폰 배경화면 리사이저 (1200 x 2600)")
    st.write("사진을 업로드하면 **비율은 그대로** 두고, "
             "빈 부분만 채워서 1200x2600 사이즈로 만들어 줍니다.")

    method = st.radio(
        "배경 확장 방식",
        ["Blurred background", "Solid color (average)"],
        index=0,
        horizontal=True
    )

    uploaded_file = st.file_uploader(
        "이미지를 업로드하세요 (JPG, JPEG, PNG)",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("원본 이미지")
            st.image(image, use_container_width=True)
            st.text(f"원본 해상도: {image.width} x {image.height}")

        # 변환
        result = make_wallpaper(image, method=method)

        with col2:
            st.subheader("배경화면용 이미지")
            st.image(result, use_container_width=True)
            st.text(f"변환 해상도: {TARGET_WIDTH} x {TARGET_HEIGHT}")

        # 다운로드 버튼
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        buf.seek(0)

        st.download_button(
            label="📥 결과 이미지 다운로드 (PNG)",
            data=buf,
            file_name="wallpaper_1200x2600.png",
            mime="image/png"
        )
    else:
        st.info("좌측에서 이미지를 업로드하면 결과를 볼 수 있습니다.")


if __name__ == "__main__":
    main()
