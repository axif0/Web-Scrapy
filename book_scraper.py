#!/usr/bin/env python3
"""
Book Data Scraper for books.toscrape.com
Extracts book information including title, price, rating, stock, links, and images.
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import urllib.robotparser
from urllib.parse import urljoin
import sys
from typing import List, Dict, Optional


class BookScraper:
    """Scraper for books.toscrape.com with pagination, error handling, and robots.txt compliance."""
    
    def __init__(self, base_url: str = "https://books.toscrape.com/", delay: float = 1.0):
        """
        Initialize the scraper.
        
        Args:
            base_url: Base URL of the website
            delay: Delay between requests in seconds
        """
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.books_data = []
        self.robots_parser = None
        
    def check_robots_txt(self) -> bool:
        """
        Check robots.txt to ensure we can scrape the website.
        
        Returns:
            True if scraping is allowed, False otherwise
        """
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            self.robots_parser = urllib.robotparser.RobotFileParser()
            self.robots_parser.set_url(robots_url)
            self.robots_parser.read()
            
            # Check if we can fetch the main page
            can_fetch = self.robots_parser.can_fetch(self.session.headers['User-Agent'], self.base_url)
            print(f"Robots.txt check: {'Allowed' if can_fetch else 'Not allowed'}")
            return can_fetch
        except Exception as e:
            print(f"Warning: Could not check robots.txt: {e}")
            print("Proceeding with scraping (assuming allowed)...")
            return True
    
    def make_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """
        Make HTTP request with retry logic.
        
        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts
            
        Returns:
            Response object or None if all retries failed
        """
        for attempt in range(max_retries):
            try:
                # Check robots.txt before making request
                if self.robots_parser:
                    if not self.robots_parser.can_fetch(self.session.headers['User-Agent'], url):
                        print(f"Robots.txt disallows: {url}")
                        return None
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to fetch {url} after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    def parse_book(self, book_element: BeautifulSoup, base_url: str) -> Optional[Dict]:
        """
        Parse a single book element and extract required fields.
        
        Args:
            book_element: BeautifulSoup element containing book information
            base_url: Base URL for resolving relative links
            
        Returns:
            Dictionary with book data or None if parsing fails
        """
        try:
            # Title
            title_elem = book_element.select_one('h3 a')
            title = title_elem.get('title', '').strip() if title_elem else ''
            
            # Product detail page link
            link_elem = book_element.select_one('h3 a')
            relative_link = link_elem.get('href', '') if link_elem else ''
            product_link = urljoin(base_url, relative_link)
            
            # Price
            price_elem = book_element.select_one('p.price_color')
            price = price_elem.get_text(strip=True) if price_elem else ''
            
            # Rating (star rating)
            rating_elem = book_element.select_one('p.star-rating')
            rating_class = rating_elem.get('class', []) if rating_elem else []
            rating = ''
            for class_name in rating_class:
                if class_name.startswith('One') or class_name.startswith('Two') or \
                   class_name.startswith('Three') or class_name.startswith('Four') or \
                   class_name.startswith('Five'):
                    rating = class_name.replace('star-rating', '').strip()
                    break
            
            # Stock availability
            stock_elem = book_element.select_one('p.instock, p.outofstock')
            stock_text = stock_elem.get_text(strip=True) if stock_elem else ''
            # Clean up stock text
            if 'In stock' in stock_text or 'instock' in stock_text.lower():
                stock_availability = 'In stock'
            elif 'Out of stock' in stock_text or 'outofstock' in stock_text.lower():
                stock_availability = 'Out of stock'
            else:
                stock_availability = stock_text
            
            # Image URL
            image_elem = book_element.select_one('div.image_container img')
            image_src = image_elem.get('src', '') if image_elem else ''
            # Handle relative image URLs
            if image_src.startswith('../'):
                image_src = image_src.replace('../', '')
            image_url = urljoin(base_url, image_src)
            
            return {
                'title': title,
                'price': price,
                'rating': rating,
                'stock_availability': stock_availability,
                'product_page_url': product_link,
                'image_url': image_url
            }
        except Exception as e:
            print(f"Error parsing book element: {e}")
            return None
    
    def scrape_page(self, url: str) -> tuple[List[Dict], Optional[str]]:
        """
        Scrape a single page and return books data and next page URL.
        
        Args:
            url: URL of the page to scrape
            
        Returns:
            Tuple of (list of book dictionaries, next page URL or None)
        """
        print(f"Scraping page: {url}")
        response = self.make_request(url)
        
        if not response:
            return [], None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        books = []
        
        # Find all book elements
        book_elements = soup.select('article.product_pod')
        
        for book_elem in book_elements:
            book_data = self.parse_book(book_elem, url)
            if book_data:
                books.append(book_data)
        
        # Find next page link
        next_link = soup.select_one('li.next a')
        next_url = None
        if next_link:
            next_href = next_link.get('href', '')
            next_url = urljoin(url, next_href)
        
        print(f"Found {len(books)} books on this page")
        return books, next_url
    
    def scrape(self, min_records: int = 500) -> List[Dict]:
        """
        Scrape books from the website with pagination.
        
        Args:
            min_records: Minimum number of records to collect
            
        Returns:
            List of book dictionaries
        """
        print("Starting book scraping...")
        
        # Check robots.txt
        if not self.check_robots_txt():
            print("Warning: robots.txt may disallow scraping. Proceeding anyway...")
        
        current_url = self.base_url
        page_count = 0
        
        while current_url and len(self.books_data) < min_records:
            page_count += 1
            books, next_url = self.scrape_page(current_url)
            
            if books:
                self.books_data.extend(books)
                print(f"Total books collected: {len(self.books_data)}")
            else:
                print(f"No books found on page {page_count}")
            
            # Move to next page
            current_url = next_url
            
            # Add delay between requests
            if current_url and len(self.books_data) < min_records:
                time.sleep(self.delay)
        
        print("\nScraping completed!")
        print(f"Total pages scraped: {page_count}")
        print(f"Total books collected: {len(self.books_data)}")
        
        return self.books_data
    
    def export_to_csv(self, filename: str = 'books_data.csv'):
        """Export scraped data to CSV file."""
        if not self.books_data:
            print("No data to export!")
            return
        
        fieldnames = ['title', 'price', 'rating', 'stock_availability', 'product_page_url', 'image_url']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.books_data)
        
        print(f"Data exported to {filename}")
    
    def export_to_json(self, filename: str = 'books_data.json'):
        """Export scraped data to JSON file."""
        if not self.books_data:
            print("No data to export!")
            return
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.books_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Data exported to {filename}")


def main():
    """Main function to run the scraper."""
    print("=" * 60)
    print("Book Scraper for books.toscrape.com")
    print("=" * 60)
    
    scraper = BookScraper(delay=1.0)  # 1 second delay between requests
    books = scraper.scrape(min_records=1000)
    
    if books:
        # Export to both CSV and JSON
        scraper.export_to_csv('books_data.csv')
        scraper.export_to_json('books_data.json')
        print(f"\nSuccessfully collected {len(books)} book records!")
    else:
        print("No books were collected. Please check the website and try again.")
        sys.exit(1)


if __name__ == '__main__':
    main()

