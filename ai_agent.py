import email
import base64
import quopri
from bs4 import BeautifulSoup
import re
from urllib.parse import unquote
import json
import pandas as pd
from datetime import datetime
import os
from typing import List, Dict, Any, Optional
import logging
import openai
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInDataExtractor:
    """AI-powered LinkedIn data extraction agent with support for ChatGPT and Gemini"""
    
    def __init__(self, openai_api_key: str = None, gemini_api_key: str = None, ai_model: str = "chatgpt"):
        """Initialize the AI-enhanced LinkedIn parser
        
        Args:
            openai_api_key: OpenAI API key for ChatGPT
            gemini_api_key: Google API key for Gemini
            ai_model: Which AI model to use ("chatgpt" or "gemini")
        """
        self.ai_model = ai_model.lower()
        self.openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.gemini_client = None
        
        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                self.gemini_client = genai.GenerativeModel('gemini-2.5-flash-lite')
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.gemini_client = None
        
        self.extracted_data = []
        self.analysis_results = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def read_mhtml_file(self, file_path: str):
        """Read an MHTML file and return the parsed email message object."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return email.message_from_file(f)
        except Exception as e:
            logger.error(f"Error reading MHTML file: {e}")
            raise

    def remove_quoted_printable_emojis_regex(self, text):
        """
        Method 1: Remove quoted-printable encoded emojis using regex patterns
        This targets common emoji byte sequences in quoted-printable format
        """
        # Pattern for quoted-printable encoded bytes (=XX format)
        # Common emoji patterns start with =F0=9F (UTF-8 emoji range)
        emoji_patterns = [
            r'=F0=9F[\=A-F0-9]{6,12}',  # Most emojis start with F0 9F
            r'=E2[\=A-F0-9]{3,9}',      # Some symbols/emojis start with E2
            r'=E2=9C=85',               # Checkmark ✅
            r'=F0=9F=95=92',            # Clock 🕒
            r'=F0=9F=93=A7',            # Email 📧
            r'=F0=9F=9A=80',            # Rocket 🚀
            r'=F0=9F=94=96',            # Bell 🔖
        ]
        
        for pattern in emoji_patterns:
            text = re.sub(pattern, '', text)
        
        return text

    def extract_html_content(self, mhtml_message):
        """Extract HTML content from MHTML message parts."""
        html_content = ""
        
        if mhtml_message.is_multipart():
            for part in mhtml_message.walk():
                content_type = part.get_content_type()
                
                if content_type == 'text/html':
                    payload = part.get_payload(decode=True)
                    if payload:
                        try:
                            try:
                                html_content = payload.decode('utf-8')
                            except UnicodeDecodeError:
                                html_content = payload.decode('latin-1')
                            break
                        except Exception as e:
                            logger.warning(f"Error decoding HTML content: {e}")
                            continue
        else:
            if mhtml_message.get_content_type() == 'text/html':
                payload = mhtml_message.get_payload(decode=True)
                if payload:
                    try:
                        html_content = payload.decode('utf-8')
                    except UnicodeDecodeError:
                        html_content = payload.decode('latin-1')
#        if html_content:
#            html_content = self.remove_quoted_printable_emojis_regex(html_content)
        return html_content
    
    def extract_linkedin_data(self, raw_html: str) -> List[Dict[str, str]]:
        """Extract LinkedIn data with enhanced parsing."""
        soup = BeautifulSoup(raw_html, 'html.parser')
        data_list = []
        
        # Find all the main post containers
        post_containers = soup.find_all('div', class_='feed-shared-update-v2')
        
        if not post_containers:
            logger.warning("No LinkedIn post containers found. Trying alternative selectors...")
            # Try alternative selectors for different LinkedIn formats
            post_containers = soup.find_all('div', class_='feed-shared-update-v2__description')
            if not post_containers:
                post_containers = soup.find_all('div', class_='feed-shared-text')
        
        logger.info(f"Found {len(post_containers)} post containers")
        
        # Debug: Log the first few containers to see what we're working with
        if post_containers:
            logger.info(f"First container classes: {post_containers[0].get('class', 'No class')}")
            logger.info(f"First container text preview: {str(post_containers[0])[:200]}...")
        
        for i, post in enumerate(post_containers):
            try:
                # Extract Name with multiple fallback strategies
                name = self._extract_name(post)
                
                # Extract Title with multiple fallback strategies
                title = self._extract_title(post)
                
                # Extract Period with multiple fallback strategies
                period = self._extract_period(post)
                
                # Extract Details with multiple fallback strategies
                details = self._extract_details(post)
                
                # Only add if we have meaningful data
                if name and name != 'N/A' and name.strip():
                    data_list.append({
                        'Name': name.strip(),
                        'Title': title.strip() if title else 'N/A',
                        'Period': period.strip() if period else 'N/A',
                        'Details': details.strip() if details else 'N/A',
                        'Post_Index': i + 1
                    })
                    
            except Exception as e:
                logger.warning(f"Error processing post {i+1}: {e}")
                continue
                
        return data_list
    
    def extract_linkedin_data_ai(self, raw_html: str) -> List[Dict[str, str]]:
        """AI-powered extraction for complex or non-standard formats using ChatGPT or Gemini"""
        if self.ai_model == "chatgpt":
            return self._extract_with_chatgpt(raw_html)
        elif self.ai_model == "gemini":
            return self._extract_with_gemini(raw_html)
        else:
            self.logger.warning(f"Unknown AI model: {self.ai_model}. Falling back to traditional extraction.")
            return []
    
    def _extract_with_chatgpt(self, raw_html: str) -> List[Dict[str, str]]:
        """Extract data using OpenAI ChatGPT"""
        if not self.openai_client:
            self.logger.warning("OpenAI client not initialized. Falling back to traditional extraction.")
            return []
        
        # Clean and truncate HTML for AI processing
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # Remove scripts, styles, and other irrelevant content
        for script in soup(["script", "style", "meta", "link"]):
            script.decompose()
        
        # Extract text content and limit size for API
        clean_text = soup.get_text(separator='\n', strip=True)
        
        # Truncate if too long (AI APIs have token limits)
        if len(clean_text) > 10000:
            clean_text = clean_text[:10000] + "..."
        
        prompt = f"""
        Extract LinkedIn post information from the following HTML content. 
        For each post, identify:
        - Name: The person's name who made the post
        - Title: Their job title or professional description
        - Period: Time period mentioned (like "2w", "1mo", etc.)
        - Details: The main content/text of their post
        - Location: The expected location of the role and if in office is required
        - Company: Name of the company
        
        Return the data as a JSON array with objects containing these fields.
        If you can't find specific information, use "N/A" as the value.
        
        HTML Content:
        {clean_text}
        """
        
        try:
            logger.info(f"Calling OpenAI API with {len(clean_text)} characters of text")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured data from LinkedIn posts. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1,
                max_tokens=2000
            )
            
            ai_data = json.loads(response.choices[0].message.content)
            logger.info(f"OpenAI returned {len(ai_data)} data items")
            
            # Add metadata
            for item in ai_data:
                item['extraction_method'] = 'ai_chatgpt'
                item['confidence'] = 0.9
            
            return ai_data
            
        except Exception as e:
            self.logger.error(f"ChatGPT extraction failed: {e}")
            return []
    
    def _extract_with_gemini(self, raw_html: str) -> List[Dict[str, str]]:
        """Extract data using Google Gemini"""
        if not self.gemini_client:
            self.logger.warning("Gemini client not initialized. Falling back to traditional extraction.")
            return []
        
        # Clean and truncate HTML for AI processing
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # Remove scripts, styles, and other irrelevant content
        for script in soup(["script", "style", "meta", "link"]):
            script.decompose()
        
        # Extract text content and limit size for API
        clean_text = soup.get_text(separator='\n', strip=True)
        
        # Truncate if too long (Gemini has token limits)
        if len(clean_text) > 10000:
            clean_text = clean_text[:10000] + "..."
        
        prompt = f"""
        Extract LinkedIn post information from the following HTML content. 
        For each post, identify:
        - Name: The person's name who made the post
        - Title: Their job title or professional description
        - Period: Time period mentioned (like "2w", "1mo", etc.)
        - Details: The main content/text of their post
        - Location: The expected location of the role and if in office is required
        - Company: Name of the company
        
        Return the data as a JSON array with objects containing these fields.
        If you can't find specific information, use "N/A" as the value.
        
        HTML Content:
        {clean_text}
        """
        
        try:
            logger.info(f"Calling Gemini API with {len(clean_text)} characters of text")
            response = self.gemini_client.generate_content(prompt)
            
            # Parse the response content
            response_text = response.text
            
            # Try to extract JSON from the response
            try:
                # Look for JSON content in the response
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                
                if json_start != -1 and json_end != 0:
                    json_content = response_text[json_start:json_end]
                    ai_data = json.loads(json_content)
                else:
                    # If no JSON array found, try to parse the entire response
                    ai_data = json.loads(response_text)
                
                logger.info(f"Gemini returned {len(ai_data)} data items")
                
                # Add metadata
                for item in ai_data:
                    item['extraction_method'] = 'ai_gemini'
                    item['confidence'] = 0.9
                
                return ai_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Response content: {response_text}")
                return []
            
        except Exception as e:
            self.logger.error(f"Gemini extraction failed: {e}")
            return []

    
    def _extract_name(self, post) -> str:
        """Extract name with multiple fallback strategies."""
        # Primary method
        name_element = post.find('span', {'aria-hidden': 'true'})
        if name_element:
            name = name_element.get_text(' ', strip=True)
            if name and len(name) > 1:
                return name
        
        # Fallback methods
        name_selectors = [
            'span[class*="actor"]',
            'span[class*="name"]',
            'a[class*="actor"]',
            'div[class*="actor"]'
        ]
        
        for selector in name_selectors:
            try:
                element = post.select_one(selector)
                if element:
                    name = element.get_text(' ', strip=True)
                    if name and len(name) > 1 and not name.isdigit():
                        return name
            except:
                continue
        
        return 'N/A'
    
    def _extract_title(self, post) -> str:
        """Extract title with multiple fallback strategies."""
        # Primary method
        title_element = post.find('span', class_='update-components-actor__description')
        if title_element:
            title = title_element.get_text(' ', strip=True)
            if title and len(title) > 1:
                return title
        
        # Fallback methods
        title_selectors = [
            'span[class*="description"]',
            'div[class*="description"]',
            'span[class*="title"]',
            'div[class*="title"]'
        ]
        
        for selector in title_selectors:
            try:
                element = post.select_one(selector)
                if element:
                    title = element.get_text(' ', strip=True)
                    if title and len(title) > 1:
                        return title
            except:
                continue
        
        return 'No title found'
    
    def _extract_period(self, post) -> str:
        """Extract period with multiple fallback strategies."""
        # Primary method
        period_element = post.find('span', class_='update-components-actor__sub-description')
        if period_element:
            period_span = period_element.find('span', {'aria-hidden': 'true'})
            if period_span:
                period = period_span.get_text(' ', strip=True)
                if period and len(period) > 1:
                    return period
        
        # Fallback methods
        period_selectors = [
            'span[class*="time"]',
            'span[class*="date"]',
            'time',
            'span[class*="sub-description"]'
        ]
        
        for selector in period_selectors:
            try:
                element = post.select_one(selector)
                if element:
                    period = element.get_text(' ', strip=True)
                    if period and len(period) > 1:
                        return period
            except:
                continue
        
        return 'N/A'
    
    def _extract_details(self, post) -> str:
        """Extract details with multiple fallback strategies."""
        # Primary method
        details_element = post.find('div', class_='feed-shared-inline-show-more-text')
        if details_element:
            details = details_element.get_text(' ', strip=True)
            if details and len(details) > 1:
                return details
        
        # Fallback methods
        detail_selectors = [
            'div[class*="text"]',
            'div[class*="content"]',
            'div[class*="body"]',
            'p',
            'span[class*="text"]'
        ]
        
        for selector in detail_selectors:
            try:
                elements = post.select(selector)
                for element in elements:
                    details = element.get_text(' ', strip=True)
                    if details and len(details) > 10:  # More substantial content
                        return details
            except:
                continue
        
        return 'N/A'
    
    def analyze_data(self, data_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """AI-powered analysis of the extracted data."""
        if not data_list:
            return {"error": "No data to analyze"}
        
        analysis = {
            "total_posts": len(data_list),
            "unique_names": len(set(item['Name'] for item in data_list)),
            "extraction_timestamp": datetime.now().isoformat(),
            "data_quality_score": 0,
            "insights": [],
            "recommendations": []
        }
        
        # Calculate data quality score
        quality_metrics = {
            "names_complete": sum(1 for item in data_list if item['Name'] != 'N/A'),
            "titles_complete": sum(1 for item in data_list if item['Title'] != 'N/A'),
            "periods_complete": sum(1 for item in data_list if item['Period'] != 'N/A'),
            "details_complete": sum(1 for item in data_list if item['Details'] != 'N/A')
        }
        
        total_fields = len(data_list) * 4
        complete_fields = sum(quality_metrics.values())
        analysis["data_quality_score"] = round((complete_fields / total_fields) * 100, 2)
        
        # Generate insights
        if analysis["data_quality_score"] > 80:
            analysis["insights"].append("High quality data extraction - most fields were successfully parsed")
        elif analysis["data_quality_score"] > 60:
            analysis["insights"].append("Moderate quality data extraction - some fields may need manual review")
        else:
            analysis["insights"].append("Low quality data extraction - manual review recommended")
        
        # Analyze patterns
        if len(data_list) > 1:
            # Check for common patterns in titles
            titles = [item['Title'] for item in data_list if item['Title'] != 'N/A']
            if titles:
                common_words = self._find_common_words(titles)
                if common_words:
                    analysis["insights"].append(f"Common keywords in titles: {', '.join(common_words[:5])}")
        
        # Generate recommendations
        if analysis["data_quality_score"] < 80:
            analysis["recommendations"].append("Consider reviewing the MHTML file format - it may be from a different LinkedIn version")
        
        if len(data_list) == 0:
            analysis["recommendations"].append("No data extracted - check if the MHTML file contains LinkedIn content")
        
        return analysis
    
    def _find_common_words(self, text_list: List[str], min_length: int = 4) -> List[str]:
        """Find common words in a list of text strings."""
        word_count = {}
        for text in text_list:
            words = re.findall(r'\b\w+\b', text.lower())
            for word in words:
                if len(word) >= min_length:
                    word_count[word] = word_count.get(word, 0) + 1
        
        # Return top 10 most common words
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:10] if count > 1]
    
    def get_formatted_output(self, data_list: List[Dict[str, str]], max_width: int = 100) -> str:
        """Generate formatted table output for display."""
        if not data_list:
            return "No data to display"
        
        # Ensure all required columns exist
        columns = ['Name', 'Title', 'Period', 'Details', 'Company', 'Location']
        
        # Calculate column widths
        col_widths = {}
        for col in columns:
            max_len = max(len(str(item.get(col, ''))) for item in data_list)
            col_widths[col] = min(max_len + 2, 30 if col in ['Name', 'Period', 'Location'] else 40 if col == 'Company' else 60)
        
        # Create header
        header_parts = []
        for col in columns:
            header_parts.append(f"{col:<{col_widths[col]}}")
        header = " | ".join(header_parts)
        separator = "-" * len(header)
        
        # Create rows
        rows = []
        for entry in data_list:
            row_parts = []
            for col in columns:
                value = str(entry.get(col, ''))[:col_widths[col]-2]
                row_parts.append(f"{value:<{col_widths[col]}}")
            row = " | ".join(row_parts)
            rows.append(row)
        
        return "\n".join([header, separator] + rows)

    def enhance_data_with_ai(self, traditional_data: List[Dict[str, str]], ai_model: str = "chatgpt") -> List[Dict[str, str]]:
        """Enhance traditional parsing results with AI to add company name and location/remote information."""
        if ai_model == "chatgpt":
            return self._enhance_with_chatgpt(traditional_data)
        elif ai_model == "gemini":
            return self._enhance_with_gemini(traditional_data)
        else:
            self.logger.warning(f"Unknown AI model: {ai_model}. Skipping AI enhancement.")
            return traditional_data
    
    def _enhance_with_chatgpt(self, traditional_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Enhance data using OpenAI ChatGPT"""
        if not self.openai_client:
            self.logger.warning("OpenAI client not initialized. Skipping AI enhancement.")
            return None
        
        try:
            # Convert traditional data to CSV format for AI processing
            # Limit to first 50 records to avoid truncation issues
