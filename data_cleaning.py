import pandas as pd
import re
import os
from datetime import datetime

def find_latest_comments_file():
    """Find the most recent comments CSV file"""
    files = [f for f in os.listdir('.') if f.startswith('youtube_comments_') and f.endswith('.csv')]
    if not files:
        print("❌ No comments file found!")
        return None
    latest = sorted(files)[-1]
    print(f"📂 Found file: {latest}")
    return latest

def clean_text(text):
    """Clean and preprocess text"""
    if pd.isna(text):
        return ""
    
    # Convert to string
    text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove mentions (@username)
    text = re.sub(r'@\w+', '', text)
    
    # Remove hashtags (optional - you might want to keep these for analysis)
    # text = re.sub(r'#\w+', '', text)
    
    # Remove special characters and numbers (keep letters and basic punctuation)
    text = re.sub(r'[^a-zA-Z\s.,!?]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def clean_data(filename):
    """Main cleaning function"""
    
    print("\n" + "="*60)
    print("🧹 STARTING DATA CLEANING")
    print("="*60)
    
    # Load the data
    print("\n📖 Loading data...")
    df = pd.read_csv(filename, encoding='utf-8')
    print(f"✅ Loaded {len(df)} comments")
    
    # Show original data sample
    print("\n📊 Original Data Sample:")
    print(df[['author', 'text', 'like_count']].head(3))
    
    # Remove duplicates
    print("\n🔍 Removing duplicates...")
    original_count = len(df)
    df = df.drop_duplicates(subset=['text'], keep='first')
    duplicates_removed = original_count - len(df)
    print(f"✅ Removed {duplicates_removed} duplicate comments")
    
    # Remove empty comments
    print("\n🔍 Removing empty comments...")
    df = df[df['text'].notna()]
    df = df[df['text'].str.strip() != '']
    print(f"✅ Remaining comments: {len(df)}")
    
    # Clean the text
    print("\n🧼 Cleaning text...")
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    # Remove comments that became empty after cleaning
    df = df[df['cleaned_text'].str.strip() != '']
    print(f"✅ After cleaning: {len(df)} comments")
    
    # Show cleaned data sample
    print("\n📊 Cleaned Data Sample:")
    print(df[['author', 'text', 'cleaned_text']].head(3))
    
    # Basic statistics
    print("\n📈 Data Statistics:")
    print(f"   Total comments: {len(df)}")
    print(f"   Average comment length: {df['cleaned_text'].str.len().mean():.2f} characters")
    print(f"   Average likes per comment: {df['like_count'].mean():.2f}")
    print(f"   Most liked comment: {df['like_count'].max()} likes")
    
    # Save cleaned data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'cleaned_comments_{timestamp}.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n💾 Cleaned data saved to: {output_file}")
    
    return df, output_file

def main():
    """Main function"""
    
    print("="*60)
    print("🎯 YouTube Comments Data Cleaning")
    print("="*60)
    
    # Find the latest comments file
    filename = find_latest_comments_file()
    
    if not filename:
        print("\n❌ Please run youtube_scraper.py first to collect data!")
        return
    
    # Clean the data
    df, output_file = clean_data(filename)
    
    print("\n" + "="*60)
    print("✅ DATA CLEANING COMPLETE!")
    print("="*60)
    print(f"\n📌 Your cleaned data is ready: {output_file}")
    print("\n📌 Next step: Run sentiment analysis!")

if __name__ == "__main__":
    main()