"""Fetch and save a webpage response."""

import argparse
from pathlib import Path
import re
from urllib.request import Request, urlopen
import ssl
import certifi
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime, timezone
from providers.untappd import resolve_menu_url

def fetch_url(url):
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")

    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    ssl_context = ssl.create_default_context(cafile=certifi.where())

    with urlopen(request, timeout=20, context=ssl_context) as response:
        content_type = response.headers.get("Content-Type", "")
        data = response.read()

    return content_type, data

def main():
    cli = argparse.ArgumentParser(
        description="Fetch a webpage and save the raw response."
    )

    cli.add_argument("url", help="Webpage URL")
    cli.add_argument(
    "--restaurant",
    required=True,
    help="Name of the restaurant"
)

    args = cli.parse_args()
    restaurant_id = re.sub(r"[^a-z0-9]+", "_", args.restaurant.lower()).strip("_")
    raw_dir = Path("data/raw") / restaurant_id
    raw_dir.mkdir(parents=True, exist_ok=True)

    try:
        resolved_url = resolve_menu_url(args.url)
        print(f"Fetching menu from: {resolved_url}")
        content_type, data = fetch_url(resolved_url)

        output_path = raw_dir / "menu_response"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_bytes(data)

        print(f"Content-Type: {content_type}")
        print(f"Saved {len(data):,} bytes to {output_path}")

    except (OSError, ValueError) as error:
        cli.error(str(error))

    saved_file = raw_dir / "menu_response"
    content = saved_file.read_text(encoding="utf-8")

    cleaned = content.replace(r"\/", "/").replace(r'\"', '"')
    cleaned = re.sub(r"\\n", "\n", cleaned)

    soup = BeautifulSoup(cleaned, "html.parser")

    beer_items = soup.select(".menu-item")
    print(f"Found {len(beer_items)} menu items")

    beers = []
    ingested_at = datetime.now(timezone.utc).isoformat()

    for item in beer_items:
        def get_text(selector):
            element = item.select_one(selector)
            return element.get_text(strip=True) if element else None


        beer = {
            "name": get_text(".item"),
            "brewery": get_text(".item-brewery"),
            "style": get_text(".item-category"),
            "location": get_text(".item-brewery-location"),
            "abv": get_text(".item-abv"),
            "description": get_text(".item-description"),
            "ibu": get_text(".item-ibu"),
            "ingested_at": ingested_at,
            "restaurant_name": args.restaurant,
            "source_url": args.url,
        }

        beers.append(beer)

    output_path = raw_dir / "menu_items.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(beers, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(beers)} menu items to {output_path}")

if __name__ == "__main__":
    main()