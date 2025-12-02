import io
import random

import numpy as np
from PIL import Image
import streamlit as st


# ---------------------------
# 유틸 함수들
# ---------------------------
def generate_random_color():
    """랜덤 RGB 색상 생성 (0~255)."""
    return (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )


def change_background_color(img: Image.Image, threshold: int = 30):
    """
    이미지에서 '배경색(왼쪽 위 픽셀 기준)'과 비슷한 색을 랜덤 색으로 변경.
    threshold: 배경색과의 거리 허용치 (값이 클수록 더 넓은 영역이 배경으로 인식됨)
    """
    # RGBA로 변환 (알파 채널 보존)
    img = img.convert("RGBA")
    arr = np.array(img)

    # 배경 기준 색: 왼쪽 위 픽셀 색상
    bg_r, bg_g, bg_b, bg_a = arr[0, 0]

    # 배경과의 색상 거리 계산을 위해 RGB만 사용
    rgb = arr[..., :3].astype(np.int16)

    # (R,G,B)와 배경색 (bg_r,bg_g,bg_b) 사이의 유클리드 거리
    diff = np.sqrt(
        (rgb[..., 0] - bg_r) ** 2 +
        (rgb[..., 1] - bg_g) ** 2 +
        (rgb[..., 2] - bg_b) ** 2
    )

    # threshold 이내인 픽셀을 배경으로 간주
    mask = diff < threshold

    # 새 배경색 (알파는 기존 알파 사용)
    new_r, new_g, new_b, = generate_random_color()

    # 마스크가 True인 부분만 색 변경 (알파 채널은 그대로 두기)
    arr[mask, 0] = new_r
    arr[mask, 1] = new_g
    arr[mask, 2] = new_b

    return Image.fromarray(arr.astype("uint8"), mode="RGBA")


def pil_image_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    """PIL 이미지를 바이트로 변환 (다운로드용)."""
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf.getvalue()


# ---------------------------
# Streamlit 앱
# ---------------------------
def main():
    st.set_page_config(page_title="Random Background Colorizer", page_icon="🎨")

    st.title("🎨 랜덤 배경색 이미지 변환기")
    st.write(
        """
        배경이 **단색인 그림/사진**을 업로드하면  
        배경색(왼쪽 위 픽셀 기준)을 감지해서 **랜덤 색상**으로 바꿔줍니다.
        """
    )

    # 파일 업로드
    uploaded_file = st.file_uploader(
        "이미지 파일을 업로드하세요 (JPG, PNG 등)",
        type=["png", "jpg", "jpeg", "webp"],
    )

    # threshold 슬라이더 (배경 인식 민감도)
    threshold = st.slider(
        "배경 인식 threshold (값이 클수록 더 넓은 영역을 배경으로 인식)",
        min_value=5,
        max_value=100,
        value=30,
        step=5,
    )

    if uploaded_file is not None:
        # 원본 이미지 로드
        original_img = Image.open(uploaded_file)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("원본 이미지")
            st.image(original_img, use_column_width=True)

        # 변환 버튼
        if st.button("배경색 랜덤으로 바꾸기 🎲"):
            with st.spinner("배경색을 변경하는 중입니다..."):
                result_img = change_background_color(original_img, threshold=threshold)

            with col2:
                st.subheader("변환된 이미지")
                st.image(result_img, use_column_width=True)

            # 다운로드 버튼
            img_bytes = pil_image_to_bytes(result_img, fmt="PNG")
            st.download_button(
                label="변환된 이미지 다운로드 (PNG)",
                data=img_bytes,
                file_name="random_bg_image.png",
                mime="image/png",
            )
        else:
            with col2:
                st.info("👉 오른쪽 위 버튼을 눌러 배경색을 변경해 보세요.")
    else:
        st.info("위에 이미지를 업로드하면 여기에 미리보기가 표시됩니다.")


if __name__ == "__main__":
    main()
