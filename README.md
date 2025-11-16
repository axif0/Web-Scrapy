# Book Data Scraper

A web scraping project to extract book data from books.toscrape.com with proper pagination handling, error handling, and responsible scraping practices.

## Website URL Used

**https://books.toscrape.com/**

## Fields Extracted

The scraper extracts the following fields for each book:

1. **Title** - Book title
2. **Price** - Book price
3. **Rating** - Star rating (One, Two, Three, Four, Five)
4. **Stock Availability** - In stock / Out of stock status
5. **Product Page URL** - Link to the book's detail page
6. **Image URL** - URL of the book's cover image

![task](https://github.com/user-attachments/assets/636fc631-39d5-400e-b3a8-e10cb6168858)

## Total Records Collected

The scraper is configured to collect a minimum of **500 book records**. The website contains 1000 books total (20 books per page across 50 pages).

## Pagination Method Used

The scraper implements automatic pagination by:

1. Starting from the homepage (https://books.toscrape.com/)
2. Extracting all book data from the current page
3. Locating the "next" button/link using CSS selectors (`li.next a`)
4. Following the next page URL and repeating the process
5. Continuing until either:
   - The minimum record count (500) is reached, or
   - No more pages are available (all pages scraped)

The pagination logic handles relative URLs by converting them to absolute URLs using `urljoin()`.

## Challenges Faced and Solutions

### Challenge 1: Robots.txt Compliance
**Problem:** Need to respect robots.txt rules for responsible scraping.

**Solution:** Implemented `urllib.robotparser` to check robots.txt before making requests. The scraper checks if the User-Agent is allowed to access each URL.

### Challenge 2: Request Rate Limiting
**Problem:** Making too many requests too quickly could lead to IP blocking or server overload.

**Solution:** Implemented a configurable delay (default 1 second) between requests using `time.sleep()`. This ensures respectful scraping practices.

### Challenge 3: Error Handling and Retries
**Problem:** Network requests can fail due to various reasons (timeouts, server errors, etc.).

**Solution:** Implemented retry logic with exponential backoff:
- Maximum 3 retry attempts per request
- Exponential backoff: 2s, 4s, 6s delays between retries
- Proper exception handling for different types of request errors

### Challenge 4: Relative URL Handling
**Problem:** The website uses relative URLs for images and links that need to be converted to absolute URLs.

**Solution:** Used `urljoin()` from `urllib.parse` to properly resolve relative URLs to absolute URLs based on the current page URL.

### Challenge 5: Data Extraction Accuracy
**Problem:** Need to accurately extract all required fields from the HTML structure.

**Solution:** Used BeautifulSoup's CSS selectors to precisely target each field:
- Title: `h3 a` element's title attribute
- Price: `p.price_color` element text
- Rating: `p.star-rating` element's class attribute
- Stock: `p.instock` or `p.outofstock` element text
- Link: `h3 a` element's href attribute
- Image: `div.image_container img` element's src attribute

## Step-by-Step Instructions to Run the Script

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone or download this project** to your local machine.

2. **Navigate to the project directory:**
   ```bash
   cd /path/to/task
   ```

3. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   ```

4. **Activate the virtual environment:**
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

5. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Script

1. **Run the scraper:**
   ```bash
   python book_scraper.py
   ```

2. **Wait for completion:**
   - The script will display progress messages as it scrapes each page
   - It will show the number of books collected after each page
   - The script automatically stops after collecting 500+ records

3. **Check output files:**
   - `books_data.csv` - CSV format output
   - `books_data.json` - JSON format output

### Expected Output

The script will output:
- Progress messages for each page scraped
- Total number of books collected
- Confirmation of successful export to CSV and JSON files

Example output:
```
============================================================
Book Scraper for books.toscrape.com
============================================================
Robots.txt check: Allowed
Starting book scraping...
Scraping page: https://books.toscrape.com/
Found 20 books on this page
Total books collected: 20
Scraping page: https://books.toscrape.com/catalogue/page-2.html
Found 20 books on this page
Total books collected: 40
...
Scraping completed!
Total pages scraped: 25
Total books collected: 500
Data exported to books_data.csv
Data exported to books_data.json

Successfully collected 500 book records!
```

## Dependencies/Requirements

All dependencies are listed in `requirements.txt`:

- **requests** (>=2.31.0) - For making HTTP requests
- **beautifulsoup4** (>=4.12.0) - For parsing HTML content
- **lxml** (>=4.9.0) - HTML parser backend for BeautifulSoup

### Installing Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install requests beautifulsoup4 lxml
```

## Project Structure

```
task/
├── book_scraper.py      # Main scraping script
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── books_data.csv      # Output CSV file (generated after running)
└── books_data.json     # Output JSON file (generated after running)
```

## Features

✅ **Automatic Pagination** - Handles multiple pages automatically  
✅ **Request Throttling** - Configurable delay between requests (default: 1 second)  
✅ **Error Handling** - Retry logic with exponential backoff  
✅ **Robots.txt Compliance** - Checks and respects robots.txt rules  
✅ **Dual Export** - Exports data to both CSV and JSON formats  
✅ **Progress Tracking** - Real-time progress updates during scraping  
✅ **Robust Parsing** - Handles edge cases and malformed HTML gracefully  

## Notes

- The scraper is configured to collect a minimum of 500 records, but can collect all 1000 books if allowed to run completely.
- The default delay between requests is 1 second to ensure responsible scraping.
- The script includes proper error handling and will continue scraping even if individual pages fail.
- Both CSV and JSON output files are generated for convenience.

## Contact Information

**Name:** Md Asiful Alam 
**Email:** muhamadasif570@gmail.com

 
