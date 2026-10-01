import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def fetch(url, retries=2):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            if attempt == retries:
                raise
            print(f'  Retry {url} ({e.code})')
            time.sleep(2)

def download_image(url, dest):
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            Path(dest).write_bytes(resp.read())
        return True
    except urllib.error.HTTPError as e:
        print(f'  Failed to download image {url}: {e.code}')
        return False

def get_last_page(html):
    pages = set()
    for m in re.finditer(r'/adoptions/page/(\d+)/', html):
        pages.add(int(m.group(1)))
    return max(pages) if pages else 1

def parse_cards(list_html):
    cards = []
    for m in re.finditer(r'<div class="pet_post([^"]*)"[^>]*>(.*?)<!-- end \.pet -->', list_html, re.S):
        classes = m.group(1)
        card = m.group(2)

        # species from class
        species = 'cat'
        if 'pet-category-dogs' in classes:
            species = 'dog'

        # slug and pet URL
        url_match = re.search(r'<a href="(https://pawsandclaws\.org\.au/pet/([^/]+)/)"', card)
        if not url_match:
            continue
        pet_url, slug = url_match.group(1), url_match.group(2)

        # name
        name_match = re.search(r'<h3 class="pet-title[^"]*"[^>]*>.*?<a[^>]*>(.*?)</a>', card, re.S)
        if not name_match:
            continue
        name = html.unescape(re.sub(r'<[^>]+>', '', name_match.group(1)).strip())

        # image
        img_match = re.search(r'<img[^>]+class="[^"]*wp-post-image[^"]*"[^>]+src="([^"]+)"', card)
        if not img_match:
            img_match = re.search(r'<img[^>]+src="([^"]+)"[^>]*class="[^"]*wp-post-image[^"]*"', card)
        photo_url = img_match.group(1) if img_match else None

        # DOB and sex from excerpt
        excerpt_match = re.search(r'<div class="tmnf_excerpt"[^>]*>.*?<p>(.*?)</p>', card, re.S)
        dob, sex = '', ''
        if excerpt_match:
            excerpt = html.unescape(re.sub(r'<[^>]+>', '', excerpt_match.group(1)))
            dm = re.search(r'Approx DOB:\s*([^|]+)\|\s*([^|]+)', excerpt)
            if dm:
                dob = dm.group(1).strip()
                sex = dm.group(2).strip()

        cards.append({
            'slug': slug,
            'name': name,
            'pet_url': pet_url,
            'species': species,
            'dob': dob,
            'sex': sex,
            'photo_url': photo_url,
        })
    return cards

def parse_pet_description(pet_html):
    # Grab the main description from the pet detail page
    entry_match = re.search(r'<div class="entry tmnf_entry"[^>]*>(.*?)</div>\s*<div class="clearfix">', pet_html, re.S)
    if not entry_match:
        entry_match = re.search(r'<div class="entry"[^>]*>(.*?)</div>', pet_html, re.S)
    if entry_match:
        entry = entry_match.group(1)
        # strip galleries/figures and images before removing tags
        entry = re.sub(r'<figure[^>]*>.*?</figure>', ' ', entry, flags=re.S)
        text = re.sub(r'<[^>]+>', ' ', entry, flags=re.S)
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    return ''

def main():
    base_url = 'https://pawsandclaws.org.au/adoptions/'
    print('Fetching adoptions page 1...')
    first_html = fetch(base_url)
    last_page = get_last_page(first_html)
    print(f'Found {last_page} adoptions pages')

    all_cards = parse_cards(first_html)
    for page in range(2, last_page + 1):
        url = f'https://pawsandclaws.org.au/adoptions/page/{page}/'
        print(f'Fetching page {page}...')
        html_text = fetch(url)
        all_cards.extend(parse_cards(html_text))
        time.sleep(0.5)

    print(f'Found {len(all_cards)} animals')

    animals = []
    for i, card in enumerate(all_cards, 1):
        print(f'[{i}/{len(all_cards)}] {card["name"]}')
        try:
            pet_html = fetch(card['pet_url'])
            description = parse_pet_description(pet_html)
        except Exception as e:
            print(f'  Could not fetch pet page for {card["name"]}: {e}')
            description = ''

        # download image
        local_photo = None
        if card['photo_url']:
            parsed = urllib.parse.urlparse(card['photo_url'])
            ext = Path(parsed.path).suffix
            if not ext:
                ext = '.jpg'
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', card['slug'])
            local_photo = f'images/{safe_name}{ext}'
            success = download_image(card['photo_url'], local_photo)
            if not success:
                local_photo = card['photo_url']  # fallback to remote URL
        else:
            local_photo = 'images/Screenshot-2022-12-28-at-22.14.52.png'

        animals.append({
            'id': card['slug'],
            'name': card['name'],
            'slug': card['slug'],
            'species': card['species'],
            'sex': card['sex'],
            'dob': card['dob'],
            'status': 'available',
            'photo': local_photo,
            'description': description,
        })
        time.sleep(0.5)

    Path('data/animals.json').write_text(json.dumps(animals, indent=2) + '\n')
    print(f'Wrote {len(animals)} animals to data/animals.json')

if __name__ == '__main__':
    main()
