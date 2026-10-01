import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Ensure the animal database exists
# ---------------------------------------------------------------------------
Path('data').mkdir(exist_ok=True)
data_file = Path('data/animals.json')

if not data_file.exists():
    sample_animals = [
        {
            "id": "misty",
            "name": "Misty",
            "slug": "misty",
            "species": "cat",
            "sex": "Girl",
            "dob": "27/07/25",
            "status": "available",
            "photo": "images/Screenshot-2022-12-28-at-22.14.52.png",
            "description": "Misty is a curious and affectionate kitten looking for a forever home. She loves to play and curl up in a sunny spot."
        },
        {
            "id": "maya",
            "name": "Maya",
            "slug": "maya",
            "species": "cat",
            "sex": "Girl",
            "dob": "7/7/23",
            "status": "available",
            "photo": "images/Screenshot-2022-12-28-at-22.14.52.png",
            "description": "Maya is a calm and loving young cat who enjoys quiet company and gentle pats."
        },
        {
            "id": "ember",
            "name": "Ember",
            "slug": "ember",
            "species": "cat",
            "sex": "Girl",
            "dob": "07/05/2026",
            "status": "available",
            "photo": "images/Screenshot-2022-12-28-at-22.14.52.png",
            "description": "Ember is a friendly and energetic kitten who is always ready for a play session."
        },
        {
            "id": "blaze",
            "name": "Blaze",
            "slug": "blaze",
            "species": "cat",
            "sex": "Girl",
            "dob": "07/05/2026",
            "status": "available",
            "photo": "images/Screenshot-2022-12-28-at-22.14.52.png",
            "description": "Blaze is a sweet and social kitten who gets along well with people and other cats."
        },
        {
            "id": "mazie",
            "name": "Mazie",
            "slug": "mazie",
            "species": "cat",
            "sex": "Girl",
            "dob": "24/04/26",
            "status": "available",
            "photo": "images/Screenshot-2022-12-28-at-22.14.52.png",
            "description": "Mazie is a sweet little girl with a calm, gentle nature. She loves nothing more than finding a cozy spot for a nap and watching the world go by. When she's awake, she enjoys a cuddle and some quiet company, making her the perfect companion for someone looking for a relaxed kitten."
        }
    ]
    data_file.write_text(json.dumps(sample_animals, indent=2) + '\n')
    print('Created data/animals.json with sample animals')

animals = json.loads(data_file.read_text())

# ---------------------------------------------------------------------------
# 2. Read the shared header and footer from index.html
# ---------------------------------------------------------------------------
base = Path('index.html').read_text()
header_start = base.find('<!-- Header -->')
header_end = base.find('    <!-- Hero -->')
footer_start = base.find('    <!-- Footer -->')
body_end = base.find('</body>')

base_header = base[header_start:header_end]
base_footer = base[footer_start:body_end]

# ---------------------------------------------------------------------------
# 3. Add an "Adoptable pets" link to the shared header if not already present
# ---------------------------------------------------------------------------
if 'Adoptable pets' not in base_header:
    base_header = base_header.replace(
        '<a href="adoption.html" class="block px-4 py-2.5 text-sm text-gray-700 hover:bg-paw-50 hover:text-paw-600">Adopt</a>',
        '<a href="adoptions/" class="block px-4 py-2.5 text-sm text-gray-700 hover:bg-paw-50 hover:text-paw-600">Adoptable pets</a>\n              <a href="adoption.html" class="block px-4 py-2.5 text-sm text-gray-700 hover:bg-paw-50 hover:text-paw-600">Adopt</a>'
    )
    base_header = base_header.replace(
        '<a href="adoption.html" class="rounded-lg px-3 py-2 pl-6 hover:bg-paw-50 hover:text-paw-600">Adopt</a>',
        '<a href="adoptions/" class="rounded-lg px-3 py-2 pl-6 hover:bg-paw-50 hover:text-paw-600">Adoptable pets</a>\n          <a href="adoption.html" class="rounded-lg px-3 py-2 pl-6 hover:bg-paw-50 hover:text-paw-600">Adopt</a>'
    )
    print('Added Adoptable pets link to header')

# ---------------------------------------------------------------------------
# 4. Apply the updated header to every existing .html page and fix links
# ---------------------------------------------------------------------------
for path in Path('.').glob('*.html'):
    content = path.read_text()
    content = re.sub(r'<header class="sticky.*?</header>', base_header, content, flags=re.DOTALL, count=1)
    content = re.sub(r'<!-- Footer -->.*?</body>', base_footer, content, flags=re.DOTALL, count=1)
    content = content.replace('https://pawsandclaws.org.au/adoptions/', 'adoptions/')
    content = content.replace('href="adoption.html"', 'href="adoptions/"')
    path.write_text(content)
    print(f'Updated header, footer and links: {path.name}')

