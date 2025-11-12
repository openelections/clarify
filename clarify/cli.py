#!/usr/bin/env python
"""
Command-line interface for Clarify election results parser
"""
import argparse
import json
import sys
import os
import zipfile
from io import StringIO

import requests

from .jurisdiction import Jurisdiction
from .parser import Parser


def cmd_jurisdiction(args):
    """Handle the jurisdiction command to discover URLs"""
    try:
        j = Jurisdiction(url=args.url, level=args.level)

        print(f"\nJurisdiction: {j.name or args.level}")
        print(f"URL: {j.url}")
        print(f"Level: {j.level}")

        # Get report URLs
        for fmt in ['xml', 'txt', 'xls']:
            report_url = j.report_url(fmt)
            if report_url:
                print(f"{fmt.upper()} Report: {report_url}")

        # Get subjurisdictions if requested
        if args.subs:
            print("\nSubjurisdictions:")
            subs = j.get_subjurisdictions()
            if subs:
                for sub in subs:
                    print(f"  - {sub.name}: {sub.url}")
                    if args.verbose:
                        xml_url = sub.report_url('xml')
                        if xml_url:
                            print(f"    XML: {xml_url}")
            else:
                print("  No subjurisdictions found")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_download(args):
    """Download election results file"""
    try:
        j = Jurisdiction(url=args.url, level=args.level)

        # Get the report URL
        report_url = j.report_url(args.format)
        if not report_url:
            print(f"Error: No {args.format} report found at this URL", file=sys.stderr)
            return 1

        # Determine output filename
        if args.output:
            output_fn = args.output
        else:
            # Create a default filename
            output_fn = f"results_{j.level}.{args.format}.zip"

        print(f"Downloading from {report_url}")
        print(f"Saving to {output_fn}")

        j.download_report(args.format, output_fn)
        print("Download complete!")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_parse(args):
    """Parse election results XML file"""
    try:
        p = Parser()

        # Parse the file - could be XML or ZIP
        if args.file.endswith('.zip'):
            p.parse_zip(args.file)
        else:
            p.parse(args.file)

        # Output based on format
        if args.format == 'json':
            output_json(p, args)
        elif args.format == 'csv':
            output_csv(p, args)
        else:  # summary (default)
            output_summary(p, args)

    except Exception as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    return 0


def output_summary(parser, args):
    """Output a human-readable summary"""
    print(f"\nElection: {parser.election_name}")
    print(f"Date: {parser.election_date}")
    print(f"Region: {parser.region}")
    print(f"Timestamp: {parser.timestamp}")
    print(f"\nTotal Voters: {parser.total_voters:,}")
    print(f"Ballots Cast: {parser.ballots_cast:,}")
    print(f"Voter Turnout: {parser.voter_turnout:.2f}%")

    print(f"\nContests: {len(parser.contests)}")
    print(f"Result Jurisdictions: {len(parser.result_jurisdictions)}")

    if args.verbose:
        print("\n" + "="*80)
        print("CONTESTS")
        print("="*80)
        for contest in parser.contests:
            print(f"\n{contest.text}")
            print(f"  Key: {contest.key}")
            print(f"  Vote for: {contest.vote_for}")
            print(f"  Precincts reporting: {contest.precincts_reporting}")

            if args.show_candidates:
                print(f"  Choices:")
                for choice in contest.choices:
                    print(f"    - {choice.text}: {choice.total_votes:,} votes")
                    if choice.party:
                        print(f"      Party: {choice.party}")


def output_json(parser, args):
    """Output results as JSON"""
    data = {
        'election_name': parser.election_name,
        'election_date': str(parser.election_date),
        'region': parser.region,
        'timestamp': str(parser.timestamp),
        'total_voters': parser.total_voters,
        'ballots_cast': parser.ballots_cast,
        'voter_turnout': parser.voter_turnout,
        'contests': []
    }

    # Add contests
    for contest in parser.contests:
        contest_data = {
            'key': contest.key,
            'text': contest.text,
            'vote_for': contest.vote_for,
            'is_question': contest.is_question,
            'precincts_reporting': contest.precincts_reporting,
            'precincts_participating': contest.precincts_participating,
            'precincts_reported': contest.precincts_reported,
            'counties_participating': contest.counties_participating,
            'counties_reported': contest.counties_reported,
            'choices': []
        }

        # Add choices
        for choice in contest.choices:
            choice_data = {
                'key': choice.key,
                'text': choice.text,
                'party': choice.party,
                'total_votes': choice.total_votes,
            }

            if args.include_results:
                choice_data['results'] = []
                for result in choice.results:
                    result_data = {
                        'vote_type': result.vote_type,
                        'votes': result.votes,
                        'jurisdiction': result.jurisdiction.name if result.jurisdiction else None
                    }
                    choice_data['results'].append(result_data)

            contest_data['choices'].append(choice_data)

        data['contests'].append(contest_data)

    # Add jurisdictions if requested
    if args.include_jurisdictions:
        data['jurisdictions'] = []
        for jurisdiction in parser.result_jurisdictions:
            data['jurisdictions'].append({
                'name': jurisdiction.name,
                'level': jurisdiction.level,
                'total_voters': jurisdiction.total_voters,
                'ballots_cast': jurisdiction.ballots_cast,
                'voter_turnout': jurisdiction.voter_turnout,
                'percent_reporting': jurisdiction.percent_reporting
            })

    print(json.dumps(data, indent=2))


