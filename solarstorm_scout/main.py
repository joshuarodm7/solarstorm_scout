#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
SolarStorm Scout - Space Weather Social Media Bot
Posts HF propagation updates to Bluesky and Mastodon.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from solarstorm_scout.config import Config, setup_logging
from solarstorm_scout.spaceweather import fetch_space_weather_data
from solarstorm_scout.formatter import format_thread_posts
from solarstorm_scout.social import SocialMediaManager

logger = logging.getLogger(__name__)


async def main():
    """Main bot execution."""
    # Setup logging
    log_level = Config().get('LOG_LEVEL', 'INFO')
    setup_logging(log_level)
    
    logger.info("=" * 50)
    logger.info("🌞 SolarStorm Scout Starting")
    logger.info("=" * 50)
    
    # Load configuration
    config = Config()
    
    # Validate configuration
    if not config.validate_config():
        logger.error("Configuration validation failed!")
        sys.exit(1)
    
    # Setup social media manager
    social = SocialMediaManager()
    
    # Add platforms
    if config.is_bluesky_enabled():
        try:
            handle, password = config.get_bluesky_config()
            if social.add_bluesky(handle, password):
                logger.info("✓ Bluesky platform added")
            else:
                logger.warning("✗ Failed to add Bluesky platform")
        except Exception as e:
            logger.error(f"Error setting up Bluesky: {e}")
    
    if config.is_mastodon_enabled():
        try:
            api_url, token, client_id, client_secret = config.get_mastodon_config()
            if social.add_mastodon(api_url, token, client_id, client_secret):
                logger.info("✓ Mastodon platform added")
            else:
                logger.warning("✗ Failed to add Mastodon platform")
        except Exception as e:
            logger.error(f"Error setting up Mastodon: {e}")
    
    # Check if any platforms were added
    if social.get_platform_count() == 0:
        logger.error("No social media platforms configured successfully!")
        sys.exit(1)
    
    logger.info(f"Configured platforms: {', '.join(social.get_platform_names())}")
    
    # Fetch space weather data
    logger.info("Fetching space weather data from NOAA...")
    try:
        data = await fetch_space_weather_data()
        logger.info("✓ Space weather data fetched successfully")
        
        # Log key data points
        logger.info(f"  Solar Flux: {data.get('solar_flux', 'N/A')} sfu")
        logger.info(f"  K-index: {data.get('k_index', 'N/A')}")
        logger.info(f"  Conditions: {data.get('propagation_conditions', 'N/A')}")
        logger.info(f"  X-Ray: {data.get('xray_class', 'N/A')}")
        
    except Exception as e:
        logger.error(f"Failed to fetch space weather data: {e}")
        sys.exit(1)
    
    # Format posts (we'll post to each platform separately with platform-specific formatting)
    logger.info("Posting to social media...")
    try:
        results = await social.post_to_all(data)
        
        # Log results
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"Posted to {success_count}/{len(results)} platforms")
        
        for platform, success in results.items():
            if success:
                logger.info(f"  ✓ {platform}: Success")
            else:
                logger.warning(f"  ✗ {platform}: Failed")
        
        if success_count == 0:
            logger.error("Failed to post to any platforms!")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to post to social media: {e}")
        sys.exit(1)
    
    logger.info("=" * 50)
    logger.info("🌞 SolarStorm Scout Completed Successfully")
    logger.info("=" * 50)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
