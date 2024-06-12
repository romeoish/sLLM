import base64

import streamlit as st
from streamlit.components.v1 import html

# Define the full-width image URL
# Define the relative path to the image in the static folder

header_image_path = "static/header.png"
header_image_data = base64.b64encode(open(header_image_path, "rb").read()).decode()

bg_image_path = "static/bg.png"
bg_image_data = base64.b64encode(open(bg_image_path, "rb").read()).decode()


def remove_height_from_html_elements():
    st.markdown(
        """
            <style>
            .element-container:has(iframe[height="0"]) {
                display: none;
            }

            /* Reduce padding-top */
            [data-testid="ScrollToBottomContainer"] > [data-testid="block-container"] {
                padding-top: 1rem;
            }

            /* Remove the gap between all elements */
            [data-testid="ScrollToBottomContainer"] > [data-testid="block-container"] > [data-testid="stVerticalBlockBorderWrapper"] > .st-emotion-cache-1wmy9hl.e1f1d6gn1 > [data-testid="stVerticalBlock"] {
                gap: 0rem;
            }

            /* Add gap after elements explicitly. If you want to have a gap between elements, copy the line here and change the selector at the end. */
            [data-testid="ScrollToBottomContainer"] > [data-testid="block-container"] > [data-testid="stVerticalBlockBorderWrapper"] > .st-emotion-cache-1wmy9hl.e1f1d6gn1 > [data-testid="stVerticalBlock"] >.stChatMessage,
            [data-testid="ScrollToBottomContainer"] > [data-testid="block-container"] > [data-testid="stVerticalBlockBorderWrapper"] > .st-emotion-cache-1wmy9hl.e1f1d6gn1 > [data-testid="stVerticalBlock"] > .stButton  {
                margin-bottom: 1rem;
            }
            </style>
        """,
        unsafe_allow_html=True,
    )


def add_header():
    st.markdown(
        """
        <style>
            .full-width-header {
                position: relative;
                z-index: 9999999999;
                background-color: #D0D1C7;
                width: 100vw;
                height: 300px;  /* Adjust the height as needed */
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;  /* Set the text color to contrast with the image */
                font-size: 24px;  /* Set the font size as needed */
                overflow: hidden;  /* Hide the scrollbars */
            }
            .full-width-header img {
                width: auto;
                min-height: 100%;
                height: 100%;
                object-fit: contain;
            }
            iframe {
                height: 0rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    html(
        f"""
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const customHeader = window.parent.document.querySelector('.full-width-header');

            if (customHeader) {{
                return;
            }}
            const stApp = window.parent.document.querySelector('[data-testid="stApp"]');
            const stAppViewContainer = window.parent.document.querySelector(
                '[data-testid="stAppViewContainer"]'
            );
            const stHeader = window.parent.document.querySelector(
                '[data-testid="stHeader"]'
            );

            // set position relative to app and app view container
            stApp.style.position = 'relative';
            stAppViewContainer.style.position = 'relative';

            // add an element as the first child of stAppViewContainer
            const newElement = document.createElement('div');
            newElement.className = 'full-width-header';

            // add an image as the first child of newElement
            const img = document.createElement('img');
            img.src = 'data:image/png;base64,{header_image_data}';
            img.alt = 'Header Image';
            newElement.appendChild(img);

            stHeader.insertAdjacentElement('afterend', newElement);
        }});
    </script>
        """,
        height=0,
    )


def add_bg_image():
    st.markdown(
        """
        <style>
        .reportview-container {
            background-color: transparent;
        }
        .sidebar .sidebar-content {
            background-color: transparent;
        }
        .stChatFloatingInputContainer {
            background-color: transparent;
        }
        .stApp{
            background-color: transparent;
        }
        .st-emotion-cache-j5kadu{
            width: 100vw;
            left: 0;
            display: flex;
            justify-content: center;
            background-color: rgba(232, 232, 227, 0.5);
            border-top: 1px solid rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);  /* Add the frosted glass effect */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    page_bg_img = f"""
    <style>
    body {{
        background-image: url(data:image/png;base64,{bg_image_data});
        background-size: cover;
        background-attachment: fixed;
        width: 100vw;
        height: 100vh;
        overflow-x: hidden;
        overflow-y: scroll;
    }}
    </style>
    """

    st.markdown(page_bg_img, unsafe_allow_html=True)


def customise_design():
    remove_height_from_html_elements()
    add_header()
    add_bg_image()
