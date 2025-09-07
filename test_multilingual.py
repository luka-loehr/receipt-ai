#!/usr/bin/env python3
"""
Test script for multilingual AI-generated receipt system
"""

import os
import sys

# Add src to path
sys.path.insert(0, 'src')

from src.config import AppConfig, Language, set_language
from src.data_manager import ModularDataManager

def test_language(language: Language, language_name: str):
    """Test the system with a specific language"""
    print(f"\n{'='*50}")
    print(f"🌍 Testing {language_name.upper()} ({language.value})")
    print(f"{'='*50}")
    
    # Set language
    set_language(language)
    
    # Create new data manager with updated config
    config = AppConfig.from_environment()
    config.language = language
    data_manager = ModularDataManager(config)
    
    try:
        # Generate receipt content
        print("🤖 Generating AI content...")
        receipt_content = data_manager.generate_complete_receipt()
        
        # Display results
        print(f"\n📄 GENERATED CONTENT:")
        print(f"Language: {receipt_content.language}")
        print(f"Greeting: {receipt_content.header.greeting}")
        print(f"Title: {receipt_content.header.title}")  
        print(f"Date: {receipt_content.header.date_formatted}")
        print(f"Brief (first 100 chars): {receipt_content.summary.brief[:100]}...")
        
        if receipt_content.task_section:
            print(f"Task Section Title: {receipt_content.task_section.section_title}")
        
        if receipt_content.shopping_section:
            print(f"Shopping Section Title: {receipt_content.shopping_section.section_title}")
        
        print(f"Footer Label: {receipt_content.footer.timestamp_label}")
        print(f"Timestamp: {receipt_content.footer.timestamp}")
        
        if receipt_content.footer.motivational_note:
            print(f"Motivational Note: {receipt_content.footer.motivational_note}")
        
        # Test data counts
        print(f"\n📊 DATA SUMMARY:")
        print(f"Emails: {receipt_content.total_emails}")
        print(f"Events: {receipt_content.total_events}")
        print(f"Tasks: {receipt_content.total_tasks}")
        print(f"Shopping Items: {receipt_content.total_shopping_items}")
        
        print(f"✅ {language_name} test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ {language_name} test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run multilingual tests"""
    print("🌐 MULTILINGUAL RECEIPT SYSTEM TEST")
    print("Testing AI-generated content in different languages")
    
    # Test languages
    test_results = []
    
    # Test German
    result_german = test_language(Language.GERMAN, "German")
    test_results.append(("German", result_german))
    
    # Test English  
    result_english = test_language(Language.ENGLISH, "English")
    test_results.append(("English", result_english))
    
    # Test Spanish (if we want to be ambitious)
    result_spanish = test_language(Language.SPANISH, "Spanish")
    test_results.append(("Spanish", result_spanish))
    
    # Summary
    print(f"\n{'='*50}")
    print("🏁 TEST SUMMARY")
    print(f"{'='*50}")
    
    for language, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{language}: {status}")
    
    total_passed = sum(1 for _, success in test_results if success)
    print(f"\nResults: {total_passed}/{len(test_results)} tests passed")
    
    if total_passed == len(test_results):
        print("🎉 All multilingual tests passed!")
        print("🌍 System is ready for international use!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
