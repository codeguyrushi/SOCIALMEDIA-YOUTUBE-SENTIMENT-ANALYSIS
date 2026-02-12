import pandas as pd
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from datetime import datetime

def find_latest_cleaned_file():
    """Find the most recent cleaned CSV file"""
    files = [f for f in os.listdir('.') if f.startswith('cleaned_comments_') and f.endswith('.csv')]
    if not files:
        print("❌ No cleaned file found!")
        print("   Please run data_cleaning.py first!")
        return None
    latest = sorted(files)[-1]
    print(f"📂 Found file: {latest}")
    return latest

def analyze_sentiment(text, analyzer):
    """Analyze sentiment of a single text"""
    if not text or text.strip() == '':
        return 0, 'neutral'
    
    # Get sentiment scores
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    
    # Classify sentiment
    if compound >= 0.05:
        sentiment = 'positive'
    elif compound <= -0.05:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return compound, sentiment

def perform_sentiment_analysis(filename):
    """Main sentiment analysis function"""
    
    print("\n" + "="*60)
    print("🎭 STARTING SENTIMENT ANALYSIS")
    print("="*60)
    
    # Load cleaned data
    print("\n📖 Loading cleaned data...")
    df = pd.read_csv(filename, encoding='utf-8')
    print(f"✅ Loaded {len(df)} comments")
    
    # Initialize VADER sentiment analyzer
    print("\n🔧 Initializing sentiment analyzer...")
    analyzer = SentimentIntensityAnalyzer()
    print("✅ Analyzer ready!")
    
    # Analyze each comment
    print("\n🎭 Analyzing sentiment...")
    df['sentiment_score'], df['sentiment'] = zip(*df['cleaned_text'].apply(
        lambda x: analyze_sentiment(x, analyzer)
    ))
    print("✅ Analysis complete!")
    
    # Calculate statistics
    print("\n📊 SENTIMENT ANALYSIS RESULTS:")
    print("="*60)
    
    sentiment_counts = df['sentiment'].value_counts()
    total = len(df)
    
    print(f"\n📈 Overall Sentiment Distribution:")
    print(f"   Positive: {sentiment_counts.get('positive', 0)} ({sentiment_counts.get('positive', 0)/total*100:.1f}%)")
    print(f"   Neutral:  {sentiment_counts.get('neutral', 0)} ({sentiment_counts.get('neutral', 0)/total*100:.1f}%)")
    print(f"   Negative: {sentiment_counts.get('negative', 0)} ({sentiment_counts.get('negative', 0)/total*100:.1f}%)")
    
    print(f"\n📊 Sentiment Score Statistics:")
    print(f"   Average score: {df['sentiment_score'].mean():.3f}")
    print(f"   Most positive: {df['sentiment_score'].max():.3f}")
    print(f"   Most negative: {df['sentiment_score'].min():.3f}")
    
    # Find most positive and negative comments
    print("\n😊 MOST POSITIVE COMMENT:")
    most_positive = df.loc[df['sentiment_score'].idxmax()]
    print(f"   Score: {most_positive['sentiment_score']:.3f}")
    print(f"   Text: {most_positive['text'][:200]}...")
    
    print("\n😞 MOST NEGATIVE COMMENT:")
    most_negative = df.loc[df['sentiment_score'].idxmin()]
    print(f"   Score: {most_negative['sentiment_score']:.3f}")
    print(f"   Text: {most_negative['text'][:200]}...")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'sentiment_results_{timestamp}.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n💾 Results saved to: {output_file}")
    
    return df, output_file

def create_visualizations(df):
    """Create sentiment visualization charts"""
    
    print("\n📊 Creating visualizations...")
    
    # Create figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Pie chart - Sentiment Distribution
    sentiment_counts = df['sentiment'].value_counts()
    colors = ['#2ecc71', '#95a5a6', '#e74c3c']  # green, gray, red
    axes[0].pie(sentiment_counts.values, labels=sentiment_counts.index, 
                autopct='%1.1f%%', colors=colors, startangle=90)
    axes[0].set_title('Sentiment Distribution', fontsize=14, fontweight='bold')
    
    # Histogram - Sentiment Score Distribution
    axes[1].hist(df['sentiment_score'], bins=30, color='#3498db', edgecolor='black', alpha=0.7)
    axes[1].set_xlabel('Sentiment Score', fontsize=12)
    axes[1].set_ylabel('Number of Comments', fontsize=12)
    axes[1].set_title('Sentiment Score Distribution', fontsize=14, fontweight='bold')
    axes[1].axvline(x=0, color='red', linestyle='--', linewidth=2, label='Neutral')
    axes[1].legend()
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plot_file = f'sentiment_visualization_{timestamp}.png'
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"✅ Visualization saved to: {plot_file}")
    
    # Show the plot
    plt.show()
    print("✅ Charts displayed!")

def main():
    """Main function"""
    
    print("="*60)
    print("🎯 YouTube Comments Sentiment Analysis")
    print("="*60)
    
    # Find the latest cleaned file
    filename = find_latest_cleaned_file()
    
    if not filename:
        return
    
    # Perform sentiment analysis
    df, output_file = perform_sentiment_analysis(filename)
    
    # Create visualizations
    create_visualizations(df)
    
    print("\n" + "="*60)
    print("✅ SENTIMENT ANALYSIS COMPLETE!")
    print("="*60)
    print(f"\n📌 Results saved to: {output_file}")
    print("📌 Check the charts that opened!")
    print("\n🎉 Your sentiment analysis project is done!")

if __name__ == "__main__":
    main()