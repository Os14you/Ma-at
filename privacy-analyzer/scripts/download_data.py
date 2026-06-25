import os
import urllib.request

domains = [
    "facebook.com", "twitter.com", "instagram.com", "linkedin.com", "reddit.com",
    "tiktok.com", "snapchat.com", "pinterest.com", "tumblr.com", "google.com",
    "yahoo.com", "outlook.com", "aol.com", "whatsapp.com", "discord.com",
    "slack.com", "zoom.us", "github.com", "stackoverflow.com", "medium.com"
]

def download_policies():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_path, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    base_url = "https://raw.githubusercontent.com/citp/privacy-policy-historical/master/"
    
    print(f"Downloading policies into {data_dir}...")
    for domain in domains:
        clean_domain = domain.replace('www.', '').lower()

        path = f"{clean_domain[0]}/{clean_domain[0:2]}/{clean_domain[0:3]}/{clean_domain}.md"
        url = base_url + path
        file_path = os.path.join(data_dir, f"{clean_domain}.md")
        
        try:
            print(f"Fetching {url} -> {file_path} ...")
            urllib.request.urlretrieve(url, file_path)
            print(f"Successfully downloaded: {domain}")
        except Exception as e:
            print(f"Failed to download {domain}: {e}")

if __name__ == "__main__":
    download_policies()
