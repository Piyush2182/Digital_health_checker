"""
============================================================
  checker.py  —  Core logic for the Digital Health Checker
============================================================

This file does all the "detective work":
  1. Searches Google to see if the business is visible online
  2. Checks the business website (speed, HTTPS, mobile-friendliness)
  3. Calculates an overall Digital Health Score out of 100
  4. Returns a structured dictionary of results

How to use:
    from checker import run_full_audit
    results = run_full_audit("Sharma Cafe", "Mumbai")
"""

import requests                        # For making HTTP requests (visiting websites)
from bs4 import BeautifulSoup          # For parsing HTML pages (reading web content)
import time                            # For measuring how long a website takes to load
import re                              # For pattern matching (finding phone numbers, emails)
import urllib.parse                    # For safely encoding text into URLs


# ──────────────────────────────────────────────
# SECTION 1 — GOOGLE SEARCH CHECK
# ──────────────────────────────────────────────

def check_google_presence(business_name: str, city: str) -> dict:
    """
    Searches Google for the business and checks if it appears in results.

    WHY THIS MATTERS:
        If a business doesn't show up on Google, customers can't find it.
        This is the #1 reason small businesses lose walk-in customers.

    HOW IT WORKS:
        We send a fake "browser" request to Google search and read the HTML.
        Then we look for the business name in the results.

    Parameters:
        business_name (str): e.g. "Sharma Cafe"
        city (str): e.g. "Mumbai"

    Returns:
        dict: {
            "found": True/False,
            "result_count": number of times name appeared,
            "has_knowledge_panel": True/False (the info box on the right side of Google)
        }
    """

    # Build the Google search URL — same as typing in the search bar
    query = f"{business_name} {city}"
    encoded_query = urllib.parse.quote_plus(query)   # Converts spaces to + signs, safe for URLs
    url = f"https://www.google.com/search?q={encoded_query}&num=10"

    # We pretend to be a real browser so Google doesn't block us
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        # Visit the Google search page (timeout=8 means wait max 8 seconds)
        response = requests.get(url, headers=headers, timeout=8)

        # Parse the HTML so we can search through it
        soup = BeautifulSoup(response.text, "html.parser")

        # Get all visible text from the page and lowercase it for easy searching
        page_text = soup.get_text().lower()
        business_lower = business_name.lower()

        # Count how many times the business name appears in the results
        result_count = page_text.count(business_lower)

        # Google shows a special "Knowledge Panel" for established businesses
        # This appears as a box on the right side — very good sign of credibility
        has_knowledge_panel = (
            "knowledge" in page_text or
            "directions" in page_text or
            "open now" in page_text or
            "opening hours" in page_text
        )

        return {
            "found": result_count > 0,
            "result_count": result_count,
            "has_knowledge_panel": has_knowledge_panel
        }

    except requests.RequestException as e:
        # If the request fails for any reason, return a safe default
        print(f"  [Warning] Google check failed: {e}")
        return {"found": False, "result_count": 0, "has_knowledge_panel": False}


# ──────────────────────────────────────────────
# SECTION 2 — WEBSITE HEALTH CHECK
# ──────────────────────────────────────────────

def check_website_health(website_url: str) -> dict:
    """
    Visits the business website and checks multiple health indicators.

    WHY THIS MATTERS:
        A slow or broken website drives customers away. Studies show
        53% of users leave if a page takes more than 3 seconds to load.

    WHAT WE CHECK:
        - Does the site load at all? (basic availability)
        - Does it use HTTPS? (security — browsers warn on HTTP sites)
        - How fast does it load? (under 2s = great, 2-5s = ok, 5s+ = bad)
        - Does it look mobile-friendly? (most users are on phones)
        - Does the page have a title? (basic SEO check)

    Parameters:
        website_url (str): e.g. "https://sharmacafe.com"

    Returns:
        dict with all health indicators and scores
    """

    # If user didn't include https://, add it automatically
    if not website_url.startswith(("http://", "https://")):
        website_url = "https://" + website_url

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        )
        # ↑ We pretend to be an iPhone to test mobile experience
    }

    try:
        # Record the time BEFORE the request starts
        start_time = time.time()

        response = requests.get(website_url, headers=headers, timeout=10, allow_redirects=True)

        # Calculate how long the request took (in seconds)
        load_time = round(time.time() - start_time, 2)

        # Parse the HTML of the website
        soup = BeautifulSoup(response.text, "html.parser")

        # ── Check 1: Does it use HTTPS? ──
        uses_https = website_url.startswith("https://") or response.url.startswith("https://")

        # ── Check 2: Load speed ──
        if load_time < 2:
            speed_rating = "Fast ✅"
        elif load_time < 5:
            speed_rating = "Moderate ⚠️"
        else:
            speed_rating = "Slow ❌"

        # ── Check 3: Does it have a page title? ──
        # <title> tags are important for SEO — Google uses them in search results
        title_tag = soup.find("title")
        has_title = title_tag is not None
        page_title = title_tag.get_text(strip=True) if has_title else "None found"

        # ── Check 4: Mobile viewport meta tag ──
        # This tag tells browsers to scale the page for mobile screens
        # Without it, the site looks like a tiny desktop version on phones
        viewport_meta = soup.find("meta", attrs={"name": "viewport"})
        is_mobile_friendly = viewport_meta is not None

        # ── Check 5: Does it have a contact number? ──
        # We use regex (pattern matching) to find phone number formats
        page_text = soup.get_text()
        phone_pattern = re.compile(r'(\+91[\s\-]?)?[6-9]\d{9}|0\d{2,4}[\s\-]?\d{6,8}')
        has_phone = bool(phone_pattern.search(page_text))

        # ── Check 6: Does it have an email? ──
        email_pattern = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
        has_email = bool(email_pattern.search(page_text))

        return {
            "accessible": True,
            "status_code": response.status_code,   # 200 = OK, 404 = not found, 500 = server error
            "load_time": load_time,
            "speed_rating": speed_rating,
            "uses_https": uses_https,
            "has_title": has_title,
            "page_title": page_title,
            "is_mobile_friendly": is_mobile_friendly,
            "has_phone": has_phone,
            "has_email": has_email,
            "final_url": response.url         # In case the site redirected us
        }

    except requests.exceptions.SSLError:
        # This happens when the HTTPS certificate is invalid/expired
        return {
            "accessible": False,
            "error": "SSL/HTTPS certificate error — site may not be secure",
            "uses_https": False
        }
    except requests.exceptions.ConnectionError:
        return {
            "accessible": False,
            "error": "Could not connect — website may be down or URL is wrong"
        }
    except requests.exceptions.Timeout:
        return {
            "accessible": False,
            "error": "Website took too long to respond (>10 seconds)"
        }
    except Exception as e:
        return {
            "accessible": False,
            "error": f"Unexpected error: {str(e)}"
        }


