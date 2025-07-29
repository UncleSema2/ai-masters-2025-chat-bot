#!/usr/bin/env python3
"""
Main entry point for AI Master 2025 Chatbot
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.main import main as bot_main


def main():
    """Entry point for the chatbot - wrapper for async main"""
    asyncio.run(bot_main())


if __name__ == "__main__":
    main()
