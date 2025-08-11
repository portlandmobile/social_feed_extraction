#!/usr/bin/env python3
"""
Demo script for the LinkedIn Data Extraction AI Agent
Shows various usage patterns and capabilities
"""

import os
import json
from ai_agent import LinkedInDataExtractor

def demo_basic_usage():
    """Demonstrate basic usage of the AI agent."""
    print("🎯 Demo 1: Basic Usage")
    print("-" * 40)
    
    # Initialize the agent
    agent = LinkedInDataExtractor()
    
    # Example file path (update this to your actual file)
    file_path = '/Users/peekay/Downloads/LinkedIn_hiring _product manager_ martech_ Aug_9.mhtml'
    
    if os.path.exists(file_path):
        print(f"📁 Processing file: {os.path.basename(file_path)}")
        
        # Process the file
        results = agent.process_mhtml_file(file_path)
        
        if results.get("success"):
            print(f"✅ Success! Extracted {len(results['extracted_data'])} posts")
            print(f"🎯 Quality Score: {results['analysis']['data_quality_score']}%")
            
            # Show first few entries
            print("\n📊 Sample Data:")
            for i, entry in enumerate(results['extracted_data'][:3]):
                print(f"  {i+1}. {entry['Name']} - {entry['Title'][:50]}...")
                
        else:
            print(f"❌ Error: {results.get('error')}")
    else:
        print(f"⚠️  File not found: {file_path}")
        print("💡 Update the file_path variable with your actual MHTML file")
    
    print()

def demo_data_analysis():
    """Demonstrate the AI agent's data analysis capabilities."""
    print("🧠 Demo 2: AI Data Analysis")
    print("-" * 40)
    
    agent = LinkedInDataExtractor()
    file_path = '/Users/peekay/Downloads/LinkedIn_hiring _product manager_ martech_ Aug_9.mhtml'
    
    if os.path.exists(file_path):
        results = agent.process_mhtml_file(file_path)
        
        if results.get("success"):
            analysis = results['analysis']
            
            print("📈 Analysis Results:")
            print(f"  • Total Posts: {analysis['total_posts']}")
            print(f"  • Unique Names: {analysis['unique_names']}")
            print(f"  • Data Quality: {analysis['data_quality_score']}%")
            
            print("\n💡 AI Insights:")
            for insight in analysis['insights']:
                print(f"  • {insight}")
            
            if analysis['recommendations']:
                print("\n🔧 Recommendations:")
                for rec in analysis['recommendations']:
                    print(f"  • {rec}")
    else:
        print("⚠️  File not found - skipping analysis demo")
    
    print()

def demo_export_formats():
    """Demonstrate export functionality."""
    print("📁 Demo 3: Export Formats")
    print("-" * 40)
    
    agent = LinkedInDataExtractor()
    file_path = '/Users/peekay/Downloads/LinkedIn_hiring _product manager_ martech_ Aug_9.mhtml'
    
    if os.path.exists(file_path):
        results = agent.process_mhtml_file(file_path)
        
        if results.get("success"):
            data = results['extracted_data']
            
            # Export to CSV
            csv_file = agent.export_to_csv(data)
            print(f"✅ CSV exported to: {csv_file}")
            
            # Export to JSON
            json_file = agent.export_to_json(data)
            print(f"✅ JSON exported to: {json_file}")
            
            # Show JSON sample
            print("\n📄 JSON Sample (first entry):")
            sample_json = json.dumps(data[0], indent=2)
            print(sample_json[:200] + "..." if len(sample_json) > 200 else sample_json)
            
            # Clean up demo files
            if os.path.exists(csv_file):
                os.remove(csv_file)
            if os.path.exists(json_file):
                os.remove(json_file)
            print("\n🧹 Demo export files cleaned up")
    else:
        print("⚠️  File not found - skipping export demo")
    
    print()

def demo_web_interface():
    """Show how to start the web interface."""
    print("🌐 Demo 4: Web Interface")
    print("-" * 40)
    print("To start the web interface:")
    print("1. Run: python3 start_ai_agent.py")
    print("2. Open: http://localhost:5000")
    print("3. Upload your MHTML file")
    print("4. View results and export data")
    print()

def main():
    """Run all demos."""
    print("🚀 LinkedIn Data Extraction AI Agent - Demo")
    print("=" * 60)
    print()
    
    demo_basic_usage()
    demo_data_analysis()
    demo_export_formats()
    demo_web_interface()
    
    print("🎉 Demo completed!")
    print("💡 The AI agent is ready to use!")
    print("🌐 Start the web interface with: python3 start_ai_agent.py")

if __name__ == '__main__':
    main() 