# ──────────────────────────────────────────────
# SECTION 3 — SOCIAL MEDIA CHECK
# ──────────────────────────────────────────────

def check_social_presence(business_name: str) -> dict:
    """
    Checks if the business likely has profiles on major social platforms.

    WHY THIS MATTERS:
        Social media is where customers discover and trust businesses today.
        A business with no social presence misses out on free marketing.

    HOW IT WORKS:
        We construct likely profile URLs and check if they return a valid page.
        (We can't verify it's THE right business — just that a page exists.)

    Parameters:
        business_name (str): e.g. "Sharma Cafe"

    Returns:
        dict: which platforms returned a valid (200 OK) response
    """

    # Create a "slug" — lowercase, no spaces — for building profile URLs
    # e.g. "Sharma Cafe" → "sharmacafe"
    name_slug = business_name.lower().replace(" ", "").replace("&", "and")

    # List of social platforms and their profile URL formats
    platforms = {
        "Facebook":  f"https://www.facebook.com/{name_slug}",
        "Instagram": f"https://www.instagram.com/{name_slug}/",
        "Twitter/X": f"https://twitter.com/{name_slug}",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"
    }

    results = {}

    for platform, url in platforms.items():
        try:
            # We use HEAD request — faster than GET, just checks if page exists
            response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)

            # 200 = page exists, 404 = page not found
            results[platform] = {
                "checked_url": url,
                "likely_exists": response.status_code == 200
            }
        except Exception:
            results[platform] = {
                "checked_url": url,
                "likely_exists": False
            }

    return results


# ──────────────────────────────────────────────
# SECTION 4 — SCORE CALCULATOR
# ──────────────────────────────────────────────

def calculate_score(google_data: dict, website_data: dict, social_data: dict) -> dict:
    """
    Combines all check results into a single Digital Health Score out of 100.

    SCORING BREAKDOWN:
        Google Presence:  40 points
        Website Health:   40 points
        Social Media:     20 points

    Parameters:
        google_data:  result from check_google_presence()
        website_data: result from check_website_health()
        social_data:  result from check_social_presence()

    Returns:
        dict: {
            "total": overall score (0–100),
            "google_score": 0–40,
            "website_score": 0–40,
            "social_score": 0–20,
            "grade": letter grade,
            "summary": short verdict text
        }
    """

    # ── Google Score (max 40 points) ──
    google_score = 0
    if google_data.get("found"):
        google_score += 25                           # +25 if they appear at all
    if google_data.get("has_knowledge_panel"):
        google_score += 15                           # +15 for having a Knowledge Panel

    # ── Website Score (max 40 points) ──
    website_score = 0
    if website_data.get("accessible"):
        website_score += 15                          # +15 just for being online
        if website_data.get("uses_https"):
            website_score += 8                       # +8 for secure HTTPS
        if website_data.get("is_mobile_friendly"):
            website_score += 7                       # +7 for mobile viewport
        load_time = website_data.get("load_time", 99)
        if load_time < 2:
            website_score += 5                       # +5 fast load
        elif load_time < 5:
            website_score += 2                       # +2 acceptable load
        if website_data.get("has_phone"):
            website_score += 3                       # +3 phone number visible
        if website_data.get("has_email"):
            website_score += 2                       # +2 email visible

    # ── Social Score (max 20 points) ──
    social_score = 0
    points_per_platform = 20 // max(len(social_data), 1)   # Divide evenly among platforms
    for platform, info in social_data.items():
        if info.get("likely_exists"):
            social_score += points_per_platform

    # Cap all scores at their maximums (just in case)
    google_score  = min(google_score, 40)
    website_score = min(website_score, 40)
    social_score  = min(social_score, 20)

    total = google_score + website_score + social_score

    # ── Assign a letter grade ──
    if total >= 80:
        grade, summary = "A", "Excellent! Strong digital presence."
    elif total >= 60:
        grade, summary = "B", "Good, but a few areas need improvement."
    elif total >= 40:
        grade, summary = "C", "Average — significant improvements possible."
    elif total >= 20:
        grade, summary = "D", "Poor — urgent improvements needed."
    else:
        grade, summary = "F", "Critical — this business is almost invisible online."

    return {
        "total": total,
        "google_score": google_score,
        "website_score": website_score,
        "social_score": social_score,
        "grade": grade,
        "summary": summary
    }


