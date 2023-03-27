import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO
import base64

st.set_page_config(layout="wide", page_title="Image Background Remover")

st.write("## Remove background from your image")

# Download the fixed image
def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im


def fix_image(upload):
    image = Image.open(upload)
    col1.write("Original Image :camera:")
    col1.image(image, width=500)

    fixed = remove(image)
    col2.write("Foreground :wrench:")
    col2.image(fixed, width=500)


# col1, col2 = st.columns(2)
c = st.container()
col1 = c
col2 = c

my_upload = st.sidebar.file_uploader(label="Image", type=["png", "jpg", "jpeg"])
st.sidebar.markdown("""
References:

- https://github.com/danielgatis/rembg
- https://blog.streamlit.io/build-an-image-background-remover-in-streamlit/
""")
                    
if my_upload is not None:
    fix_image(upload=my_upload)
else:
    fix_image("./zebra.jpg")
