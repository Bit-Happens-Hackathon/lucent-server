#!/usr/bin/env python3
"""
Activity seeding script.

This script generates activity data for a user within a specified date range,
with random days skipped based on a frequency parameter.

Usage:
    python seed_activity.py <user_id> <start_date> <end_date> <frequency>

Example:
    python seed_activity.py user@example.com 2025-01-01 2025-04-01 0.2
    (This will create activity records for user@example.com from Jan 1 to Apr 1, 2025,
     with approximately 20% of days randomly skipped)
"""

import sys
import random
import asyncio
from datetime import datetime, timedelta, time
import os
import argparse
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_supabase_client
from app.api.activity.model import ActivityCreate
from app.api.activity.service import ActivityService


async def seed_user_activity(
    user_id: str,
    start_date_str: str,
    end_date_str: str,
    frequency: float = 0.0
):
    """
    Generate activity data for a user within a specified date range.
    
    Args:
        user_id (str): Email of the user
        start_date_str (str): Start date in format YYYY-MM-DD
        end_date_str (str): End date in format YYYY-MM-DD
        frequency (float): Probability (0.0 to 1.0) of skipping a day
                           0.0 means no days skipped, 1.0 means all days skipped
    
    Returns:
        int: Number of activity records created
    """
    try:
        # Parse dates
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        
        if start_date > end_date:
            print("Error: Start date must be before end date")
            return 0
        
        # Initialize Supabase client and service
        supabase = get_supabase_client()
        activity_service = ActivityService(supabase)
        
        # Keep track of created records
        created_count = 0
        
        # Generate activities for each day in the range
        current_date = start_date
        while current_date <= end_date:
            # Randomly skip days based on frequency
            if random.random() >= frequency:
                # Generate a random time for the login (between 8 AM and 10 PM)
                random_hour = random.randint(8, 22)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                
                login_datetime = datetime.combine(
                    current_date,
                    time(hour=random_hour, minute=random_minute, second=random_second)
                )
                
                # Create activity record
                activity = ActivityCreate(
                    user_id=user_id,
                    login=login_datetime
                )
                
                try:
                    await activity_service.create_activity(activity)
                    created_count += 1
                    print(f"Created activity for {user_id} on {login_datetime}")
                except Exception as e:
                    print(f"Error creating activity for {current_date}: {str(e)}")
            
            # Move to next day
            current_date += timedelta(days=1)
        
        print(f"\nSuccessfully created {created_count} activity records for {user_id}")
        return created_count
    
    except Exception as e:
        print(f"Error in seed_user_activity: {str(e)}")
        return 0


async def main():
    """
    Parse command line arguments and run the seeding function.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Seed user activity data")
    
    parser.add_argument("user_id", type=str, help="Email of the user")
    parser.add_argument("start_date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("end_date", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument(
        "frequency", 
        type=float, 
        help="Probability (0.0 to 1.0) of skipping a day"
    )
    
    args = parser.parse_args()
    
    # Validate frequency
    if not (0.0 <= args.frequency <= 1.0):
        print("Error: Frequency must be between 0.0 and 1.0")
        return
    
    # Run the seeding function
    await seed_user_activity(
        args.user_id,
        args.start_date,
        args.end_date,
        args.frequency
    )


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the async main function
    asyncio.run(main())