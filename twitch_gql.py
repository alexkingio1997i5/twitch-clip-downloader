import re
import httpx

CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"
GQL_URL = "https://gql.twitch.tv/gql"

class ClipNotFoundError(Exception):
    pass

def extract_slug(url_or_slug: str) -> str:
    url_or_slug = url_or_slug.strip()
    
    # Catches clips.twitch.tv/Slug or twitch.tv/channel/clip/Slug
    # Also handles trailing query params like ?filter=clips
    match = re.search(r"(?:clips\.twitch\.tv/|/clip/|^)([a-zA-Z0-9_-]+)(?:\?|$)", url_or_slug)
    if match:
        return match.group(1)
        
    return url_or_slug

def get_clip_data(slug_or_url: str) -> dict:
    """Fetch clip metadata and source download URLs from Twitch's GQL."""
    slug = extract_slug(slug_or_url)
    
    # Expanded query to pull game details for file naming downstream
    query = """
    query($slug: ID!) {
      clip(slug: $slug) {
        id
        title
        durationSeconds
        viewCount
        createdAt
        thumbnailURL
        game {
          name
        }
        broadcaster {
          displayName
          login
        }
        videoQualities {
          frameRate
          quality
          sourceURL
        }
      }
    }
    """
    
    headers = {
        "Client-ID": CLIENT_ID,
        # GQL interface blocks blank user agents intermittently
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    
    payload = {
        "query": query,
        "variables": {"slug": slug}
    }
    
    with httpx.Client(timeout=10.0) as client:
        resp = client.post(GQL_URL, json=payload, headers=headers)
        resp.raise_for_status()
        
        data = resp.json()
        # print(f"DEBUG raw GQL output: {data}")
        
        if "errors" in data and data["errors"]:
            raise ClipNotFoundError(f"Twitch GQL error: {data['errors'][0]['message']}")
            
        clip_data = data.get("data", {}).get("clip")
        if not clip_data:
            raise ClipNotFoundError(f"Clip '{slug}' not found on Twitch.")
            
        qualities = clip_data.get("videoQualities")
        if not qualities:
            raise ClipNotFoundError(f"No video streams available for clip '{slug}'.")
            
        return clip_data

def get_highest_quality_url(clip_data: dict) -> tuple[str, str]:
    # Sorts the videoQualities list to extract the absolute best quality feed
    qualities = clip_data.get("videoQualities", [])
    if not qualities:
        raise ValueError("No video qualities returned from metadata.")
        
    # TODO: Twitch sometimes serves a raw source with "source" as string. We force match it first.
    def sorting_rule(q):
        q_str = q.get("quality", "0")
        if q_str == "source":
            res_val = 9999
        else:
            try:
                res_val = int(re.sub(r"\D", "", q_str))
            except ValueError:
                res_val = 0
        
        fps = q.get("frameRate", 0)
        return (res_val, fps)

    best = max(qualities, key=sorting_rule)
    return best["sourceURL"], f"{best.get('quality')}p{best.get('frameRate')}"
