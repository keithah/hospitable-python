#!/usr/bin/env python3
"""
Example usage of the Hospitable Python SDK
"""

import os
from datetime import datetime, timedelta
from hospitable import HospitableClient
from hospitable.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ForbiddenError,
)


def main():
    """Example usage of the Hospitable SDK"""
    
    # Initialize client (set HOSPITABLE_TOKEN environment variable)
    try:
        client = HospitableClient()
        print("✓ Client initialized successfully")
    except ValueError as e:
        print(f"✗ Client initialization failed: {e}")
        print("Please set HOSPITABLE_TOKEN environment variable")
        return
    
    try:
        # Test authentication by getting user info
        user = client.user.get()
        print(f"✓ Authenticated as: {user.name} ({user.email})")
        
        # Get properties
        properties = client.properties.list(per_page=5)
        print(f"✓ Found {len(properties.data)} properties")
        
        if not properties.data:
            print("No properties found - cannot continue with examples")
            return
        
        # Get first property details
        property_uuid = properties.data[0].id
        property_name = properties.data[0].name
        print(f"✓ Using property: {property_name}")
        
        # Get property calendar
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        calendar = client.properties.get_calendar(
            property_uuid,
            start_date=start_date,
            end_date=end_date
        )
        print(f"✓ Retrieved calendar: {len(calendar.days)} days")
        
        # Get reservations for this property
        reservations = client.reservations.list(
            properties=[property_uuid],
            start_date=start_date,
            end_date=end_date,
            per_page=5
        )
        print(f"✓ Found {len(reservations.data)} upcoming reservations")
        
        # Get reviews for the property
        reviews = client.reviews.list(property_uuid, per_page=3)
        print(f"✓ Found {len(reviews.data)} reviews")
        
        # Example calendar update (commented out to avoid modifying real data)
        """
        update_result = client.properties.update_calendar(
            property_uuid,
            [
                {
                    "date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
                    "price": {"amount": 15000},  # $150.00
                    "available": True,
                    "min_stay": 2
                }
            ]
        )
        print(f"✓ Calendar update: {update_result.status}")
        """
        
        print("\n🎉 All tests passed! The SDK is working correctly.")
        
    except AuthenticationError:
        print("✗ Authentication failed - check your token")
    except RateLimitError as e:
        print(f"✗ Rate limited - retry after {e.retry_after} seconds")
    except ValidationError as e:
        print(f"✗ Validation error: {e.message}")
    except NotFoundError:
        print("✗ Resource not found")
    except ForbiddenError:
        print("✗ Insufficient permissions")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    finally:
        # Clean up
        client.close()


if __name__ == "__main__":
    main()