def build_page_header(title, desc):
    h = base_header.replace('<title>Paws and Claws Animal Shelter | Port Douglas</title>', f'<title>{title}</title>', 1)
    h = h.replace('content="Paws and Claws Animal Shelter is a non-profit, no-kill dog and cat rescue organisation based in Port Douglas, Queensland."', f'content="{desc}"', 1)
    return h

# ---------------------------------------------------------------------------
# 5. Generate adoptions listing page
# ---------------------------------------------------------------------------
Path('adoptions').mkdir(exist_ok=True)

cards = '\n'.join(
    f'''        <a href="pet/{a["slug"]}/" data-species="{a["species"]}" class="adoption-card group block overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-gray-100 transition hover:shadow-lg">
          <div class="aspect-[4/5] overflow-hidden bg-gray-100">
            <img src="{a["photo"]}" alt="{a["name"]}" class="h-full w-full object-cover transition duration-500 group-hover:scale-105" />
          </div>
          <div class="p-6">
            <p class="text-xs font-semibold uppercase tracking-wider text-paw-600">{a["species"].capitalize()}</p>
            <h3 class="mt-1 text-2xl font-bold text-gray-900">{a["name"]}</h3>
            <p class="mt-2 text-sm text-gray-600">Approx DOB: {a["dob"]} | {a["sex"]}</p>
            <p class="mt-3 text-sm text-gray-600 line-clamp-3">{a["description"]}</p>
            <span class="mt-4 inline-flex items-center gap-2 font-semibold text-paw-600 group-hover:text-paw-700">Learn more <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" /></svg></span>
          </div>
        </a>'''
    for a in animals
)

adoptions_main = f'''<!-- Hero -->
    <section class="relative min-h-[60vh] bg-paw-900 py-24">
      <div class="mx-auto flex min-h-[60vh] max-w-7xl flex-col justify-center px-4 sm:px-6 lg:px-8">
        <div class="max-w-2xl text-white">
          <p class="mb-4 text-sm font-semibold uppercase tracking-widest text-paw-100">Adoptions</p>
          <h1 class="text-4xl font-extrabold leading-tight sm:text-5xl lg:text-6xl">Pet Adoptions</h1>
          <p class="mt-6 text-lg leading-relaxed text-paw-100 sm:text-xl">Meet the cats and dogs waiting for a loving forever home.</p>
        </div>
      </div>
    </section>

    <!-- Listing -->
    <section class="py-20 sm:py-24">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex flex-wrap gap-3" role="group" aria-label="Filter by species">
          <button data-filter="all" class="filter-btn rounded-full bg-paw-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-paw-700">All</button>
          <button data-filter="cat" class="filter-btn rounded-full bg-gray-200 px-5 py-2.5 text-sm font-semibold text-gray-700 transition hover:bg-gray-300">Cats</button>
          <button data-filter="dog" class="filter-btn rounded-full bg-gray-200 px-5 py-2.5 text-sm font-semibold text-gray-700 transition hover:bg-gray-300">Dogs</button>
        </div>

        <div class="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3" id="adoption-grid">
{cards}
        </div>
      </div>
    </section>

    <script>
      const buttons = document.querySelectorAll('.filter-btn');
      const cards = document.querySelectorAll('.adoption-card');
      buttons.forEach((btn) => {{
        btn.addEventListener('click', () => {{
          const filter = btn.dataset.filter;
          buttons.forEach((b) => {{
            b.classList.toggle('bg-paw-600', b === btn);
            b.classList.toggle('text-white', b === btn);
            b.classList.toggle('bg-gray-200', b !== btn);
            b.classList.toggle('text-gray-700', b !== btn);
          }});
          cards.forEach((card) => {{
            card.classList.toggle('hidden', filter !== 'all' && card.dataset.species !== filter);
          }});
        }});
      }});
    </script>

'''

adoptions_html = build_page_header(
    'Pet Adoptions | Paws and Claws',
    'Adopt a cat or dog from Paws and Claws Animal Shelter in Port Douglas.'
) + adoptions_main + base_footer

Path('adoptions/index.html').write_text(adoptions_html)
print('Generated adoptions/index.html')

