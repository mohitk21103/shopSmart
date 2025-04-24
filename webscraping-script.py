import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from concurrent.futures import ThreadPoolExecutor

class EcommerceWebScraper:
    def __init__(self):
        # Headers to mimic a browser visit
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/'
        }
        # Session for maintaining cookies
        self.session = requests.Session()
        
    def get_amazon_results(self, search_query, max_results=5):
        """Scrape Amazon search results"""
        print(f"Searching Amazon for: {search_query}")
        
        # Format the search query for the URL
        search_query = search_query.replace(' ', '+')
        url = f"https://www.amazon.com/s?k={search_query}"
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to retrieve Amazon search results: Status code {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            products = []
            results = soup.select('div[data-component-type="s-search-result"]')
            
            for i, item in enumerate(results):
                if i >= max_results:
                    break
                    
                # Extract data
                try:
                    title_element = item.select_one('h2 a span')
                    title = title_element.text.strip() if title_element else "Title not found"
                    
                    url_element = item.select_one('h2 a')
                    url = "https://www.amazon.com" + url_element['href'] if url_element and 'href' in url_element.attrs else "#"
                    
                    price_element = item.select_one('.a-price .a-offscreen')
                    price = price_element.text.strip() if price_element else "Price not available"
                    
                    rating_element = item.select_one('.a-icon-star-small .a-icon-alt')
                    rating = rating_element.text.strip() if rating_element else "No ratings"
                    
                    image_element = item.select_one('img.s-image')
                    image_url = image_element['src'] if image_element and 'src' in image_element.attrs else ""
                    
                    products.append({
                        'title': title,
                        'price': price,
                        'rating': rating,
                        'url': url,
                        'image_url': image_url,
                        'source': 'Amazon'
                    })
                except Exception as e:
                    print(f"Error extracting Amazon product data: {e}")
                    continue
                    
            return products
            
        except Exception as e:
            print(f"Error scraping Amazon: {e}")
            return []
    
    def get_flipkart_results(self, search_query, max_results=5):
        """Scrape Flipkart search results"""
        print(f"Searching Flipkart for: {search_query}")
        
        # Format the search query for the URL
        search_query = search_query.replace(' ', '%20')
        url = f"https://www.flipkart.com/search?q={search_query}"
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to retrieve Flipkart search results: Status code {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            products = []
            results = soup.select('div._1AtVbE')
            
            count = 0
            for item in results:
                # Flipkart's structure can be complex, these selectors might need adjustment
                product_card = item.select_one('div._13oc-S') or item.select_one('div._4ddWXP')
                if not product_card:
                    continue
                
                try:
                    title_element = product_card.select_one('div._4rR01T') or product_card.select_one('a.s1Q9rs')
                    title = title_element.text.strip() if title_element else "Title not found"
                    
                    link_element = product_card.select_one('a._1fQZEK') or product_card.select_one('a.s1Q9rs')
                    url = "https://www.flipkart.com" + link_element['href'] if link_element and 'href' in link_element.attrs else "#"
                    
                    price_element = product_card.select_one('div._30jeq3')
                    price = price_element.text.strip() if price_element else "Price not available"
                    
                    rating_element = product_card.select_one('div._3LWZlK')
                    rating = rating_element.text.strip() + " stars" if rating_element else "No ratings"
                    
                    image_element = product_card.select_one('img._396cs4') or product_card.select_one('img._2r_T1I')
                    image_url = image_element['src'] if image_element and 'src' in image_element.attrs else ""
                    
                    products.append({
                        'title': title,
                        'price': price,
                        'rating': rating,
                        'url': url,
                        'image_url': image_url,
                        'source': 'Flipkart'
                    })
                    
                    count += 1
                    if count >= max_results:
                        break
                        
                except Exception as e:
                    print(f"Error extracting Flipkart product data: {e}")
                    continue
                    
            return products
            
        except Exception as e:
            print(f"Error scraping Flipkart: {e}")
            return []
    
    def search_products(self, query, max_results=5):
        """Search for products on both platforms concurrently"""
        all_results = []
        
        # Using ThreadPoolExecutor to run searches concurrently
        with ThreadPoolExecutor(max_workers=2) as executor:
            amazon_future = executor.submit(self.get_amazon_results, query, max_results)
            
            # Short delay to avoid triggering anti-scraping measures
            time.sleep(random.uniform(1, 3))
            
            flipkart_future = executor.submit(self.get_flipkart_results, query, max_results)
            
            amazon_results = amazon_future.result()
            flipkart_results = flipkart_future.result()
        
        all_results = amazon_results + flipkart_results
        return all_results
    
    def save_results_to_csv(self, results, filename="search_results.csv"):
        """Save results to CSV file"""
        if results:
            df = pd.DataFrame(results)
            df.to_csv(filename, index=False)
            print(f"Results saved to {filename}")
        else:
            print("No results to save")

# Example of how to use the scraper
def main():
    search_query = input("Enter product to search: ")
    
    scraper = EcommerceWebScraper()
    
    print(f"Searching for '{search_query}' on Amazon and Flipkart...")
    results = scraper.search_products(search_query)
    
    # Display results in console
    if results:
        print(f"\nFound {len(results)} results:")
        
        # Group by source
        amazon_results = [r for r in results if r['source'] == 'Amazon']
        flipkart_results = [r for r in results if r['source'] == 'Flipkart']
        
        print(f"\n--- Amazon Results ({len(amazon_results)}) ---")
        for i, product in enumerate(amazon_results, 1):
            print(f"{i}. {product['title']}")
            print(f"   Price: {product['price']}")
            print(f"   Rating: {product['rating']}")
            print(f"   URL: {product['url']}")
            print()
            
        print(f"\n--- Flipkart Results ({len(flipkart_results)}) ---")
        for i, product in enumerate(flipkart_results, 1):
            print(f"{i}. {product['title']}")
            print(f"   Price: {product['price']}")
            print(f"   Rating: {product['rating']}")
            print(f"   URL: {product['url']}")
            print()
        
        # Save results to CSV
        scraper.save_results_to_csv(results, f"{search_query.replace(' ', '_')}_results.csv")
    else:
        print("No results found.")

if __name__ == "__main__":
    main()
