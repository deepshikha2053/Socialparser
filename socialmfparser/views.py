import os
import time
import praw
import prawcore
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import now
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def home(request):
    return render(request, 'index.html')

def authenticate_reddit():
    reddit = praw.Reddit(
        client_id="t4nx9H687_YTsFEZxkkQgg",
        client_secret="zArhPpw0a9ZP7D1P1C2iOtBtfTul7A",
        user_agent="Socialfeedyy/1.0 by u/deeptsy101",
        username="deeptsy101",
        password="Deepshikha@reddit03"
    )
    return reddit

def fetch_reddit_posts(query, limit=5):
    reddit = authenticate_reddit()
    try:
        if query.startswith("u/"):
            redditor = reddit.redditor(query[2:])
            posts = redditor.submissions.new(limit=limit)
            return [(post.title, post.selftext, post.url) for post in posts]
        else:
            subreddit = reddit.subreddit(query)
            posts = subreddit.hot(limit=limit)
            return [(post.title, post.selftext, post.url) for post in posts]
    except prawcore.exceptions.NotFound:
        return [("Error", f"Subreddit '{query}' not found.", "")]
    except prawcore.exceptions.Forbidden:
        return [("Error", f"Subreddit '{query}' is private.", "")]
    except prawcore.exceptions.RequestException:
        return [("Error", "Reddit API request failed. Try again later.", "")]
    except Exception as e:
        return [("Error", f"Unexpected error: {str(e)}", "")]

def setup_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    return driver

def fetch_instagram_data(username, driver, login_user, login_pass):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)
    
    try:
        # Log in to Instagram
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(login_user)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(login_pass, Keys.RETURN)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)
        
        # Close "Save Login Info" notification if it appears
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Not Now')]"))).click()
        except:
            pass
        
        # Close "Turn on Notifications" notification if it appears
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Not Now')]"))).click()
        except:
            pass
        
        # Navigate to the profile page
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(5)
        
        # Create a directory for screenshots
        os.makedirs("screenshots", exist_ok=True)
        
        # Capture follower, following, and post counts
        followers, following, posts = "N/A", "N/A", "N/A"
        try:
            stats = driver.find_elements(By.XPATH, "//ul[contains(@class, '_aa_7')]/li//span/span")
            if len(stats) >= 3:
                posts, followers, following = stats[0].text, stats[1].text, stats[2].text
        except Exception as e:
            print("Error fetching Instagram stats:", e)
        
        # Scroll and capture multiple screenshots
        screenshot_paths = []
        for i in range(3):  # Capture 3 screenshots
            driver.execute_script("window.scrollBy(0, 500);")  # Scroll down
            time.sleep(2)
            ss_path = f"screenshots/profile_screenshot_{i+1}.png"
            driver.save_screenshot(ss_path)
            screenshot_paths.append(ss_path)
        
        # Navigate to DMs and take a screenshot
        driver.get("https://www.instagram.com/direct/inbox/")
        time.sleep(5)
        dm_ss_path = "screenshots/dm_screenshot.png"
        driver.save_screenshot(dm_ss_path)
        
    except Exception as e:
        print("Instagram login/profile fetch error:", e)
        followers, following, posts = "N/A", "N/A", "N/A"
        screenshot_paths = []
        dm_ss_path = None
    
    driver.quit()
    return {
        "username": username,
        "followers": followers,
        "following": following,
        "posts": posts,
        "profile_screenshots": screenshot_paths,
        "dm_screenshot": dm_ss_path
    }

def save_to_pdf(data, filename="forensic_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(30, 780, f"Forensic Report - {now().strftime('%Y-%m-%d %H:%M:%S')}")
    y = 750

    if "username" in data:  # Instagram data
        c.drawString(30, y, f"Instagram Profile: {data['username']}")
        c.drawString(50, y - 20, f"Followers: {data['followers']}")
        c.drawString(50, y - 40, f"Following: {data['following']}")
        c.drawString(50, y - 60, f"Posts: {data['posts']}")
        y -= 80
        
        # Add profile screenshots
        if data.get("profile_screenshots"):
            c.drawString(30, y, "Profile Screenshots:")
            y -= 20
            for ss_path in data["profile_screenshots"]:
                c.drawImage(ss_path, 30, y - 120, width=200, height=150)
                y -= 170
        
        # Add DM screenshot
        if data.get("dm_screenshot"):
            c.drawString(30, y, "DM Screenshot:")
            c.drawImage(data["dm_screenshot"], 30, y - 120, width=200, height=150)
            y -= 170

    elif "reddit_posts" in data:  # Reddit data
        c.drawString(30, y, f"Reddit Query: {data['query']}")
        y -= 20
        for post in data["reddit_posts"]:
            title, selftext, url = post
            c.drawString(30, y, f"Title: {title}")
            c.drawString(30, y - 20, f"Content: {selftext}")
            c.drawString(30, y - 40, f"URL: {url}")
            y -= 60
            if y < 100:  # Add a new page if we run out of space
                c.showPage()
                y = 750

    c.save()
    return filename

def generate_forensic_report(request):
    if request.method == 'POST':
        platform = request.POST['platform']
        query = request.POST['query']
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if platform == 'instagram':
            driver = setup_driver()
            data = fetch_instagram_data(query, driver, username, password)
            pdf_file = save_to_pdf(data)
        elif platform == 'reddit':
            reddit_posts = fetch_reddit_posts(query)
            if reddit_posts and reddit_posts[0][0] == "Error":
                return HttpResponse(reddit_posts[0][1])
            data = {"query": query, "reddit_posts": reddit_posts}
            pdf_file = save_to_pdf(data)
        
        response = HttpResponse(open(pdf_file, 'rb').read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={pdf_file}'
        return response
    return HttpResponse("Invalid Request")