def output_csv(parser, args):
    """Output results as CSV"""
    import csv

    # Write to stdout
    writer = csv.writer(sys.stdout)

    # Header
    writer.writerow([
        'contest_key', 'contest_text', 'choice_key', 'choice_text',
        'party', 'vote_type', 'jurisdiction', 'votes'
    ])

    # Data rows
    for contest in parser.contests:
        for choice in contest.choices:
            for result in choice.results:
                writer.writerow([
                    contest.key,
                    contest.text,
                    choice.key,
                    choice.text,
                    choice.party or '',
                    result.vote_type,
                    result.jurisdiction.name if result.jurisdiction else 'Total',
                    result.votes
                ])


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Clarify - Parse election results from Clarity systems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get jurisdiction info and report URLs
  clarify jurisdiction --url "http://results.enr.clarityelections.com/GA/63991/184321/en/summary.html" --level state

  # Download XML results
  clarify download --url "http://results.enr.clarityelections.com/GA/63991/184321/en/summary.html" --level state --format xml

  # Parse results from a zip file
  clarify parse results.xml.zip

  # Parse and output as JSON
  clarify parse results.xml.zip --format json

  # Parse and output as CSV
  clarify parse results.xml.zip --format csv > results.csv
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Jurisdiction command
    jurisdiction_parser = subparsers.add_parser(
        'jurisdiction',
        help='Get information about a jurisdiction and discover report URLs'
    )
    jurisdiction_parser.add_argument(
        '--url',
        required=True,
        help='Clarity election results URL'
    )
    jurisdiction_parser.add_argument(
        '--level',
        required=True,
        choices=['state', 'county', 'city', 'precinct'],
        help='Jurisdiction level'
    )
    jurisdiction_parser.add_argument(
        '--subs',
        action='store_true',
        help='List subjurisdictions (e.g., counties within a state)'
    )
    jurisdiction_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    # Download command
    download_parser = subparsers.add_parser(
        'download',
        help='Download election results file'
    )
    download_parser.add_argument(
        '--url',
        required=True,
        help='Clarity election results URL'
    )
    download_parser.add_argument(
        '--level',
        required=True,
        choices=['state', 'county', 'city', 'precinct'],
        help='Jurisdiction level'
    )
    download_parser.add_argument(
        '--format',
        choices=['xml', 'txt', 'xls'],
        default='xml',
        help='Report format to download (default: xml)'
    )
    download_parser.add_argument(
        '-o', '--output',
        help='Output filename (default: auto-generated)'
    )

    # Parse command
    parse_parser = subparsers.add_parser(
        'parse',
        help='Parse election results XML file'
    )
    parse_parser.add_argument(
        'file',
        help='XML or ZIP file containing election results'
    )
    parse_parser.add_argument(
        '--format',
        choices=['summary', 'json', 'csv'],
        default='summary',
        help='Output format (default: summary)'
    )
    parse_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output (for summary format)'
    )
    parse_parser.add_argument(
        '--show-candidates',
        action='store_true',
        help='Show candidate names and vote totals (for summary format)'
    )
    parse_parser.add_argument(
        '--include-results',
        action='store_true',
        help='Include detailed results by jurisdiction (for JSON format)'
    )
    parse_parser.add_argument(
        '--include-jurisdictions',
        action='store_true',
        help='Include jurisdiction information (for JSON format)'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate command handler
    if args.command == 'jurisdiction':
        return cmd_jurisdiction(args)
    elif args.command == 'download':
        return cmd_download(args)
    elif args.command == 'parse':
        return cmd_parse(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