#            max_records = min(50, len(traditional_data))
#            data_for_ai = traditional_data[:max_records]            
#            if len(traditional_data) > max_records:
#                logger.info(f"Limiting AI enhancement to first {max_records} records to avoid truncation (total: {len(traditional_data)})")
            
            # Convert to CSV format
            csv_input = self._convert_to_csv_input(traditional_data)
            
            # Create prompt for AI enhancement
            prompt = f"""
            You are an expert at analying job postings. First, let me clarify the steps before providing you with the data.
            
                1. After receiving the CSV formatted data, covert them into a table  Add 3 columns - an unique ID for each row, "Company" and "Location".
                2. For each row in the "Company" column, derive the company name from data in either "Name" or "Title" columns only.  Do not use Detais.If you can't find anything, write "N/A".
                3. For each row in the "Location" column, derive the location from the data in the "Details" column:
                 3a) If the job is likely remote, write "Remote";
                   else If not remote, write the specific location (city, state, country) and make sure to double quote the entire string.
                   If you are not sure, write "Location not specified";

            Here is the input data in CSV format:
            {csv_input}
            
            Before returning the data:
            - The rows must be in the same order as the original data. You can use "Name" as reference.
            - Remove column "Title", "Details" and keep only "Name", "Company", "Location", the unique ID column.
            After completing all these, the # of rows should be the same as the original data.  It shoudl be 71.  If not the same, please explain why and which are missing or added.  And how you can make the # of rows the same.
            
            Then return all rows with the headers in CSV format.
            """
            
