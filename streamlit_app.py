import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
from PIL import Image
import tempfile
from pyzbar.pyzbar import decode

st.set_page_config(page_title="Agent Demo: eBay Lookup", layout="centered")
st.title("🔍 eBay Lookup Agent Demo")
st.write("Upload a product image (with a barcode) or enter keywords/EAN to see how an agent can fetch listings from eBay.com")

def decode_barcode_from_image(image_path):
    img = Image.open(image_path)
    barcodes = decode(img)
    return barcodes[0].data.decode('utf-8') if barcodes else None

def search_ebay_web(query, max_results=5):
    url = f"https://www.ebay.com/sch/i.html?_nkw={requests.utils.quote(query)}"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    items = []
    for li in soup.select('#srp-river-results ul.srp-results li.s-item')[:max_results]:
        title_tag = li.select_one('.s-item__title')
        price_tag = li.select_one('.s-item__price')
        link_tag  = li.select_one('.s-item__link')
        if title_tag and link_tag:
            items.append({
                'title': title_tag.get_text(),
                'price': price_tag.get_text() if price_tag else 'N/A',
                'link':  link_tag['href'],
            })
    return items

mode = st.radio("Input mode:", ["Upload Image", "Enter Text Query"], index=0)
query = None

if mode == "Upload Image":
    uploaded = st.file_uploader("Upload a photo of your product (with barcode):", type=['png','jpg','jpeg'])
    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1]) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name
        st.image(tmp_path, caption="Uploaded Image", use_column_width=True)
        with st.spinner("Decoding barcode..."):
            code = decode_barcode_from_image(tmp_path)
        if code:
            st.success(f"Detected barcode: {code}")
            query = code
        else:
            st.warning("No barcode detected — please switch to Text Query mode.")

elif mode == "Enter Text Query":
    query = st.text_input("Enter EAN, UPC, or keywords:")

limit = st.slider("How many results to fetch?", 1, 10, 5)
if query and st.button("🔍 Search eBay"):
    with st.spinner(f"Searching eBay for '{query}'..."):
        try:
            results = search_ebay_web(query, max_results=limit)
            if not results:
                st.error("No results found.")
            else:
                for idx, item in enumerate(results, 1):
                    st.markdown(f"**Result {idx}:** [{item['title']}]({item['link']})  \nPrice: {item['price']}")
        except Exception as e:
            st.error(f"Error during search: {e}")

st.markdown("---")
st.caption("Prototype demo – scrape-based lookup from ebay.com. Not for production use.")
