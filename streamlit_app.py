# streamlit_app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Agent Demo: eBay Lookup", layout="centered")
st.title("🔍 eBay Lookup Agent Demo")
st.write("Enter EAN, UPC, or keywords to see how an agent can fetch listings from eBay.com")

# Function to search eBay via web scraping

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

# UI for text input only
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
                    st.markdown(f"**Result {idx}:** [{item['title']}]({item['link']})  
  Price: {item['price']}")
        except Exception as e:
            st.error(f"Error during search: {e}")

st.markdown("---")
st.caption("Prototype demo – scrape-based lookup from ebay.com. Only text input supported.")
