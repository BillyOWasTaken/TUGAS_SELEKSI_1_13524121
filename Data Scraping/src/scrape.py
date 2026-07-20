from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import json
import re
import time
from pathlib import Path

BASE = "https://personaassistant.dad"

def text_after_label(page, label):
    """Get text content that appears after a label"""
    try:
        # Try the working approach first (following::*[1])
        result = (
            page.get_by_text(label, exact=True)
            .locator("xpath=following::*[1]")
            .inner_text()
            .strip()
        )
        if result and not result.startswith('.') and not result.startswith('@'):
            return result
    except:
        pass
    
    # Fallback: try to find the content using alternative methods
    try:
        # Get the label element
        label_elem = page.get_by_text(label, exact=True)
        
        # Try to find the next sibling (if the content is a sibling)
        try:
            sibling = label_elem.locator("xpath=following-sibling::*[1]")
            if sibling.count() > 0:
                text = sibling.inner_text().strip()
                if text and not text.startswith('.') and not text.startswith('@'):
                    # Clean up multiple spaces/newlines
                    text = ' '.join(text.split())
                    if len(text) < 500:  # Not CSS
                        return text
        except:
            pass
        
        # Try to find content using the parent/child relationship
        try:
            parent = label_elem.locator("xpath=..")
            # Look for any text node or element after the label within the parent
            all_text = parent.inner_text()
            # Extract text after the label
            pattern = rf'{re.escape(label)}\s*(.*?)(?:\n|$)'
            match = re.search(pattern, all_text)
            if match:
                content = match.group(1).strip()
                if content and not content.startswith('.') and not content.startswith('@'):
                    return content
        except:
            pass
    except:
        pass
    
    return None