# ---------------------------------------------------------------------------
# 6. Generate individual pet pages
# ---------------------------------------------------------------------------
Path('pet').mkdir(exist_ok=True)
for i, a in enumerate(animals):
    prev_a = animals[(i - 1) % len(animals)]
    next_a = animals[(i + 1) % len(animals)]
    pet_main = f'''<!-- Hero -->
    <section class="relative min-h-[60vh] bg-paw-900 py-24">
      <div class="mx-auto flex min-h-[60vh] max-w-7xl flex-col justify-center px-4 sm:px-6 lg:px-8">
        <div class="max-w-2xl text-white">
          <p class="mb-4 text-sm font-semibold uppercase tracking-widest text-paw-100">{a['species'].capitalize()}</p>
          <h1 class="text-4xl font-extrabold leading-tight sm:text-5xl lg:text-6xl">{a['name']}</h1>
          <p class="mt-6 text-lg leading-relaxed text-paw-100 sm:text-xl">Approx DOB: {a['dob']} | {a['sex']}</p>
        </div>
      </div>
    </section>

    <!-- Pet details -->
    <section class="py-20 sm:py-24">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="grid gap-12 lg:grid-cols-2">
          <div class="overflow-hidden rounded-2xl bg-gray-100">
            <img src="{a['photo']}" alt="{a['name']}" class="w-full object-cover" />
          </div>
          <div>
            <h2 class="text-3xl font-bold text-gray-900 sm:text-4xl">About {a['name']}</h2>
            <p class="mt-6 leading-relaxed text-gray-600">{a['description']}</p>
            <ul class="mt-6 space-y-3 text-gray-700">
              <li><strong class="text-gray-900">Species:</strong> {a['species'].capitalize()}</li>
              <li><strong class="text-gray-900">Sex:</strong> {a['sex']}</li>
              <li><strong class="text-gray-900">Approx DOB:</strong> {a['dob']}</li>
              <li><strong class="text-gray-900">Status:</strong> {a['status'].capitalize()}</li>
            </ul>
            <a href="mailto:reception@pawsandclaws.org.au?subject=Adoption enquiry: {a['name']}" class="mt-8 inline-block rounded-full bg-paw-600 px-7 py-3.5 font-semibold text-white transition hover:bg-paw-700">Ask about {a['name']}</a>
          </div>
        </div>

        <div class="mt-12 flex items-center justify-between border-t border-gray-200 pt-8">
          <a href="pet/{prev_a['slug']}/" class="font-semibold text-paw-600 hover:text-paw-700">← {prev_a['name']}</a>
          <a href="adoptions/" class="rounded-full bg-gray-100 px-6 py-2.5 font-semibold text-gray-700 hover:bg-gray-200">Back to adoptions</a>
          <a href="pet/{next_a['slug']}/" class="font-semibold text-paw-600 hover:text-paw-700">{next_a['name']} →</a>
        </div>
      </div>
    </section>

'''
    pet_html = build_page_header(
        f"{a['name']} | Paws and Claws",
        f"Adopt {a['name']}, a {a['sex'].lower()} {a['species']} looking for a home at Paws and Claws Animal Shelter."
    ) + pet_main + base_footer

    pet_dir = Path(f"pet/{a['slug']}")
    pet_dir.mkdir(parents=True, exist_ok=True)
    (pet_dir / 'index.html').write_text(pet_html)
    print(f"Generated pet/{a['slug']}/index.html")

# ---------------------------------------------------------------------------
# 7. Write .gitignore so generated pages don't get committed
# ---------------------------------------------------------------------------
gitignore = Path('.gitignore')
lines = {
    '# Generated adoptions and pet pages are built by build-animals.py',
    '/adoptions/',
    '/pet/',
    '__pycache__/',
    '.wrangler/',
    '.DS_Store'
}
existing = set(gitignore.read_text().splitlines()) if gitignore.exists() else set()
new_lines = [l for l in lines if l not in existing]
if new_lines:
    with gitignore.open('a') as f:
        for l in new_lines:
            f.write(f'\n{l}')
    print('Updated .gitignore')

# ---------------------------------------------------------------------------
# 8. Update GitHub Actions workflow to run the build before deploy
# ---------------------------------------------------------------------------
workflow = Path('.github/workflows/deploy.yml')
if workflow.exists():
    content = workflow.read_text()
    if 'python3 build-animals.py' not in content:
        content = content.replace(
            '      - name: Deploy to Cloudflare Pages\n        uses: cloudflare/wrangler-action@v3',
            '      - name: Set up Python\n        uses: actions/setup-python@v5\n        with:\n          python-version: "3.x"\n\n      - name: Build animal pages\n        run: python3 build-animals.py\n\n      - name: Deploy to Cloudflare Pages\n        uses: cloudflare/wrangler-action@v3'
        )
        workflow.write_text(content)
        print('Updated .github/workflows/deploy.yml')
