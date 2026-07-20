import requests
from bs4 import BeautifulSoup
import re

def scrape_google_search(query):
    """Scrapes raw text summaries from duckduckgo/google search pages locally."""
    if not query.strip():
        return "No search query provided."
    
    print(f"\n[INTERNET ENGINE]: Searching the live web for: '{query}'...")
    
    # We use DuckDuckGo HTML view because it doesn't block local bots with heavy Captchas
    url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return "I am unable to reach the search servers at the moment."
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Pull text snippets from the search results layout
        snippets = soup.find_all('a', class_='result__snippet')
        
        if not snippets:
            return "No immediate search details found for this topic."
            
        # Compile the top 3 snippets into a clean, short summary block
        compiled_text = ""
        for i, snippet in enumerate(snippets[:3]):
            compiled_text += f"[{i+1}] {snippet.get_text().strip()}\n"
            
        # Clean out excess whitespaces or breaking tabs
        cleaned_summary = re.sub(r'\s+', ' ', compiled_text).strip()
        return cleaned_summary
        
    except Exception as e:
        return f"Internet lookup failed due to connection error: {e}"

if __name__ == "__main__":
    # Test our local scraping pipeline natively
    print("[TESTING SCRAPER]: Firing live request...")
    test_result = scrape_google_search("What is the latest news about Apple M4 chips")
    print(f"\n[LIVE DATA RETRIEVED]:\n{test_result}")