#            logger.info(f"Calling OpenAI API to enhance {len(data_for_ai)} records (limited from {len(traditional_data)} total)")
            logger.info(f"Calling OpenAI API to enhance records (limited from {len(traditional_data)} total)")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing LinkedIn job postings and extracting structured data. Return valid CSV format only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            response_content = response.choices[0].message.content
            logger.info(f"OpenAI response content length: {len(response_content)} characters")
            
            # Parse CSV response
            enhanced_data = self._parse_csv_response(response_content)
            if enhanced_data:
                logger.info(f"Successfully parsed OpenAI CSV response with {len(enhanced_data)} records")
                # Merge AI enhanced data with original data
                merged_data = self._merge_ai_enhancement_with_original(traditional_data, enhanced_data)
                return self._add_metadata(merged_data, 'traditional+ai_chatgpt')
            else:
                logger.error("Failed to parse OpenAI CSV response")
                return None
            
        except Exception as e:
            self.logger.error(f"ChatGPT enhancement failed: {e}")
            return None
    
    def _enhance_with_gemini(self, traditional_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Enhance data using Google Gemini"""
        if not self.gemini_client:
            self.logger.warning("Gemini client not initialized. Skipping AI enhancement.")
            return None
        
        try:
            # Convert traditional data to CSV format for AI processing
            # Limit to first 50 records to avoid truncation issues
#            max_records = min(50, len(traditional_data))
#            data_for_ai = traditional_data[:max_records]
            
#            if len(traditional_data) > max_records:
#                logger.info(f"Limiting AI enhancement to first {max_records} records to avoid truncation (total: {len(traditional_data)})")
            
            # Convert to CSV format
            csv_input = self._convert_to_csv_input(traditional_data)
            
            # Create prompt for AI enhancement
            prompt = f"""
            You are an expert at analying job postings. First, let me clarify the steps before providing you with the data.
            
                1. After receiving the CSV formatted data, covert them into a table  Add 3 columns - an unique ID for each row, "Company" and "Location".
                2. For each row in the "Company" column, derive the company name from data in either "Name" or "Title" columns only.  Do not use Detais.If you can't find anything, write "N/A".
                3. For each row in the "Location" column, derive the location from the data in the "Details" column:
                 3a) If the job is likely remote, write "Remote";
                   else If not remote, write the specific location (city, state, country) and make sure to double quote the entire string.
                   If you are not sure, write "Location not specified";

            Here is the input data in CSV format:
            {csv_input}
            
            Before returning the data:
            - The rows must be in the same order as the original data. You can use "Name" as reference.
            - Remove column "Title", "Details" and keep only "Name", "Company", "Location", the unique ID column.
            After completing all these, the # of rows should be the same as the original data.  It shoudl be 71.  If not the same, please explain why and which are missing or added.  And how you can make the # of rows the same.
            
            Then return all rows with the headers in CSV format.
            """
            
#            logger.info(f"Calling Gemini API to enhance {len(data_for_ai)} records (limited from {len(traditional_data)} total)")
            logger.info(f"Calling Gemini API to enhance records (limited from {len(traditional_data)} total)")
            response = self.gemini_client.generate_content(prompt)
            
            # Parse the response content
            response_text = response.text
            logger.info(f"Gemini response content length: {len(response_text)} characters")
#            logger.info(f"Gemini response: {response_text}")
            
            # Parse CSV response
            enhanced_data = self._parse_csv_response(response_text)
            if enhanced_data:
                logger.info(f"Successfully parsed Gemini CSV response with {len(enhanced_data)} records")
                # Merge AI enhanced data with original data
                merged_data = self._merge_ai_enhancement_with_original(traditional_data, enhanced_data)
                return self._add_metadata(merged_data, 'traditional+ai_gemini')
            else:
                logger.error("Failed to parse Gemini CSV response")
                return None
            
        except Exception as e:
            self.logger.error(f"Gemini enhancement failed: {e}")
            return None
    
    def _salvage_partial_json(self, json_text: str) -> List[Dict[str, str]]:
        """Attempt to salvage partial JSON by finding complete objects."""
        try:
            salvaged_data = []
            
            # Split by "}," to find individual objects
            objects = json_text.split('},')
            
            for i, obj in enumerate(objects):
                # Clean up the object text
                if i == 0:  # First object
                    obj = obj.strip()
                    if obj.startswith('['):
                        obj = obj[1:]  # Remove opening bracket
                elif i == len(objects) - 1:  # Last object
                    obj = obj.strip()
                    if obj.endswith(']'):
                        obj = obj[:-1]  # Remove closing bracket
                else:
                    obj = obj.strip()
                
                # Add closing brace if missing
                if not obj.endswith('}'):
                    obj += '}'
                
                # Try to parse this individual object
                try:
                    parsed_obj = json.loads(obj)
                    
                    # Verify it has the required fields
                    if isinstance(parsed_obj, dict) and 'Name' in parsed_obj:
                        salvaged_data.append(parsed_obj)
                        logger.info(f"Salvaged object {i+1}: {parsed_obj.get('Name', 'Unknown')}")
                except json.JSONDecodeError:
                    logger.debug(f"Could not salvage object {i+1}: {obj[:100]}...")
                    continue
            
            if salvaged_data:
                logger.info(f"Successfully salvaged {len(salvaged_data)} complete objects from partial JSON")
                return salvaged_data
            else:
                logger.warning("No complete objects could be salvaged from partial JSON")
                return []
                
        except Exception as e:
            logger.error(f"Error during JSON salvage attempt: {e}")
            return []
    
    def _convert_to_csv_input(self, data: List[Dict[str, str]]) -> str:
        """Convert data to CSV format for AI input."""
        if not data:
            return ""
        
        # Create CSV header
        csv_lines = ["Name,Title,Period,Details"]
        
        # Add data rows
        for item in data:
            # Clean and escape values
            name = item.get('Name', 'N/A').replace('"', '""')
            title = item.get('Title', 'N/A').replace('"', '""')
            period = item.get('Period', 'N/A').replace('"', '""')
            details = item.get('Details', 'N/A').replace('"', '""')
            
            # Wrap in quotes if contains commas
            if ',' in name:
                name = f'"{name}"'
            if ',' in title:
                title = f'"{title}"'
            if ',' in period:
                period = f'"{period}"'
            if ',' in details:
                details = f'"{details}"'
            
            csv_lines.append(f"{name},{title},{period},{details}")
        
        return '\n'.join(csv_lines)
    
    def _merge_ai_enhancement_with_original(self, original_data: List[Dict[str, str]], ai_enhanced_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Merge AI enhanced data (ID, Name, Company, Location) with original data (Name, Title, Period, Details) by matching Name column."""
        if not ai_enhanced_data:
            self.logger.warning("No AI enhanced data to merge")
            # Add Company and Location fields with default values to original data
            enhanced_original = []
            for item in original_data:
                enhanced_item = {
                    'Name': item.get('Name', 'N/A'),
                    'Title': item.get('Title', 'N/A'),
                    'Period': item.get('Period', 'N/A'),
                    'Details': item.get('Details', 'N/A'),
                    'Company': 'N/A',
                    'Location': 'N/A'
                }
                enhanced_original.append(enhanced_item)
            return enhanced_original
        
        # Create a lookup dictionary for AI enhanced data by Name
        ai_lookup = {}
        for ai_item in ai_enhanced_data:
            name = ai_item.get('Name', '').strip()
            if name:
                ai_lookup[name] = ai_item
        
        # Merge the data
        merged_data = []
        for original_item in original_data:
            original_name = original_item.get('Name', '').strip()
            
            # Find matching AI enhanced data
            ai_match = ai_lookup.get(original_name)
            
            if ai_match:
                # Merge original data with AI enhancement
                merged_item = {
                    'Name': original_item.get('Name', 'N/A'),
                    'Title': original_item.get('Title', 'N/A'),
                    'Period': original_item.get('Period', 'N/A'),
                    'Details': original_item.get('Details', 'N/A'),
                    'Company': ai_match.get('Company', 'N/A'),
                    'Location': ai_match.get('Location', 'N/A')
                }
                merged_data.append(merged_item)
                self.logger.debug(f"Successfully merged data for: {original_name}")
            else:
                # No AI match found, use original data with default Company/Location
                merged_item = {
                    'Name': original_item.get('Name', 'N/A'),
                    'Title': original_item.get('Title', 'N/A'),
                    'Period': original_item.get('Period', 'N/A'),
                    'Details': original_item.get('Details', 'N/A'),
                    'Company': 'N/A',
                    'Location': 'N/A'
                }
                merged_data.append(merged_item)
                self.logger.warning(f"No AI enhancement match found for: {original_name}")
        
        self.logger.info(f"Successfully merged {len(merged_data)} records (original: {len(original_data)}, AI enhanced: {len(ai_enhanced_data)})")
        return merged_data
    
    def _verify_enhanced_data(self, data: List[Dict[str, str]]) -> bool:
        """Verify that the enhanced data has the required structure."""
        if not data or not isinstance(data, list):
            return False
        
        required_fields = ['Name', 'Title', 'Period', 'Details', 'Company', 'Location']
        
        for item in data:
            if not isinstance(item, dict):
                return False
            
            # Check if all required fields exist
            for field in required_fields:
                if field not in item:
                    return False
        
        return True
    
    def _add_metadata(self, data: List[Dict[str, str]], extraction_method: str) -> List[Dict[str, str]]:
        """Add metadata to enhanced data."""
        for item in data:
            item['extraction_method'] = extraction_method
            item['confidence'] = 0.9
            
            # Ensure all required fields exist
            for field in ['Name', 'Title', 'Period', 'Details', 'Company', 'Location']:
                if field not in item:
                    item[field] = 'N/A'
        
        return data
    
    def _parse_csv_response(self, response_text: str) -> List[Dict[str, str]]:
        """Parse CSV response from AI models."""
        try:
            # Clean up the response text
            lines = response_text.strip().split('\n')
            
            # Find the CSV content (skip any markdown formatting)
            csv_lines = []
            in_csv = False
            
            for line in lines:
                line = line.strip()
                if line.startswith('```csv') or line.startswith('```'):
                    in_csv = True
                    continue
                elif line.startswith('```') and in_csv:
                    in_csv = False
                    break
                elif in_csv and line:
                    csv_lines.append(line)
                elif not in_csv and ',' in line:
                    # Found CSV content without markdown
                    csv_lines.append(line)
            
            if not csv_lines:
                # If no CSV found, try to parse the entire response as CSV
                csv_lines = [line.strip() for line in lines if line.strip() and ',' in line]
            
            # Filter out lines that don't look like CSV data
            # AI models should return: ID, Name, Company, Location (4 columns)
            filtered_csv_lines = []
            for line in csv_lines:
                if ',' in line and len(line.split(',')) >= 4:  # Should have at least 4 columns
                    filtered_csv_lines.append(line)
            
            if len(filtered_csv_lines) < 2:  # Need at least header + 1 data row
                logger.error(f"Insufficient CSV content found. Found {len(filtered_csv_lines)} valid lines from {len(csv_lines)} total lines")
                logger.error(f"Sample lines: {csv_lines[:3]}")
                return None
            
            csv_lines = filtered_csv_lines
            
            # Parse CSV content
            import csv
            from io import StringIO
            
            csv_content = '\n'.join(csv_lines)
            logger.info(f"Parsing CSV content: {csv_content[:200]}...")
            
            # Use StringIO to parse CSV
            csv_file = StringIO(csv_content)
            csv_reader = csv.DictReader(csv_file)
            
            enhanced_data = []
            for row in csv_reader:
                # Clean up the row data and ensure required fields exist
                cleaned_row = {}
                required_fields = ['ID', 'Name', 'Company', 'Location']
                
                for field in required_fields:
                    if field in row and row[field]:
                        # Remove quotes and clean up
                        cleaned_value = row[field].strip().strip('"').strip("'")
                        cleaned_row[field] = cleaned_value
                    else:
                        # Set default value for missing fields
                        if field == 'ID':
                            cleaned_row[field] = 'N/A'
                        elif field == 'Name':
                            cleaned_row[field] = 'N/A'
                        elif field == 'Company':
                            cleaned_row[field] = 'N/A'
                        elif field == 'Location':
                            cleaned_row[field] = 'N/A'
                
                enhanced_data.append(cleaned_row)
            
            logger.info(f"Successfully parsed {len(enhanced_data)} CSV records with fields: {list(enhanced_data[0].keys()) if enhanced_data else 'None'}")
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error parsing CSV response: {e}")
            logger.error(f"Response content: {response_text[:500]}...")
            return None
    
    def process_mhtml_file(self, file_path: str, use_ai: bool = False, ai_model: str = "chatgpt") -> Dict[str, Any]:
        """Main method to process an MHTML file and return comprehensive results."""
        try:
            logger.info(f"Processing MHTML file: {file_path} with traditional parsing + {'AI enhancement (' + ai_model + ')' if use_ai else 'no AI enhancement'}")
            
            # Read and parse the file
            mhtml_message = self.read_mhtml_file(file_path)
            html_content = self.extract_html_content(mhtml_message)
            
            if not html_content:
                return {"error": "No HTML content found in MHTML file"}
            
            # Always extract data using traditional method first
            extracted_data = self.extract_linkedin_data(html_content)
            logger.info(f"Traditional parsing extracted {len(extracted_data)} records")
            
            # If AI enhancement is requested, enhance the data
            if use_ai and (self.openai_client or self.gemini_client):
                logger.info(f"AI enhancement requested with model: {ai_model}")
                logger.info(f"OpenAI client available: {self.openai_client is not None}")
                logger.info(f"Gemini client available: {self.gemini_client is not None}")
                
                try:
                    enhanced_data = self.enhance_data_with_ai(extracted_data, ai_model)
                    if enhanced_data is not None:
                        logger.info(f"AI enhancement completed successfully")
                        logger.info(f"Enhanced data sample: {enhanced_data[0] if enhanced_data else 'None'}")
                        logger.info(f"Enhanced data has Company field: {'Company' in enhanced_data[0] if enhanced_data else False}")
                        logger.info(f"Enhanced data has Location field: {'Location' in enhanced_data[0] if enhanced_data else False}")
                        
