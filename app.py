"""
============================================================
  app.py  —  Command Line Interface (the program you run)
============================================================

This is the ENTRY POINT of the project.
Run it in your terminal like this:

    python app.py

It will ask you for the business details, run the audit,
print results to the screen, and generate a PDF report.

FLOW:
    1. Ask user for business info
    2. Call checker.py to run all checks
    3. Print a nicely formatted summary to the terminal
    4. Call report.py to generate the PDF
    5. Tell the user where the PDF was saved
"""

import os
import sys

# Import our own modules (the files we created)
from checker import run_full_audit
from report import generate_pdf_report


# ──────────────────────────────────────────────
# TERMINAL COLOR CODES
# ──────────────────────────────────────────────
# These special codes make the terminal output colorful
# They only work on Mac/Linux/modern Windows terminals

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"


def color_score(score: int) -> str:
    """Wraps a score number in the right terminal color."""
    if score >= 70:
        return f"{GREEN}{score}{RESET}"
    elif score >= 40:
        return f"{YELLOW}{score}{RESET}"
    else:
        return f"{RED}{score}{RESET}"


def print_banner():
    """Prints a welcome banner when the app starts."""
    banner = f"""
{BLUE}{'='*56}{RESET}
{BOLD}{CYAN}   🏪  Digital Health Checker for Local Businesses  {RESET}
{BLUE}{'='*56}{RESET}
{GRAY}   Check how visible your business is online —
   get a score + actionable tips in under 60 seconds.{RESET}
{BLUE}{'='*56}{RESET}
"""
    print(banner)


def get_user_input() -> tuple:
    """
    Asks the user to enter business details interactively.

    Returns:
        tuple: (business_name, city, website_url)
    """

    print(f"{BOLD}Please enter the business details:{RESET}\n")

    # input() displays a prompt and waits for the user to type something
    business_name = input(f"  {CYAN}Business Name{RESET}: ").strip()
    if not business_name:
        print(f"{RED}  Error: Business name cannot be empty.{RESET}")
        sys.exit(1)   # Stop the program with error code 1

    city = input(f"  {CYAN}City{RESET}: ").strip()
    if not city:
        print(f"{RED}  Error: City cannot be empty.{RESET}")
        sys.exit(1)

    website_url = input(f"  {CYAN}Website URL{RESET} (press Enter to skip): ").strip()

    print()   # Blank line for spacing
    return business_name, city, website_url


def print_results(audit: dict):
    """
    Displays the audit results in a clean, readable format in the terminal.

    Parameters:
        audit (dict): The full result from run_full_audit()
    """

    score = audit["score"]

    # ── Overall Score ──
    print(f"\n{BLUE}{'─'*56}{RESET}")
    print(f"  {BOLD}DIGITAL HEALTH SCORE:{RESET}  {color_score(score['total'])}/100   Grade: {BOLD}{score['grade']}{RESET}")
    print(f"  {GRAY}{score['summary']}{RESET}")
    print(f"{BLUE}{'─'*56}{RESET}")

    # Sub-scores breakdown
    print(f"\n  {BOLD}Score Breakdown:{RESET}")
    print(f"    📡 Google Presence:  {color_score(score['google_score'])}/40")
    print(f"    🌐 Website Health:   {color_score(score['website_score'])}/40")
    print(f"    📱 Social Media:     {color_score(score['social_score'])}/20")

    # ── Google Results ──
    print(f"\n{BLUE}{'─'*56}{RESET}")
    print(f"  {BOLD}📡 Google Presence{RESET}")
    print(f"{BLUE}{'─'*56}{RESET}")

    google = audit["google"]
    found_str   = f"{GREEN}Yes ✓{RESET}" if google.get("found")            else f"{RED}No ✗{RESET}"
    panel_str   = f"{GREEN}Yes ✓{RESET}" if google.get("has_knowledge_panel") else f"{YELLOW}No{RESET}"

    print(f"    Found on Google:      {found_str}")
    print(f"    Name appeared:        {google.get('result_count', 0)} times")
    print(f"    Knowledge Panel:      {panel_str}")

    # ── Website Results ──
    print(f"\n{BLUE}{'─'*56}{RESET}")
    print(f"  {BOLD}🌐 Website Health{RESET}")
    print(f"{BLUE}{'─'*56}{RESET}")

    website = audit["website"]
    if website.get("accessible"):
        https_str  = f"{GREEN}Yes ✓{RESET}" if website.get("uses_https")        else f"{RED}No ✗{RESET}"
        mobile_str = f"{GREEN}Yes ✓{RESET}" if website.get("is_mobile_friendly") else f"{RED}No ✗{RESET}"
        phone_str  = f"{GREEN}Yes ✓{RESET}" if website.get("has_phone")          else f"{YELLOW}No{RESET}"
        email_str  = f"{GREEN}Yes ✓{RESET}" if website.get("has_email")          else f"{YELLOW}No{RESET}"

        print(f"    Status:              {GREEN}Online ✓{RESET}")
        print(f"    Load time:           {website.get('load_time')}s  ({website.get('speed_rating')})")
        print(f"    Uses HTTPS:          {https_str}")
        print(f"    Mobile Friendly:     {mobile_str}")
        print(f"    Phone on site:       {phone_str}")
        print(f"    Email on site:       {email_str}")
    else:
        print(f"    Status:              {RED}Not accessible ✗{RESET}")
        print(f"    Reason:              {website.get('error', 'Unknown')}")

    # ── Social Media Results ──
    print(f"\n{BLUE}{'─'*56}{RESET}")
    print(f"  {BOLD}📱 Social Media{RESET}")
    print(f"{BLUE}{'─'*56}{RESET}")

    for platform, info in audit["social"].items():
        status = f"{GREEN}Likely exists ✓{RESET}" if info.get("likely_exists") else f"{YELLOW}Not found{RESET}"
        print(f"    {platform:<14}  {status}")

    # ── Recommendations ──
    print(f"\n{BLUE}{'─'*56}{RESET}")
    print(f"  {BOLD}💡 Recommendations{RESET}")
    print(f"{BLUE}{'─'*56}{RESET}\n")

    for tip in audit["recommendations"]:
        # Wrap long tips at 60 characters for readability
        print(f"  {tip}\n")


def main():
    """
    The main function — this runs when you execute: python app.py

    It orchestrates the whole flow:
        1. Show banner
        2. Get input
        3. Run audit
        4. Print results
        5. Generate PDF
    """

    print_banner()

    # Step 1: Get business info from user
    business_name, city, website_url = get_user_input()

    # Step 2: Run the full audit (this is where all the checking happens)
    print(f"{CYAN}Running audit...{RESET}")
    audit = run_full_audit(business_name, city, website_url)

    # Step 3: Print results to terminal
    print_results(audit)

    # Step 4: Generate the PDF report
    print(f"\n{CYAN}Generating PDF report...{RESET}")

    # Create an "output" folder if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)   # exist_ok=True means don't error if already exists

    pdf_path = generate_pdf_report(audit, output_dir)

    # Step 5: Tell the user where the PDF is
    print(f"\n{GREEN}{'='*56}{RESET}")
    print(f"  {BOLD}✅ Audit complete!{RESET}")
    print(f"  📄 PDF saved to: {BOLD}{pdf_path}{RESET}")
    print(f"{GREEN}{'='*56}{RESET}\n")


# ──────────────────────────────────────────────
# PYTHON ENTRY POINT
# ──────────────────────────────────────────────
# This block only runs when you execute this file directly.
# It does NOT run when this file is imported by another module.
# This is standard Python convention.

if __name__ == "__main__":
    main()
