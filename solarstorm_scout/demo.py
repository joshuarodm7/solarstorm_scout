#!/usr/bin/env python3
"""
SolarStorm Scout - Test/Demo Script
Shows what the posts will look like without actually posting to social media.
"""

import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from solarstorm_scout.spaceweather import fetch_space_weather_data
from solarstorm_scout.formatter import format_thread_posts, get_post_stats

# Setup simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print demo banner."""
    print("\n" + "=" * 70)
    print("🌞  SOLARSTORM SCOUT - POST PREVIEW DEMO")
    print("=" * 70)
    print()


def print_post(post_num: int, post_data: dict, platform: str, limit: int):
    """Print a single post preview."""
    text = post_data['text']
    image_url = post_data.get('image_url')
    alt_text = post_data.get('alt_text', '')
    
    length = len(text)
    remaining = limit - length
    
    # Header
    print(f"\n┌─ POST {post_num}/5 ".ljust(70, '─') + "┐")
    print(f"│ Platform: {platform.ljust(55)} │")
    print(f"│ Length: {length}/{limit} chars ({{remaining}} remaining)".format(remaining=remaining).ljust(68) + " │")
    
    if image_url:
        print(f"│ 🖼️  Image: {image_url[:50]}...".ljust(68) + " │")
    
    print("├" + "─" * 68 + "┤")
    
    # Post content
    for line in text.split('\n'):
        # Wrap long lines
        while len(line) > 66:
            print(f"│ {line[:66]} │")
            line = line[66:]
        print(f"│ {line.ljust(66)} │")
    
    print("└" + "─" * 68 + "┘")


async def main():
    """Run the demo."""
    print_banner()
    
    print("Fetching live space weather data from NOAA...")
    print()
    
    try:
        # Fetch real data
        data = await fetch_space_weather_data()
        
        # Show data summary
        print("📊 DATA SUMMARY:")
        print(f"   Solar Flux: {data.get('solar_flux', 'N/A')} sfu")
        print(f"   K-index: {data.get('k_index', 'N/A')}")
        print(f"   foF2: {data.get('fof2', 'N/A')} MHz")
        print(f"   Conditions: {data.get('propagation_conditions', 'N/A')}")
        print(f"   D-Region: {data.get('d_region_absorption', 'N/A')}")
        print(f"   Aurora: {data.get('aurora_power', 'N/A')} GW")
        print(f"   X-Ray: {data.get('xray_class', 'N/A')}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Format posts for both platforms
        print("\n" + "=" * 70)
        print("BLUESKY POSTS (300 character limit)")
        print("=" * 70)
        
        bluesky_posts = format_thread_posts(data, 'bluesky')
        bluesky_stats = get_post_stats(bluesky_posts, 'bluesky')
        
        for i, post_data in enumerate(bluesky_posts):
            print_post(i + 1, post_data, 'Bluesky', 300)
        
        print("\n" + "=" * 70)
        print("MASTODON POSTS (500 character limit)")
        print("=" * 70)
        
        mastodon_posts = format_thread_posts(data, 'mastodon')
        mastodon_stats = get_post_stats(mastodon_posts, 'mastodon')
        
        for i, post_data in enumerate(mastodon_posts):
            print_post(i + 1, post_data, 'Mastodon', 500)
        
        # Statistics
        print("\n" + "=" * 70)
        print("STATISTICS")
        print("=" * 70)
        
        print("\nBluesky:")
        for post_stat in bluesky_stats['posts']:
            print(f"  Post {post_stat['number']}: {post_stat['length']}/300 chars " +
                  f"({post_stat['remaining']} remaining) " +
                  f"{'[+image]' if post_stat['has_image'] else ''}")
        
        print("\nMastodon:")
        for post_stat in mastodon_stats['posts']:
            print(f"  Post {post_stat['number']}: {post_stat['length']}/500 chars " +
                  f"({post_stat['remaining']} remaining) " +
                  f"{'[+image]' if post_stat['has_image'] else ''}")
        
        # Image URLs
        print("\n" + "=" * 70)
        print("IMAGE SOURCES")
        print("=" * 70)
        print("\nPost 1 (Solar Indices):")
        print("  (no image)")
        print("\nPost 2 (Band Conditions):")
        print("  (no image)")
        print("\nPost 3 (D-Region Absorption):")
        print("  🗺️  " + bluesky_posts[2]['image_url'])
        print("\nPost 4 (Aurora):")
        print("  🌌 " + bluesky_posts[3]['image_url'])
        print("\nPost 5 (X-Ray):")
        if bluesky_posts[4]['image_url'] == 'GENERATE_CHART':
            print("  📊 Generated chart from NOAA JSON data (matplotlib)")
        else:
            print("  ☀️  " + bluesky_posts[4]['image_url'])
        
        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETE - Posts formatted correctly!")
        print("=" * 70)
        print("\nTo post for real:")
        print("  1. Set up your .env file with credentials")
        print("  2. Run: python3 -m solarstorm_scout.main")
        print()
        
    except Exception as e:
        logger.error(f"Error running demo: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
