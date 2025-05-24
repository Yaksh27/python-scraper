# Odisha RERA Projects Scraper

A Python-based Selenium web scraper to extract real estate project details from the [Odisha RERA portal](https://rera.odisha.gov.in/projects/project-list).

## Features

- Scrapes project name, RERA registration number, promoter details, address, and GST number
- Handles both company and proprietor edge cases
- Exports data to CSV (`odisha_rera_projects.csv`)
- Supports headless and non-headless Chrome

## Requirements

- Python 3.7+
- Google Chrome installed
- [ChromeDriver](https://chromedriver.chromium.org/downloads) compatible with your Chrome version
- `pip install`:
    - selenium
    - pandas

## Installation

1. Clone the repo:
    ```bash
    git clone https://github.com/YOUR_USERNAME/python_scraping.git
    cd python_scraping
    ```

2. Install dependencies:
    ```bash
    pip install selenium pandas
    ```

3. Make sure ChromeDriver is in your PATH or the project directory.

## Usage

```bash
python scraper.py