# ──────────────────────────────────────────────
# SECTION 5 — GENERATE RECOMMENDATIONS
# ──────────────────────────────────────────────

def generate_recommendations(google_data: dict, website_data: dict, social_data: dict) -> list:
    """
    Looks at all the check results and creates a list of actionable tips.

    WHY THIS MATTERS:
        A score without advice is useless. Business owners need to know
        exactly what to fix, in plain language.

    Returns:
        list of strings — each one is a recommendation
    """

    tips = []

    # ── Google tips ──
    if not google_data.get("found"):
        tips.append("🔴 Your business is not appearing on Google. Create a free Google Business Profile at business.google.com — it takes 15 minutes.")
    elif not google_data.get("has_knowledge_panel"):
        tips.append("🟡 You appear on Google but don't have a Knowledge Panel. Verify your Google Business Profile to get one — it dramatically improves trust.")

    # ── Website tips ──
    if not website_data.get("accessible"):
        tips.append("🔴 Your website is not accessible. Check if the domain is paid and the hosting is active.")
    else:
        if not website_data.get("uses_https"):
            tips.append("🔴 Your website uses HTTP instead of HTTPS. Get a free SSL certificate (via Let's Encrypt). Browsers warn users about non-HTTPS sites.")
        if not website_data.get("is_mobile_friendly"):
            tips.append("🟡 Your website is NOT mobile-friendly. Over 70% of visitors use phones. Ask your web developer to add a viewport meta tag.")
        load = website_data.get("load_time", 0)
        if load >= 5:
            tips.append(f"🔴 Your website loads in {load}s — very slow. Compress images and use caching to speed it up.")
        elif load >= 2:
            tips.append(f"🟡 Your website loads in {load}s. Aim for under 2 seconds. Consider image compression.")
        if not website_data.get("has_phone"):
            tips.append("🟡 No phone number found on your website. Add it prominently — customers want to call before visiting.")
        if not website_data.get("has_email"):
            tips.append("🟡 No email address found on your website. Add a contact email to build trust.")

    # ── Social media tips ──
    missing_platforms = [p for p, info in social_data.items() if not info.get("likely_exists")]
    if missing_platforms:
        tips.append(f"🟡 Consider creating profiles on: {', '.join(missing_platforms)}. Free profiles = free marketing.")

    if not tips:
        tips.append("✅ Great job! Your business has a solid digital presence. Keep it updated regularly.")

    return tips


# ──────────────────────────────────────────────
# SECTION 6 — MASTER FUNCTION (runs everything)
# ──────────────────────────────────────────────

def run_full_audit(business_name: str, city: str, website_url: str = "") -> dict:
    """
    The main function that runs ALL checks and returns a complete audit report.

    This is the function you call from app.py or report.py.

    Parameters:
        business_name (str): Name of the business
        city (str): City where it's located
        website_url (str): Optional — the business website URL

    Returns:
        dict: Complete audit with all raw data, score, and recommendations
    """

    print(f"\n🔍 Starting Digital Health Audit for: {business_name}, {city}")
    print("─" * 50)

    # Step 1: Check Google
    print("  📡 Checking Google presence...")
    google_data = check_google_presence(business_name, city)

    # Step 2: Check website (only if a URL was provided)
    print("  🌐 Checking website health...")
    if website_url.strip():
        website_data = check_website_health(website_url)
    else:
        # No website provided — give a failing result with a helpful message
        website_data = {
            "accessible": False,
            "error": "No website URL provided"
        }

    # Step 3: Check social media
    print("  📱 Checking social media...")
    social_data = check_social_presence(business_name)

    # Step 4: Calculate score
    print("  📊 Calculating score...")
    score_data = calculate_score(google_data, website_data, social_data)

    # Step 5: Generate recommendations
    recommendations = generate_recommendations(google_data, website_data, social_data)

    print(f"  ✅ Audit complete! Score: {score_data['total']}/100 ({score_data['grade']})\n")

    # Return everything bundled in one dictionary
    return {
        "business_name": business_name,
        "city": city,
        "website_url": website_url,
        "google": google_data,
        "website": website_data,
        "social": social_data,
        "score": score_data,
        "recommendations": recommendations
    }
