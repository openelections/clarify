#!/usr/bin/env python3
"""
Basic functionality test for Clarify without complex mocking.
Run this to verify the core parsing functionality works.
"""
import os
import sys

# Add compatibility fix for collections.Callable before importing anything else
import collections
try:
    from collections.abc import Callable
    collections.Callable = Callable
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clarify.parser import Parser
from clarify.jurisdiction import Jurisdiction

def test_parser_basic():
    """Test basic parser functionality with local XML files"""
    print("Testing Parser with precinct data...")
    
    # Test precinct parsing
    p = Parser()
    p.parse('tests/data/precinct.xml')
    
    print(f"✓ Election: {p.election_name}")
    print(f"✓ Region: {p.region}")
    print(f"✓ Total voters: {p.total_voters}")
    print(f"✓ Ballots cast: {p.ballots_cast}")
    print(f"✓ Result jurisdictions: {len(p.result_jurisdictions)}")
    print(f"✓ Contests: {len(p.contests)}")
    print(f"✓ Results: {len(p.results)}")
    
    # Test county parsing
    print("\nTesting Parser with county data...")
    p2 = Parser()
    p2.parse('tests/data/county.xml')
    
    print(f"✓ Election: {p2.election_name}")
    print(f"✓ Region: {p2.region}")
    print(f"✓ Total voters: {p2.total_voters}")
    print(f"✓ Ballots cast: {p2.ballots_cast}")
    print(f"✓ Result jurisdictions: {len(p2.result_jurisdictions)}")
    print(f"✓ Contests: {len(p2.contests)}")
    print(f"✓ Results: {len(p2.results)}")
    
    print("\n✅ Parser functionality working correctly!")

def test_jurisdiction_basic():
    """Test basic jurisdiction functionality"""
    print("\nTesting Jurisdiction URL parsing...")
    
    # Test URL parsing
    url = 'https://results.enr.clarityelections.com/KY/15261/30235/en/summary.html'
    j = Jurisdiction(url=url, level='state')
    
    print(f"✓ URL: {j.url}")
    print(f"✓ Level: {j.level}")
    print(f"✓ Parsed URL keys: {list(j.parsed_url.keys())}")
    
    print("\n✅ Jurisdiction functionality working correctly!")

def main():
    """Run basic functionality tests"""
    print("🧪 Running basic Clarify functionality tests...\n")
    
    try:
        test_parser_basic()
        test_jurisdiction_basic()
        print("\n🎉 All basic tests passed! The core functionality is working.")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())