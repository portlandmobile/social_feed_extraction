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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInDataExtractor:
    """AI-powered LinkedIn data extraction agent"""
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the AI-enhanced LinkedIn parser"""
        self.openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
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
        """AI-powered extraction for complex or non-standard formats"""
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
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured data from LinkedIn posts. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            ai_data = json.loads(response.choices[0].message.content)
            
            # Add metadata
            for item in ai_data:
                item['extraction_method'] = 'ai'
                item['confidence'] = 0.9
            
            return ai_data
            
        except Exception as e:
            self.logger.error(f"AI extraction failed: {e}")
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
    
    def export_to_csv(self, data_list: List[Dict[str, str]], filename: str = None) -> str:
        """Export data to CSV format."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_data_{timestamp}.csv"
        
        df = pd.DataFrame(data_list)
        df.to_csv(filename, index=False)
        return filename
    
    def export_to_json(self, data_list: List[Dict[str, str]], filename: str = None) -> str:
        """Export data to JSON format."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_data_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def process_mhtml_file(self, file_path: str, use_ai: bool = False) -> Dict[str, Any]:
        """Main method to process an MHTML file and return comprehensive results."""
        try:
            logger.info(f"Processing MHTML file: {file_path} with {'AI' if use_ai else 'traditional'} parsing")
            
            # Read and parse the file
            mhtml_message = self.read_mhtml_file(file_path)
            html_content = self.extract_html_content(mhtml_message)
            
            if not html_content:
                return {"error": "No HTML content found in MHTML file"}
            
            # Extract data using chosen method
            if use_ai and self.openai_client:
                extracted_data = self.extract_linkedin_data_ai(html_content)
                if not extracted_data:  # Fallback to traditional if AI fails
                    logger.warning("AI extraction failed, falling back to traditional method")
                    extracted_data = self.extract_linkedin_data(html_content)
            else:
                extracted_data = self.extract_linkedin_data(html_content)
            
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
                results["analysis"]["extraction_method"] = "ai"
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
    
    def get_formatted_output(self, data_list: List[Dict[str, str]], max_width: int = 100) -> str:
        """Generate formatted table output for display."""
        if not data_list:
            return "No data to display"
        
        # Calculate column widths
        col_widths = {
            'Name': min(30, max(len(str(item.get('Name', ''))) for item in data_list) + 2),
            'Title': min(60, max(len(str(item.get('Title', ''))) for item in data_list) + 2),
            'Period': min(15, max(len(str(item.get('Period', ''))) for item in data_list) + 2),
            'Details': min(50, max(len(str(item.get('Details', ''))) for item in data_list) + 2)
        }
        
        # Create header
        header = f"{'Name':<{col_widths['Name']}} | {'Title':<{col_widths['Title']}} | {'Period':<{col_widths['Period']}} | {'Details':<{col_widths['Details']}}"
        separator = "-" * len(header)
        
        # Create rows
        rows = []
        for entry in data_list:
            name = str(entry.get('Name', ''))[:col_widths['Name']-2]
            title = str(entry.get('Title', ''))[:col_widths['Title']-2]
            period = str(entry.get('Period', ''))[:col_widths['Period']-2]
            details = str(entry.get('Details', ''))[:col_widths['Details']-2]
            
            row = f"{name:<{col_widths['Name']}} | {title:<{col_widths['Title']}} | {period:<{col_widths['Period']}} | {details:<{col_widths['Details']}}"
            rows.append(row)
        
        return "\n".join([header, separator] + rows)

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
            csv_file = agent.export_to_csv(results['extracted_data'])
            json_file = agent.export_to_json(results['extracted_data'])
            print(f"\nData exported to: {csv_file} and {json_file}")
            
        else:
            print(f"Error: {results.get('error', 'Unknown error')}")
    else:
        print(f"File not found: {file_path}")
        print("Please update the file_path variable with the correct path to your MHTML file.") 