def list_after_label(page, label):
    """Get list items that appear after a label"""
    try:
        # Try to find a ul element after the label
        ul = (
            page.get_by_text(label, exact=True)
            .locator("xpath=following::ul[1]/li")
        )
        if ul.count() > 0:
            items = [
                ul.nth(i).inner_text().strip()
                for i in range(ul.count())
            ]
            if items:
                return items
    except:
        pass
    
    # Try alternative: find a div or container with list items
    try:
        label_elem = page.get_by_text(label, exact=True)
        parent = label_elem.locator("xpath=..")
        
        # Look for the next sibling that might contain a list
        sibling = parent.locator("xpath=following-sibling::*[1]")
        if sibling.count() > 0:
            text = sibling.inner_text().strip()
            if text and not text.startswith('.') and not text.startswith('@'):
                # Split into lines and clean
                items = []
                for line in text.splitlines():
                    line = line.strip()
                    # Remove bullet points
                    line = re.sub(r'^[•·∙\-]\s*', '', line)
                    if line and not line.startswith('.') and not line.startswith('@'):
                        items.append(line)
                if items:
                    return items
    except:
        pass
    
    # Try using regex on the page text
    try:
        page_text = page.locator('body').inner_text()
        pattern = rf'{re.escape(label)}\s*(.*?)(?:\n\n|\Z)'
        match = re.search(pattern, page_text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            items = []
            for line in content.splitlines():
                line = line.strip()
                line = re.sub(r'^[•·∙\-]\s*', '', line)
                if line and not line.startswith('.') and not line.startswith('@'):
                    items.append(line)
            return items
    except:
        pass
    
    return []

def scrape_episode(browser, url, episodes):
    """Scrape an episode using a new page/tab"""
    page = browser.new_page()
    
    try:
        page.goto(url, wait_until="networkidle")
        
        m = re.search(r"/episodes/(\d+)", url)
        episode_id = int(m.group(1))
        
        # Skip if already scraped
        if episode_id in episodes:
            page.close()
            return episodes
        
        title = page.locator("h1").first.inner_text().strip()
        crumbs = page.locator(".crumbs").first.inner_text()
        
        season = None
        episode = None
        
        sm = re.search(r"Season\s+(\d+)", crumbs)
        em = re.search(r"Episode\s+(\d+)", crumbs)
        
        if sm:
            season = int(sm.group(1))
        if em:
            episode = int(em.group(1))
        
        # Use the fixed text_after_label function
        air_date = text_after_label(page, "Originally Aired")
        runtime = text_after_label(page, "Runtime")
        
        try:
            summary = page.locator(
                '.change_translation_text[data-language="eng"] p'
            ).first.inner_text().strip()
        except:
            summary = None
        
        episodes[episode_id] = {
            "id": episode_id,
            "title": title,
            "season": season,
            "episode": episode,
            "air_date": air_date,
            "runtime": runtime,
            "summary": summary,
            "tvdb_url": url,
        }
        
        print(f"    Scraped episode: {title} (S{season}E{episode})")
        if air_date:
            print(f"      Air date: {air_date}")
        if runtime:
            print(f"      Runtime: {runtime}")
        
    except Exception as e:
        print(f"    Error scraping episode {url}: {e}")
    
    page.close()
    return episodes

def save_data(personas, episodes):
    # Save personas
    with open("", "w", encoding="utf-8") as f:
        json.dump(personas, f, indent=4, ensure_ascii=False)
    
    # Save episodes (convert dict to list for sorting)
    with open("../data/episodes.json", "w", encoding="utf-8") as f:
        json.dump(
            sorted(episodes.values(), key=lambda x: (x["season"] or 0, x["episode"] or 0)),
            f,
            indent=4,
            ensure_ascii=False,
        )

def load_existing_data():
    """Load existing data if files exist"""
    personas = []
    episodes = {}
    
    if Path("../data/personas.json").exists():
        with open("../data/personas.json", "r", encoding="utf-8") as f:
            personas = json.load(f)
        print(f"Loaded {len(personas)} existing personas")
    
    if Path("../data/episodes.json").exists():
        with open("../data/episodes.json", "r", encoding="utf-8") as f:
            episodes_data = json.load(f)
            episodes = {ep["id"]: ep for ep in episodes_data}
        print(f"Loaded {len(episodes)} existing episodes")
    
    return personas, episodes

def extract_episode_link(page, label):
    """Extract episode link from a specific field"""
    try:
        link = (
            page.get_by_text(label, exact=True)
            .locator("xpath=following::a[1]")
        )
        href = link.get_attribute("href")
        if href:
            episode_url = urljoin("https://thetvdb.com", href)
            m = re.search(r"/episodes/(\d+)", href)
            if m:
                episode_id = int(m.group(1))
                print(f"    Found {label}: Episode ID {episode_id}")
                return episode_id, episode_url
    except:
        pass
    return None, None

def scrape_persona_details(page, browser, episodes):
    """Scrape details from a persona page"""
    # Get the name
    name = page.locator("h1").first.inner_text().strip()
    print(f"Persona: {name}")
    
    # Get quotes using the fixed list_after_label
    quotes = list_after_label(page, "Quotes:")
    if quotes:
        print(f"Found {len(quotes)} quotes")
        for quote in quotes[:3]:  # Show first 3 quotes as preview
            print(f"- {quote[:50]}...")
    
    # Get notes using the fixed text_after_label
    notes = text_after_label(page, "Notes:")
    if notes:
        print(f"Notes: {notes[:50]}...")
    
    # First Appeared
    first_episode = None
    episode_id, episode_url = extract_episode_link(page, "First Appeared:")
    if episode_id:
        first_episode = episode_id
        if episode_id not in episodes and episode_url:
            print(f"Scraping first appeared episode...")
            episodes = scrape_episode(browser, episode_url, episodes)
    
    # Appeared in Intro
    intro_episode = None
    episode_id, episode_url = extract_episode_link(page, "Appeared in Intro:")
    if episode_id:
        intro_episode = episode_id
        if episode_id not in episodes and episode_url:
            print(f"Scraping intro episode...")
            episodes = scrape_episode(browser, episode_url, episodes)
    
    return {
        "name": name,
        "first_appeared": first_episode,
        "appeared_in_intro": intro_episode,
        "quotes": quotes,
        "notes": notes,
    }, episodes

with sync_playwright() as p:
    
    # Load existing data
    personas, episodes = load_existing_data()
    
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Get persona URLs from listing page
    persona_urls = set()
    page_num = 1
    
    while True:
        print("Listing page", page_num)
        
        page.goto(
            f"{BASE}/?page={page_num}",
            wait_until="networkidle"
        )
        
        links = page.locator('a[href^="/persona/"]')
        
        if links.count() == 0:
            break
        
        before = len(persona_urls)
        
        for i in range(links.count()):
            href = links.nth(i).get_attribute("href")
            persona_urls.add(urljoin(BASE, href))
        
        if len(persona_urls) == before:
            break
        
        page_num += 1
        time.sleep(.1)
    
    print(f"\n{len(persona_urls)} unique personas found")
    print("-" * 50)
    
    # Scrape persona pages
    for i, url in enumerate(sorted(persona_urls), 1):
        print(f"\n[{i}/{len(persona_urls)}] {url}")
        
        try:
            page.goto(url, wait_until="networkidle")
            
            persona_data, episodes = scrape_persona_details(page, browser, episodes)
            
            # Update or append persona
            existing_idx = next((idx for idx, p in enumerate(personas) if p["name"] == persona_data["name"]), None)
            if existing_idx is not None:
                personas[existing_idx] = persona_data
            else:
                personas.append(persona_data)
            
            # Save after each persona
            save_data(personas, episodes)
            print(f"Saved ({len(personas)} personas, {len(episodes)} episodes)")
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            import traceback
            traceback.print_exc()
            # Still save what we have
            save_data(personas, episodes)
    
    browser.close()

print(f"\n{'='*50}")
print(f"FINAL: {len(personas)} personas, {len(episodes)} episodes")
print("Data saved to ../data/personas.json and ../data/episodes.json")
