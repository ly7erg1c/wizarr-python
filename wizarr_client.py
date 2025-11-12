#!/usr/bin/env python3
"""
Wizarr API Client for batch invitation creation.

This module provides functionality to create invitations in batches
with various configuration options.
"""

import argparse
import json
import sys
from typing import Dict, List, Optional, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class WizarrClient:
    """Client for interacting with the Wizarr API.
    
    Args:
        base_url: Base URL of the Wizarr API (default: https://invite.rarbg.zip)
        api_key: API key for authentication
    """
    
    def __init__(self, base_url: str = "https://invite.rarbg.zip", api_key: str = None):
        # Add https:// scheme if not provided
        if not base_url.startswith(('http://', 'https://')):
            base_url = f'https://{base_url}'
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        if self.api_key:
            self.session.headers.update({
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            })
    
    def create_invitation(
        self,
        server_ids: List[int],
        expires_in_days: Optional[int] = None,
        duration: str = "unlimited",
        unlimited: bool = True,
        library_ids: Optional[List[int]] = None,
        allow_downloads: bool = False,
        allow_live_tv: bool = False,
        allow_mobile_uploads: bool = False
    ) -> Dict[str, Any]:
        """Create a single invitation.
        
        Args:
            server_ids: Array of server IDs (required)
            expires_in_days: Days until invitation expires (1, 7, 30, or None)
            duration: User access duration in days or "unlimited"
            unlimited: Whether user access is unlimited
            library_ids: Array of library IDs to grant access to
            allow_downloads: Allow user downloads
            allow_live_tv: Allow live TV access
            allow_mobile_uploads: Allow mobile uploads
            
        Returns:
            Dictionary containing the invitation response
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/invitations"
        
        payload = {
            "server_ids": server_ids,
            "duration": duration,
            "unlimited": unlimited,
            "allow_downloads": allow_downloads,
            "allow_live_tv": allow_live_tv,
            "allow_mobile_uploads": allow_mobile_uploads
        }
        
        # Add optional fields only if they are provided
        if expires_in_days is not None:
            payload["expires_in_days"] = expires_in_days
        
        if library_ids is not None:
            payload["library_ids"] = library_ids
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def create_invitations_batch(
        self,
        count: int,
        server_ids: List[int],
        expires_in_days: Optional[int] = None,
        duration: str = "unlimited",
        unlimited: bool = True,
        library_ids: Optional[List[int]] = None,
        allow_downloads: bool = False,
        allow_live_tv: bool = False,
        allow_mobile_uploads: bool = False,
        stop_on_error: bool = False
    ) -> List[Dict[str, Any]]:
        """Create multiple invitations in batch.
        
        Args:
            count: Number of invitations to create
            server_ids: Array of server IDs (required)
            expires_in_days: Days until invitation expires (1, 7, 30, or None)
            duration: User access duration in days or "unlimited"
            unlimited: Whether user access is unlimited
            library_ids: Array of library IDs to grant access to
            allow_downloads: Allow user downloads
            allow_live_tv: Allow live TV access
            allow_mobile_uploads: Allow mobile uploads
            stop_on_error: If True, stop batch creation on first error
            
        Returns:
            List of dictionaries containing invitation responses
        """
        results = []
        errors = []
        
        for i in range(count):
            try:
                result = self.create_invitation(
                    server_ids=server_ids,
                    expires_in_days=expires_in_days,
                    duration=duration,
                    unlimited=unlimited,
                    library_ids=library_ids,
                    allow_downloads=allow_downloads,
                    allow_live_tv=allow_live_tv,
                    allow_mobile_uploads=allow_mobile_uploads
                )
                results.append({
                    "success": True,
                    "index": i + 1,
                    "data": result
                })
                print(f"✓ Created invitation {i + 1}/{count}", file=sys.stderr)
            except requests.exceptions.RequestException as e:
                error_info = {
                    "success": False,
                    "index": i + 1,
                    "error": str(e)
                }
                errors.append(error_info)
                print(f"✗ Failed to create invitation {i + 1}/{count}: {e}", file=sys.stderr)
                
                if stop_on_error:
                    break
        
        return {
            "results": results,
            "errors": errors,
            "total": count,
            "successful": len(results),
            "failed": len(errors)
        }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Wizarr API Client - Batch invitation creation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create 5 invitations (outputs only URLs by default)
  python wizarr_client.py --api-key YOUR_KEY --count 5 --server-ids 1 2

  # Create invitations with detailed JSON output
  python wizarr_client.py --api-key YOUR_KEY --count 10 \\
    --server-ids 1 --expires-in-days 7 --duration 30 \\
    --allow-downloads --allow-live-tv --verbose

  # Create invitations from JSON config file
  python wizarr_client.py --api-key YOUR_KEY --config config.json

  # Save only URLs to a file
  python wizarr_client.py --api-key YOUR_KEY --count 5 \\
    --server-ids 1 --output urls.txt
        """
    )
    
    # API configuration
    parser.add_argument(
        '--api-key',
        required=True,
        help='API key for authentication'
    )
    parser.add_argument(
        '--base-url',
        default='https://invite.rarbg.zip',
        help='Base URL of the Wizarr API (default: https://invite.rarbg.zip)'
    )
    
    # Batch creation options
    parser.add_argument(
        '--count',
        type=int,
        help='Number of invitations to create (required if --config not used)'
    )
    parser.add_argument(
        '--config',
        help='Path to JSON configuration file (alternative to command-line options)'
    )
    
    # Invitation parameters
    parser.add_argument(
        '--server-ids',
        nargs='+',
        type=int,
        help='Array of server IDs (required)'
    )
    parser.add_argument(
        '--expires-in-days',
        type=int,
        choices=[1, 7, 30],
        help='Days until invitation expires (1, 7, or 30)'
    )
    parser.add_argument(
        '--duration',
        default='unlimited',
        help='User access duration in days or "unlimited" (default: unlimited)'
    )
    parser.add_argument(
        '--no-unlimited',
        action='store_false',
        dest='unlimited',
        help='Disable unlimited user access (default: unlimited)'
    )
    parser.add_argument(
        '--library-ids',
        nargs='+',
        type=int,
        help='Array of library IDs to grant access to'
    )
    parser.add_argument(
        '--allow-downloads',
        action='store_true',
        help='Allow user downloads'
    )
    parser.add_argument(
        '--allow-live-tv',
        action='store_true',
        help='Allow live TV access'
    )
    parser.add_argument(
        '--allow-mobile-uploads',
        action='store_true',
        help='Allow mobile uploads'
    )
    
    # Batch options
    parser.add_argument(
        '--stop-on-error',
        action='store_true',
        help='Stop batch creation on first error'
    )
    
    # Output options
    parser.add_argument(
        '--output',
        help='Output file path for results'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Output detailed JSON results instead of just invitation URLs'
    )
    
    args = parser.parse_args()
    
    # Load config from file if provided
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        # Override with command-line args if provided
        count = args.count or config.get('count', 1)
        server_ids = args.server_ids or config.get('server_ids')
        expires_in_days = args.expires_in_days if args.expires_in_days is not None else config.get('expires_in_days')
        duration = args.duration if args.duration != 'unlimited' else config.get('duration', 'unlimited')
        unlimited = args.unlimited if 'unlimited' in vars(args) else config.get('unlimited', True)
        library_ids = args.library_ids or config.get('library_ids')
        allow_downloads = args.allow_downloads or config.get('allow_downloads', False)
        allow_live_tv = args.allow_live_tv or config.get('allow_live_tv', False)
        allow_mobile_uploads = args.allow_mobile_uploads or config.get('allow_mobile_uploads', False)
    else:
        if not args.count:
            parser.error("--count is required when --config is not used")
        if not args.server_ids:
            parser.error("--server-ids is required")
        
        count = args.count
        server_ids = args.server_ids
        expires_in_days = args.expires_in_days
        duration = args.duration
        unlimited = args.unlimited
        library_ids = args.library_ids
        allow_downloads = args.allow_downloads
        allow_live_tv = args.allow_live_tv
        allow_mobile_uploads = args.allow_mobile_uploads
    
    # Create client
    client = WizarrClient(base_url=args.base_url, api_key=args.api_key)
    
    # Create invitations
    if not args.quiet:
        print(f"Creating {count} invitation(s)...", file=sys.stderr)
    
    result = client.create_invitations_batch(
        count=count,
        server_ids=server_ids,
        expires_in_days=expires_in_days,
        duration=duration,
        unlimited=unlimited,
        library_ids=library_ids,
        allow_downloads=allow_downloads,
        allow_live_tv=allow_live_tv,
        allow_mobile_uploads=allow_mobile_uploads,
        stop_on_error=args.stop_on_error
    )
    
    # Output results
    if args.verbose:
        # Output full JSON structure
        output = json.dumps(result, indent=2)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            if not args.quiet:
                print(f"\nResults saved to {args.output}", file=sys.stderr)
        else:
            print(output)
    else:
        # Output only invitation URLs (one per line)
        urls = []
        for res in result['results']:
            if res['success'] and 'invitation' in res['data']:
                invitation = res['data']['invitation']
                if 'url' in invitation:
                    urls.append(invitation['url'])
        
        output = '\n'.join(urls)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
                if urls:
                    f.write('\n')  # Add trailing newline
            if not args.quiet:
                print(f"\n{len(urls)} invitation URL(s) saved to {args.output}", file=sys.stderr)
        else:
            if urls:
                print(output)
    
    # Exit with error code if any failures
    if result['failed'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()

