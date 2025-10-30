#!/usr/bin/env python3
"""
Test database connection and basic queries.
Run this to verify database is accessible.
"""
import asyncio
import sys


async def test_database_connection():
    """Test database connection and schema."""
    print("Testing database connection...")

    try:
        from src.database import get_db

        db = await get_db()
        print("  Connected to database successfully")

        # Test papers table
        cursor = await db.execute("SELECT COUNT(*) as count FROM papers")
        row = await cursor.fetchone()
        papers_count = row["count"]
        print(f"  Papers table: {papers_count} rows")

        # Test paper_author_affiliations table
        cursor = await db.execute("SELECT COUNT(*) as count FROM paper_author_affiliations")
        row = await cursor.fetchone()
        affiliations_count = row["count"]
        print(f"  Paper-author-affiliations table: {affiliations_count} rows")

        # Test paper_references table
        cursor = await db.execute("SELECT COUNT(*) as count FROM paper_references")
        row = await cursor.fetchone()
        references_count = row["count"]
        print(f"  Paper-references table: {references_count} rows")

        # Test year range
        cursor = await db.execute("SELECT MIN(year) as min_year, MAX(year) as max_year FROM papers")
        row = await cursor.fetchone()
        print(f"  Year range: {row['min_year']} - {row['max_year']}")

        # Test 2020-2022 papers
        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM papers WHERE year >= 2020 AND year <= 2022"
        )
        row = await cursor.fetchone()
        recent_count = row["count"]
        print(f"  Papers (2020-2022): {recent_count} rows")

        await db.close()

        print("\nDatabase connection test completed successfully!")
        return True

    except Exception as e:
        print(f"\nDatabase connection test FAILED: {e}")
        print("\nMake sure the database file exists at: data/sciscinet_vt_cs.db")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_database_connection())
    sys.exit(0 if success else 1)
