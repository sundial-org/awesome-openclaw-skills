"""
ClawBack - Congressional Trade Data Collector
Fetches and processes public trade disclosures from:
- Official House Clerk data (disclosures-clerk.house.gov)
- Official Senate eFD data (efdsearch.senate.gov)
"""
import json
import logging
import requests
import re
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

logger = logging.getLogger(__name__)

class CongressTracker:
    """Collects and processes congressional trade data (House and Senate)"""

    def __init__(self, config):
        self.config = config
        self.data_source = config['congress']['dataSource']
        self.min_trade_size = config['congress']['minimumTradeSize']
        self.trade_types = config['congress']['tradeTypes']

        # Configurable target politicians (default: Pelosi)
        self.target_politicians = config.get('congress', {}).get('targetPoliticians', [
            {'name': 'Nancy Pelosi', 'chamber': 'house'}
        ])

        # Include Senate data
        self.include_senate = config.get('congress', {}).get('includeSenate', True)

        # Cache for recent trades
        self.recent_trades = []
        self.last_fetch_time = None

        logger.info("Initialized congressional trade tracker")
    
    def fetch_house_clerk_data(self):
        """Fetch data from official House Clerk disclosures (free, official source)"""
        try:
            # Get current year's financial disclosure ZIP
            year = datetime.now().year
            url = f"https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}FD.ZIP"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error(f"Failed to fetch House Clerk data: {response.status_code}")
                return []

            # Extract XML from ZIP
            with ZipFile(BytesIO(response.content)) as zf:
                xml_filename = f"{year}FD.xml"
                if xml_filename not in zf.namelist():
                    logger.error(f"XML file not found in ZIP")
                    return []
                xml_content = zf.read(xml_filename)

            # Parse XML to find Pelosi's PTR filings
            root = ET.fromstring(xml_content)
            all_trades = []

            for member in root.findall('.//Member'):
                last_name = member.find('Last')
                first_name = member.find('First')

                if last_name is None or first_name is None:
                    continue
                if not (last_name.text and 'pelosi' in last_name.text.lower()):
                    continue
                if not (first_name.text and 'nancy' in first_name.text.lower()):
                    continue

                filing_type = member.find('FilingType')
                if filing_type is None or filing_type.text != 'P':  # P = Periodic Transaction Report
                    continue

                doc_id = member.find('DocID')
                filing_date = member.find('FilingDate')
                doc_id_val = doc_id.text if doc_id is not None else ''
                filing_date_val = filing_date.text if filing_date is not None else ''

                # Build representative name
                rep_name = f"Hon. {first_name.text} {last_name.text}" if first_name is not None and last_name is not None else "Unknown"

                pdf_url = f"https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{year}/{doc_id_val}.pdf"
                logger.info(f"Found PTR: {rep_name} - {filing_date_val}")

                # Try to parse the PDF for actual trades
                pdf_trades = self._parse_ptr_pdf(pdf_url, filing_date_val, rep_name)
                if pdf_trades:
                    all_trades.extend(pdf_trades)

            logger.info(f"Found {len(all_trades)} Pelosi trades from House Clerk")
            return all_trades

        except Exception as e:
            logger.error(f"Error fetching House Clerk data: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _parse_ptr_pdf(self, pdf_url, filing_date, representative="Hon. Nancy Pelosi"):
        """Parse a PTR PDF to extract individual trades using multiple strategies"""
        if not HAS_PDFPLUMBER:
            logger.warning("pdfplumber not installed, cannot parse PDFs")
            return []

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(pdf_url, headers=headers, timeout=30)
            if response.status_code != 200:
                logger.debug(f"Failed to fetch PDF: {response.status_code}")
                return []

            trades = []
            with pdfplumber.open(BytesIO(response.content)) as pdf:
                # Strategy 1: Try table extraction first (more reliable for structured PDFs)
                table_trades = self._parse_ptr_tables(pdf, filing_date, representative, pdf_url)
                if table_trades:
                    trades.extend(table_trades)

                # Strategy 2: Fall back to text parsing if no table trades found
                if not trades:
                    text_trades = self._parse_ptr_text(pdf, filing_date, representative, pdf_url)
                    trades.extend(text_trades)

            return trades

        except Exception as e:
            logger.error(f"Error parsing PTR PDF {pdf_url}: {e}")
            return []

    def _parse_ptr_tables(self, pdf, filing_date, representative, pdf_url):
        """Extract trades from PDF tables"""
        trades = []

        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                if not table or len(table) < 2:
                    continue

                # Find header row to identify columns
                header_row = None
                for i, row in enumerate(table[:3]):  # Check first 3 rows for headers
                    row_text = ' '.join(str(cell or '').lower() for cell in row)
                    if 'asset' in row_text or 'transaction' in row_text or 'amount' in row_text:
                        header_row = i
                        break

                if header_row is None:
                    continue

                headers = [str(h or '').lower().strip() for h in table[header_row]]

                # Map column indices
                col_map = {}
                for i, h in enumerate(headers):
                    if 'asset' in h or 'description' in h:
                        col_map['asset'] = i
                    elif 'type' in h and 'transaction' not in h:
                        col_map['tx_type'] = i
                    elif 'transaction' in h and 'type' in h:
                        col_map['tx_type'] = i
                    elif 'date' in h and 'notification' not in h:
                        col_map['date'] = i
                    elif 'amount' in h:
                        col_map['amount'] = i

                # Parse data rows
                for row in table[header_row + 1:]:
                    if not row or len(row) < 3:
                        continue

                    try:
                        # Extract ticker from asset description
                        asset_idx = col_map.get('asset', 0)
                        asset_text = str(row[asset_idx] or '')
                        ticker = self._extract_ticker(asset_text)

                        if not ticker:
                            continue

                        # Get transaction type
                        tx_type = None
                        if 'tx_type' in col_map:
                            tx_text = str(row[col_map['tx_type']] or '').lower()
                            if 'p' in tx_text or 'purchase' in tx_text or 'buy' in tx_text:
                                tx_type = 'purchase'
                            elif 's' in tx_text or 'sale' in tx_text or 'sell' in tx_text:
                                tx_type = 'sale'
                        else:
                            # Try to find P or S in any cell
                            for cell in row:
                                cell_str = str(cell or '').strip().upper()
                                if cell_str == 'P':
                                    tx_type = 'purchase'
                                    break
                                elif cell_str == 'S':
                                    tx_type = 'sale'
                                    break

                        if not tx_type:
                            continue

                        # Get amount
                        amount = 0
                        amount_range = ''
                        if 'amount' in col_map:
                            amount_text = str(row[col_map['amount']] or '')
                            amount, amount_range = self._parse_amount_range(amount_text)
                        else:
                            # Search all cells for dollar amounts
                            for cell in row:
                                cell_str = str(cell or '')
                                if '$' in cell_str:
                                    amount, amount_range = self._parse_amount_range(cell_str)
                                    if amount > 0:
                                        break

                        if amount < self.min_trade_size:
                            continue

                        # Get date
                        tx_date = filing_date
                        if 'date' in col_map:
                            date_text = str(row[col_map['date']] or '')
                            parsed_date = self._extract_date(date_text)
                            if parsed_date:
                                tx_date = parsed_date

                        # Skip options unless exercised
                        if self._is_option_trade(asset_text) and 'exercise' not in asset_text.lower():
                            continue

                        if tx_type in self.trade_types:
                            trade = {
                                'transaction_date': tx_date,
                                'disclosure_date': filing_date,
                                'ticker': ticker,
                                'symbol': ticker,
                                'asset_name': asset_text[:100],
                                'transaction_type': tx_type,
                                'amount': amount,
                                'amount_range': amount_range,
                                'representative': representative,
                                'chamber': 'house',
                                'source': 'house_clerk_pdf',
                                'pdf_url': pdf_url
                            }
                            trades.append(trade)
                            logger.debug(f"Table parsed: {ticker} {tx_type} {amount_range}")

                    except Exception as e:
                        logger.debug(f"Error parsing table row: {e}")
                        continue

        return trades

    def _parse_ptr_text(self, pdf, filing_date, representative, pdf_url):
        """Extract trades from PDF text (fallback method)"""
        trades = []

        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        # Multiple splitting strategies for different PDF formats
        # Strategy A: Split on "SP " prefix (common format)
        blocks = re.split(r'\n(?:SP|JT|DC)\s+', full_text)

        # Strategy B: If no blocks found, try splitting on ticker patterns
        if len(blocks) <= 1:
            blocks = re.split(r'\n(?=[A-Z][a-z]+.*\([A-Z]{1,5}\))', full_text)

        # Strategy C: Split on common stock keywords
        if len(blocks) <= 1:
            blocks = re.split(r'\n(?=.*(?:Common Stock|Stock|Corp|Inc|LLC).*\([A-Z]{1,5}\))', full_text)

        for block in blocks:
            if len(block) < 20:
                continue

            # Extract ticker - try multiple patterns
            ticker = self._extract_ticker(block)
            if not ticker:
                continue

            # Determine transaction type with expanded patterns
            tx_type = self._extract_transaction_type(block)
            if not tx_type:
                continue

            # Find amount
            amount, amount_range = self._extract_amount_from_text(block)
            if amount < self.min_trade_size:
                continue

            # Find transaction date
            tx_date = self._extract_date(block) or filing_date

            # Skip options unless exercised
            if self._is_option_trade(block) and 'exercise' not in block.lower():
                continue

            if tx_type in self.trade_types:
                trade = {
                    'transaction_date': tx_date,
                    'disclosure_date': filing_date,
                    'ticker': ticker,
                    'symbol': ticker,
                    'asset_name': '',
                    'transaction_type': tx_type,
                    'amount': amount,
                    'amount_range': amount_range,
                    'representative': representative,
                    'chamber': 'house',
                    'source': 'house_clerk_pdf',
                    'pdf_url': pdf_url
                }
                trades.append(trade)
                logger.debug(f"Text parsed: {ticker} {tx_type} {amount_range}")

        return trades

    def _extract_ticker(self, text):
        """Extract stock ticker from text using multiple patterns"""
        # Pattern 1: Ticker in parentheses (NVDA)
        match = re.search(r'\(([A-Z]{1,5})\)', text)
        if match:
            ticker = match.group(1)
            # Exclude common non-ticker patterns
            if ticker not in ['ST', 'OP', 'JT', 'DC', 'SP', 'NA', 'LLC', 'INC', 'ETF']:
                return ticker

        # Pattern 2: Ticker after dash "- NVDA"
        match = re.search(r'-\s*([A-Z]{1,5})(?:\s|$)', text)
        if match:
            return match.group(1)

        # Pattern 3: Standalone ticker at end of line
        match = re.search(r'\s([A-Z]{2,5})$', text.split('\n')[0] if '\n' in text else text)
        if match:
            return match.group(1)

        return None

    def _extract_transaction_type(self, text):
        """Extract transaction type with expanded pattern matching"""
        text_lower = text.lower()

        # Explicit keywords
        if 'purchase' in text_lower or 'bought' in text_lower:
            return 'purchase'
        if 'sale' in text_lower or 'sold' in text_lower:
            return 'sale'

        # P/S indicators with context
        # Look for standalone P or S near dates or amounts
        if re.search(r'\s+P\s+\d{1,2}/', text):  # P followed by date
            return 'purchase'
        if re.search(r'\s+S\s+\d{1,2}/', text):  # S followed by date
            return 'sale'
        if re.search(r'\s+P\s+\$', text):  # P followed by amount
            return 'purchase'
        if re.search(r'\s+S\s+\$', text):  # S followed by amount
            return 'sale'

        # P/S in brackets or with type indicators
        if re.search(r'\[ST\]\s*P\b', text) or re.search(r'\[OP\]\s*P\b', text):
            return 'purchase'
        if re.search(r'\[ST\]\s*S\b', text) or re.search(r'\[OP\]\s*S\b', text):
            return 'sale'

        # S (partial) or S (full)
        if re.search(r'\bS\s*\(partial\)', text, re.IGNORECASE):
            return 'sale'
        if re.search(r'\bS\s*\(full\)', text, re.IGNORECASE):
            return 'sale'

        return None

    def _extract_amount_from_text(self, text):
        """Extract amount from text block"""
        # Look for dollar amount ranges: $100,001 - $250,000
        range_match = re.search(r'\$([0-9,]+)\s*-\s*\$([0-9,]+)', text)
        if range_match:
            low = float(range_match.group(1).replace(',', ''))
            high = float(range_match.group(2).replace(',', ''))
            return (low + high) / 2, f"${low:,.0f} - ${high:,.0f}"

        # Look for individual dollar amounts
        amounts = re.findall(r'\$([0-9,]+)', text)
        if len(amounts) >= 2:
            low = float(amounts[0].replace(',', ''))
            high = float(amounts[1].replace(',', ''))
            return (low + high) / 2, f"${low:,.0f} - ${high:,.0f}"
        elif len(amounts) == 1:
            amount = float(amounts[0].replace(',', ''))
            return amount, f"${amount:,.0f}"

        return 0, ''

    def _parse_amount_range(self, text):
        """Parse amount from text, handling ranges"""
        return self._extract_amount_from_text(text)

    def _extract_date(self, text):
        """Extract date from text, trying multiple formats"""
        # Pattern: MM/DD/YYYY
        match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', text)
        if match:
            return match.group(1)

        # Pattern: YYYY-MM-DD
        match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        if match:
            return match.group(1)

        # Pattern: Month DD, YYYY
        match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}', text, re.IGNORECASE)
        if match:
            return match.group(0)

        return None

    def _is_option_trade(self, text):
        """Check if this is an options trade"""
        text_lower = text.lower()
        return ('[op]' in text_lower or
                'option' in text_lower or
                'call' in text_lower or
                'put' in text_lower or
                'strike' in text_lower)

    def fetch_senate_data(self, senator_name=None):
        """Fetch Senate data directly from official Senate eFD website"""
        logger.info("Fetching Senate data from official eFD source...")
        return self._fetch_senate_direct(senator_name)

    def _fetch_senate_direct(self, senator_name=None, max_pages=3, days_back=90):
        """Scrape Senate eFD using Selenium (headless browser)"""
        if not HAS_SELENIUM:
            logger.warning("Selenium not installed - cannot scrape Senate eFD directly")
            logger.info("Install with: pip install selenium webdriver-manager")
            return []

        driver = None
        try:
            logger.info("Starting headless Chrome for Senate eFD scraping...")

            # Configure headless Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")

            # Auto-download and configure ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)

            base_url = "https://efdsearch.senate.gov"

            # Step 1: Go to home page and accept agreement
            driver.get(f"{base_url}/search/home/")
            time.sleep(2)

            # Click agreement checkbox
            try:
                checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "agree_statement"))
                )
                checkbox.click()
                time.sleep(2)
            except Exception as e:
                logger.error(f"Could not click agreement: {e}")
                return []

            # Step 2: Select "Senator" filer type, set date range, and submit search
            try:
                senator_radio = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "filerTypeLabelSenator"))
                )
                senator_radio.click()

                # Optionally filter by name
                if senator_name:
                    last_name_input = driver.find_element(By.ID, "lastName")
                    last_name_input.clear()
                    last_name_input.send_keys(senator_name)

                # Set date range to recent filings only
                start_date = (datetime.now() - timedelta(days=days_back)).strftime('%m/%d/%Y')
                end_date = datetime.now().strftime('%m/%d/%Y')

                try:
                    start_input = driver.find_element(By.ID, "fromDate")
                    start_input.clear()
                    start_input.send_keys(start_date)

                    end_input = driver.find_element(By.ID, "toDate")
                    end_input.clear()
                    end_input.send_keys(end_date)
                except:
                    logger.debug("Date fields not found, using defaults")

                # Submit search
                submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'].btn-primary")
                submit_btn.click()
                time.sleep(3)
            except Exception as e:
                logger.error(f"Could not submit search: {e}")
                return []

            # Step 3: Parse results table
            trades = []
            pages_processed = 0
            try:
                # Wait for results table
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, "filedReports"))
                )

                # Get rows, limited to max_pages
                while pages_processed < max_pages:
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    table = soup.find('table', {'id': 'filedReports'})

                    if table:
                        rows = table.find('tbody').find_all('tr') if table.find('tbody') else []

                        for row in rows:
                            cells = row.find_all('td')
                            if len(cells) < 5:
                                continue

                            first_name = cells[0].get_text().strip()
                            last_name = cells[1].get_text().strip()
                            full_name = f"{first_name} {last_name}"

                            # Get report link
                            report_cell = cells[3]
                            report_link = report_cell.find('a')
                            if not report_link:
                                continue

                            report_title = report_link.get_text().strip()

                            # Only process PTR reports
                            if 'periodic' not in report_title.lower():
                                continue

                            report_href = report_link.get('href', '')
                            report_url = urljoin(base_url, report_href)
                            filing_date = cells[4].get_text().strip()

                            logger.info(f"Found Senate PTR: {full_name} - {filing_date}")

                            # Fetch and parse the individual report
                            report_trades = self._fetch_senate_report_selenium(driver, report_url, full_name, filing_date)
                            trades.extend(report_trades)

                            # Rate limit between reports
                            time.sleep(1)

                    pages_processed += 1

                    # Check for next page (if under max_pages limit)
                    if pages_processed >= max_pages:
                        logger.info(f"Reached max pages limit ({max_pages})")
                        break

                    try:
                        next_btn = driver.find_element(By.CSS_SELECTOR, ".paginate_button.next:not(.disabled)")
                        if next_btn:
                            next_btn.click()
                            time.sleep(2)
                        else:
                            break
                    except:
                        break  # No more pages

            except Exception as e:
                logger.error(f"Error parsing Senate results: {e}")

            logger.info(f"Found {len(trades)} Senate trades via direct scraping")
            return trades

        except Exception as e:
            logger.error(f"Error in Senate Selenium scraping: {e}")
            import traceback
            traceback.print_exc()
            return []

        finally:
            if driver:
                driver.quit()

    def _fetch_senate_report_selenium(self, driver, report_url, senator_name, filing_date):
        """Fetch and parse a single Senate PTR report"""
        trades = []

        try:
            # Open report in new tab
            driver.execute_script(f"window.open('{report_url}', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find transaction tables
            tables = soup.find_all('table')

            for table in tables:
                # Look for transaction-related headers
                header_row = table.find('tr')
                if not header_row:
                    continue

                header_text = header_row.get_text().lower()
                if 'transaction' not in header_text and 'asset' not in header_text:
                    continue

                rows = table.find_all('tr')[1:]  # Skip header

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) < 4:
                        continue

                    try:
                        cell_texts = [c.get_text().strip() for c in cells]

                        # Extract ticker
                        ticker = None
                        asset_name = ''
                        for i, text in enumerate(cell_texts):
                            ticker_match = re.search(r'\(([A-Z]{1,5})\)', text)
                            if ticker_match:
                                ticker = ticker_match.group(1)
                                asset_name = text
                                break

                        if not ticker:
                            continue

                        # Determine transaction type
                        tx_type = None
                        for text in cell_texts:
                            text_lower = text.lower()
                            if 'purchase' in text_lower:
                                tx_type = 'purchase'
                                break
                            elif 'sale' in text_lower:
                                tx_type = 'sale'
                                break

                        if not tx_type:
                            continue

                        # Find amount
                        amount = 0
                        amount_range = ''
                        for text in cell_texts:
                            if '$' in text:
                                amount_range = text
                                amount = self._parse_amount(text)
                                if amount > 0:
                                    break

                        # Find transaction date
                        tx_date = filing_date
                        for text in cell_texts:
                            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', text)
                            if date_match:
                                tx_date = date_match.group(1)
                                break

                        if tx_type in self.trade_types and amount >= self.min_trade_size:
                            trade = {
                                'transaction_date': tx_date,
                                'disclosure_date': filing_date,
                                'ticker': ticker,
                                'symbol': ticker,
                                'asset_name': asset_name,
                                'transaction_type': tx_type,
                                'amount': amount,
                                'amount_range': amount_range,
                                'representative': f"Sen. {senator_name}",
                                'chamber': 'senate',
                                'source': 'senate_efd',
                                'report_url': report_url
                            }
                            trades.append(trade)
                            logger.debug(f"Parsed Senate trade: {ticker} {tx_type} {amount_range}")

                    except Exception as e:
                        logger.debug(f"Error parsing Senate row: {e}")
                        continue

            # Close tab and switch back
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            logger.error(f"Error fetching Senate report: {e}")
            # Make sure we're back on main window
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

        return trades

    def _parse_senate_json_results(self, session, base_url, headers, data, target_name=None):
        """Parse JSON response from Senate eFD AJAX endpoint"""
        trades = []

        try:
            records = data.get('data', [])
            logger.info(f"Found {len(records)} Senate PTR filings")

            for record in records:
                # record format: [first_name, last_name, office, report_type, date, link_html]
                if len(record) < 6:
                    continue

                first_name = record[0]
                last_name = record[1]
                full_name = f"{first_name} {last_name}"

                # Filter by name if specified
                if target_name and target_name.lower() not in full_name.lower():
                    continue

                # Extract report link from HTML
                link_html = record[5] if len(record) > 5 else ''
                link_match = re.search(r'href="([^"]+)"', str(link_html))
                if not link_match:
                    continue

                report_url = urljoin(base_url, link_match.group(1))
                filing_date = record[4] if len(record) > 4 else ''

                logger.info(f"Found Senate PTR: {full_name} - {filing_date}")

                # Fetch and parse the report
                report_trades = self._parse_senate_ptr_report(session, report_url, headers, full_name, filing_date)
                trades.extend(report_trades)

                # Rate limit
                time.sleep(0.5)

        except Exception as e:
            logger.error(f"Error parsing Senate JSON results: {e}")

        return trades

    def _parse_senate_html_results(self, session, base_url, headers, target_name=None):
        """Parse HTML results from Senate eFD search page"""
        trades = []

        try:
            # Get the search results page
            search_url = f"{base_url}/search/"
            response = session.get(search_url, headers=headers, timeout=30)

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find results table
            table = soup.find('table', {'id': 'filedReports'})
            if not table:
                logger.warning("Could not find Senate results table")
                return []

            rows = table.find_all('tr')[1:]  # Skip header

            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue

                first_name = cells[0].get_text().strip()
                last_name = cells[1].get_text().strip()
                full_name = f"{first_name} {last_name}"

                # Filter by name if specified
                if target_name and target_name.lower() not in full_name.lower():
                    continue

                # Get report link
                report_link = cells[3].find('a')
                if not report_link:
                    continue

                report_url = urljoin(base_url, report_link['href'])
                filing_date = cells[4].get_text().strip()

                logger.info(f"Found Senate PTR: {full_name} - {filing_date}")

                # Fetch and parse the report
                report_trades = self._parse_senate_ptr_report(session, report_url, headers, full_name, filing_date)
                trades.extend(report_trades)

                # Rate limit
                time.sleep(0.5)

        except Exception as e:
            logger.error(f"Error parsing Senate HTML results: {e}")

        return trades

    def _parse_senate_ptr_report(self, session, report_url, headers, senator_name, filing_date):
        """Parse an individual Senate PTR report page"""
        trades = []

        try:
            response = session.get(report_url, headers=headers, timeout=30)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find transactions table - Senate PTRs have a specific format
            # Look for tables with transaction data
            tables = soup.find_all('table')

            for table in tables:
                # Check if this looks like a transactions table
                headers_row = table.find('tr')
                if not headers_row:
                    continue

                header_text = headers_row.get_text().lower()
                if 'transaction' not in header_text and 'asset' not in header_text:
                    continue

                rows = table.find_all('tr')[1:]  # Skip header

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) < 4:
                        continue

                    try:
                        # Senate PTR format varies, but typically includes:
                        # Transaction Date, Owner, Ticker/Asset, Type, Amount
                        cell_texts = [c.get_text().strip() for c in cells]

                        # Try to extract ticker - look for stock symbols
                        ticker = None
                        asset_name = ''
                        for text in cell_texts:
                            # Match ticker patterns like (AAPL) or AAPL
                            ticker_match = re.search(r'\(([A-Z]{1,5})\)|^([A-Z]{1,5})$', text)
                            if ticker_match:
                                ticker = ticker_match.group(1) or ticker_match.group(2)
                                break
                            # Also check for "Stock" or "Common Stock" indicators
                            if 'stock' in text.lower() and not ticker:
                                asset_name = text

                        if not ticker:
                            continue

                        # Determine transaction type
                        tx_type = None
                        for text in cell_texts:
                            text_lower = text.lower()
                            if 'purchase' in text_lower or text_lower == 'p':
                                tx_type = 'purchase'
                                break
                            elif 'sale' in text_lower or text_lower == 's':
                                tx_type = 'sale'
                                break

                        if not tx_type:
                            continue

                        # Find amount
                        amount = 0
                        amount_range = ''
                        for text in cell_texts:
                            if '$' in text:
                                amount_range = text
                                amount = self._parse_amount(text)
                                if amount > 0:
                                    break

                        # Find transaction date
                        tx_date = filing_date
                        for text in cell_texts:
                            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', text)
                            if date_match:
                                tx_date = date_match.group(1)
                                break

                        # Only include if meets criteria
                        if tx_type in self.trade_types and amount >= self.min_trade_size:
                            trade = {
                                'transaction_date': tx_date,
                                'disclosure_date': filing_date,
                                'ticker': ticker,
                                'symbol': ticker,
                                'asset_name': asset_name,
                                'transaction_type': tx_type,
                                'amount': amount,
                                'amount_range': amount_range,
                                'representative': f"Sen. {senator_name}",
                                'chamber': 'senate',
                                'source': 'senate_efd',
                                'report_url': report_url
                            }
                            trades.append(trade)
                            logger.debug(f"Parsed Senate trade: {ticker} {tx_type} {amount_range}")

                    except Exception as e:
                        logger.debug(f"Error parsing Senate row: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error parsing Senate PTR report: {e}")

        return trades

    def fetch_mock_data(self):
        """Mock data for testing - replace with real data source in production"""
        # Sample Pelosi trades based on historical public disclosures
        # In production, replace this with a real data subscription
        mock_trades = [
            {
                'transaction_date': '2025-12-15',
                'disclosure_date': '2025-12-20',
                'ticker': 'NVDA',
                'symbol': 'NVDA',
                'asset_name': 'NVIDIA Corporation',
                'transaction_type': 'purchase',
                'amount': 500000,
                'amount_range': '$250,001 - $500,000',
                'representative': 'Hon. Nancy Pelosi',
                'source': 'mock'
            },
            {
                'transaction_date': '2025-11-20',
                'disclosure_date': '2025-11-25',
                'ticker': 'GOOGL',
                'symbol': 'GOOGL',
                'asset_name': 'Alphabet Inc Class A',
                'transaction_type': 'purchase',
                'amount': 250000,
                'amount_range': '$100,001 - $250,000',
                'representative': 'Hon. Nancy Pelosi',
                'source': 'mock'
            },
            {
                'transaction_date': '2025-10-05',
                'disclosure_date': '2025-10-10',
                'ticker': 'AAPL',
                'symbol': 'AAPL',
                'asset_name': 'Apple Inc',
                'transaction_type': 'sale',
                'amount': 1000000,
                'amount_range': '$500,001 - $1,000,000',
                'representative': 'Hon. Nancy Pelosi',
                'source': 'mock'
            },
            {
                'transaction_date': '2025-09-12',
                'disclosure_date': '2025-09-17',
                'ticker': 'MSFT',
                'symbol': 'MSFT',
                'asset_name': 'Microsoft Corporation',
                'transaction_type': 'purchase',
                'amount': 500000,
                'amount_range': '$250,001 - $500,000',
                'representative': 'Hon. Nancy Pelosi',
                'source': 'mock'
            },
            {
                'transaction_date': '2025-08-22',
                'disclosure_date': '2025-08-27',
                'ticker': 'TSLA',
                'symbol': 'TSLA',
                'asset_name': 'Tesla Inc',
                'transaction_type': 'purchase',
                'amount': 250000,
                'amount_range': '$100,001 - $250,000',
                'representative': 'Hon. Nancy Pelosi',
                'source': 'mock'
            }
        ]

        # Filter by trade type and minimum size
        trades = []
        for trade in mock_trades:
            if (trade['transaction_type'] in self.trade_types and
                trade['amount'] >= self.min_trade_size):
                trades.append(trade)

        logger.info(f"Loaded {len(trades)} mock Pelosi trades for testing")
        logger.warning("Using MOCK DATA - configure a real data source for production!")
        return trades

    def _parse_amount(self, amount_str):
        """Parse amount string like '$1,000,000 - $5,000,000' or '$50,000'"""
        try:
            # Remove currency symbols and whitespace
            amount_str = amount_str.replace('$', '').replace(',', '').strip()
            
            # Handle ranges (take the midpoint)
            if '-' in amount_str:
                parts = amount_str.split('-')
                low = float(parts[0].strip())
                high = float(parts[1].strip())
                return (low + high) / 2
            else:
                return float(amount_str)
        except ValueError:
            logger.warning(f"Could not parse amount: {amount_str}")
            return 0
    
    def get_recent_trades(self, days=30):
        """Get recent trades within specified days"""
        try:
            # Try multiple data sources
            all_trades = []

            # Try data sources in order of reliability
            if self.data_source == 'mock':
                trades = self.fetch_mock_data()
                all_trades.extend(trades)

            # Load manually added trades first
            if self.data_source in ['manual', 'auto']:
                manual_trades = self.load_trades_from_file('pelosi_trades.json')
                all_trades.extend(manual_trades)

            # Official House Clerk data (free, shows new filings)
            if self.data_source in ['house_clerk', 'official', 'auto']:
                trades = self.fetch_house_clerk_data()
                all_trades.extend(trades)

            # Official Senate eFD data (free, official source)
            if self.data_source in ['senate_efd', 'official', 'auto'] or self.include_senate:
                logger.info("Fetching Senate eFD data...")
                senate_trades = self.fetch_senate_data()
                all_trades.extend(senate_trades)
                logger.info(f"Added {len(senate_trades)} trades from Senate eFD")

            # Fallback to mock data if no real data available (for testing)
            if not all_trades and self.data_source == 'mock':
                logger.warning("Using mock data for testing")
                trades = self.fetch_mock_data()
                all_trades.extend(trades)
            
            # Filter by date (if date parsing works)
            recent_trades = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for trade in all_trades:
                try:
                    # Try to parse date
                    trade_date = self._parse_date(trade['transaction_date'])
                    if trade_date >= cutoff_date:
                        trade['parsed_date'] = trade_date
                        recent_trades.append(trade)
                except (ValueError, KeyError):
                    # If date parsing fails, include anyway
                    recent_trades.append(trade)
            
            # Remove duplicates (same ticker, similar date, same type)
            unique_trades = self._deduplicate_trades(recent_trades)
            
            self.recent_trades = unique_trades
            self.last_fetch_time = datetime.now()
            
            logger.info(f"Total unique recent trades: {len(unique_trades)}")
            return unique_trades
            
        except Exception as e:
            logger.error(f"Error getting recent trades: {e}")
            return []
    
    def _parse_date(self, date_str):
        """Parse various date formats"""
        if not date_str:
            return datetime.now()

        # Clean the string
        date_str = str(date_str).strip()

        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m/%d/%y',
            '%Y/%m/%d',
            '%b %d, %Y',
            '%b %d %Y',
            '%B %d, %Y',
            '%B %d %Y',
            '%d-%b-%Y',
            '%d-%B-%Y',
            '%d %b %Y',
            '%d %B %Y',
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # Try to extract date components with regex
        # Handle "January 15, 2024" or "Jan 15 2024"
        month_match = re.search(
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})',
            date_str, re.IGNORECASE
        )
        if month_match:
            month_str = month_match.group(1)[:3]
            day = int(month_match.group(2))
            year = int(month_match.group(3))
            try:
                return datetime.strptime(f"{month_str} {day} {year}", '%b %d %Y')
            except ValueError:
                pass

        # Handle MM/DD/YY or M/D/YY
        short_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2})(?!\d)', date_str)
        if short_match:
            month = int(short_match.group(1))
            day = int(short_match.group(2))
            year = int(short_match.group(3))
            year = year + 2000 if year < 50 else year + 1900
            try:
                return datetime(year, month, day)
            except ValueError:
                pass

        # If all fail, return current date
        logger.warning(f"Could not parse date: {date_str}")
        return datetime.now()
    
    def _deduplicate_trades(self, trades):
        """Remove duplicate trades"""
        unique_trades = []
        seen_keys = set()
        
        for trade in trades:
            # Create a unique key
            key = f"{trade.get('ticker', '')}_{trade.get('transaction_date', '')}_{trade.get('transaction_type', '')}"
            
            if key not in seen_keys:
                seen_keys.add(key)
                unique_trades.append(trade)
        
        return unique_trades
    
    def get_trades_since(self, last_check_date):
        """Get trades since last check date"""
        all_trades = self.get_recent_trades(days=90)  # Get 90 days to be safe
        
        new_trades = []
        for trade in all_trades:
            trade_date = trade.get('parsed_date')
            if trade_date and trade_date > last_check_date:
                new_trades.append(trade)
        
        return new_trades
    
    def save_trades_to_file(self, trades, filename='pelosi_trades.json'):
        """Save trades to JSON file for analysis"""
        try:
            # Convert dates to strings for JSON serialization
            serializable_trades = []
            for trade in trades:
                trade_copy = trade.copy()
                if 'parsed_date' in trade_copy:
                    trade_copy['parsed_date'] = trade_copy['parsed_date'].isoformat()
                serializable_trades.append(trade_copy)
            
            with open(filename, 'w') as f:
                json.dump(serializable_trades, f, indent=2)
            
            logger.info(f"Saved {len(trades)} trades to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving trades to file: {e}")
            return False
    
    def load_trades_from_file(self, filename='pelosi_trades.json'):
        """Load trades from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Convert date strings back to datetime objects
            for trade in data:
                if 'parsed_date' in trade and trade['parsed_date']:
                    trade['parsed_date'] = datetime.fromisoformat(trade['parsed_date'])
            
            logger.info(f"Loaded {len(data)} trades from {filename}")
            return data
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load trades from file: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading trades from file: {e}")
            return []