#                        logger.info(f"Full enhanced data: {enhanced_data}")
                        # Verify that the data is actually enhanced (has Company and Location fields)
                        if enhanced_data and len(enhanced_data) > 0 and 'Company' in enhanced_data[0] and 'Location' in enhanced_data[0]:
                            logger.info("Enhanced data verified - contains Company and Location fields")
                            extracted_data = enhanced_data
                        else:
                            logger.warning("AI enhancement returned data but missing Company/Location fields, using traditional data")
                            extracted_data = enhanced_data
                    else:
                        logger.warning("AI enhancement failed, using traditional data only")
                except Exception as e:
                    logger.error(f"AI enhancement error: {e}, using traditional data only")
            else:
                logger.info(f"AI enhancement not requested (use_ai: {use_ai})")
                logger.info(f"OpenAI client: {self.openai_client is not None}")
                logger.info(f"Gemini client: {self.gemini_client is not None}")
            
            self.extracted_data = extracted_data
            
            # Analyze the data
            analysis = self.analyze_data(extracted_data)
            
            # Prepare results
            results = {
                "success": True,
                "file_path": file_path,
                "extracted_data": extracted_data,
                "analysis": analysis,
                "summary": {
                    "total_posts": len(extracted_data),
                    "quality_score": analysis["data_quality_score"],
                    "processing_time": datetime.now().isoformat()
                }
            }
            
            # Add extraction method to analysis
            if use_ai:
                results["analysis"]["extraction_method"] = f"traditional+ai_{ai_model}"
            else:
                results["analysis"]["extraction_method"] = "traditional"
            
            logger.info(f"Successfully processed {len(extracted_data)} posts with quality score {analysis['data_quality_score']}%")
            return results
            
        except Exception as e:
            logger.error(f"Error processing MHTML file: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }

# Example usage and testing
if __name__ == '__main__':
    # Initialize the AI agent
    agent = LinkedInDataExtractor()
    
    # Example file path (update this to your actual file)
    file_path = '/Users/peekay/Downloads/LinkedIn_hiring _product manager_ martech_ Aug_9.mhtml'
    
    if os.path.exists(file_path):
        # Process the file
        results = agent.process_mhtml_file(file_path)
        
        if results.get("success"):
            print("=== EXTRACTION RESULTS ===")
            print(f"Total posts extracted: {results['summary']['total_posts']}")
            print(f"Data quality score: {results['analysis']['data_quality_score']}%")
            print(f"Insights: {', '.join(results['analysis']['insights'])}")
            
            print("\n=== EXTRACTED DATA ===")
            print(agent.get_formatted_output(results['extracted_data']))
            
            # Export to files
            #csv_file = agent.export_to_csv(results['extracted_data'])
            #json_file = agent.export_to_json(results['extracted_data'])
            #print(f"\nData exported to: {csv_file} and {json_file}")
            
        else:
            print(f"Error: {results.get('error', 'Unknown error')}")
    else:
        print(f"File not found: {file_path}")
        print("Please update the file_path variable with the correct path to your MHTML file.") 