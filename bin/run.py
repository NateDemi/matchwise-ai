#!/usr/bin/env python
# scripts/run.py
import argparse
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.matching.matcher import process_receipt_items


def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('matching.log')
        ]
    )

def main():
    """Main function to run receipt matching"""
    parser = argparse.ArgumentParser(description='Run receipt-inventory matching')
    parser.add_argument('--docupanda_id', type=str, required=True,
                       help='Document ID to process (required)')
    parser.add_argument('--save_to_db', action='store_true', default=True,
                       help='Save results to database (default: True)')
    parser.add_argument('--dry_run', action='store_true',
                       help='Run without saving to database (overrides --save_to_db)')
    
    args = parser.parse_args()
    
    # Handle dry run mode
    if args.dry_run:
        args.save_to_db = False
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🚀 Starting processing for docupanda_id: {args.docupanda_id}")
        logger.info(f"⚙️  Configuration: save_to_db={args.save_to_db}")
        
        results = process_receipt_items(args.docupanda_id, save_to_db=args.save_to_db)
        
        logger.info(f"✅ Processing completed successfully!")
        logger.info(f"📋 Processed {len(results)} items")
        
        if args.save_to_db:
            logger.info("💾 Results saved to database")
        else:
            logger.info("📄 Results not saved to database (dry run mode)")
            
    except Exception as e:
        logger.error(f"❌ Processing failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()