#!/usr/bin/env python3
"""
Script to parse and populate database with ITMO AI master programs data
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging

from parsers.itmo_parser import ITMOParser


def main():
    """Parse ITMO programs and populate database"""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting data parsing...")

    try:
        parser = ITMOParser()
        parser.parse_and_save_programs()
        logger.info("Data parsing completed successfully!")

    except Exception as e:
        logger.error(f"Error during data parsing: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
