import re

def resolve_menu_url(url):
    pattern = r"/embeds/iframes/(\d+)/(\d+)"
    match = re.search(pattern, url)

    if match:
        location_id, theme_id = match.groups()

        return (
            f"https://business.untappd.com/locations/"
            f"{location_id}/themes/{theme_id}/js"
        )
    return url
