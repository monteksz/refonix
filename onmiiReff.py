import random
import re
import time
import requests
import secrets
import string
from bs4 import BeautifulSoup
import json

# Function to generate a random password with a maximum length of 8 characters
def generate_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(8))

# Function to generate a random email address using 1secmail API
def get_email():
    random_username = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    domains = ['1secmail.com', '1secmail.org', 'txcct.com', '1secmail.net']
    domain = random.choice(domains)
    email = f"{random_username}@{domain}"
    return email

# Function to register using the API
def register(email, invite_code):
    url = 'https://onmi-waitlist.rand.wtf/api/register'
    password = generate_password()
    payload = {
        'password': password,
        'email': email,
        'password_hash': password,
        'password_confirmation': password,
        'invite_code': invite_code
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return password, f"Registration successful! Account {email} with password {password}"
    else:
        return None, f"Registration failed with status code: {response.status_code} and message: {response.json()}"

# Function to get inbox ID using 1secmail API
def get_inbox_id(email, try_count=0):
    login, domain = email.split('@')
    api_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if data:
            inbox_id = data[0]["id"]
            return inbox_id
        else:
            if try_count < 4:
                time.sleep(5)
                return get_inbox_id(email, try_count + 1)
            return None
    except requests.exceptions.RequestException:
        if try_count < 4:
            time.sleep(5)
            return get_inbox_id(email, try_count + 1)
        return None

# Function to get message using 1secmail API
def get_message(email, inbox_id, try_count=0):
    login, domain = email.split('@')
    endpoint = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={inbox_id}"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        message_data = response.json()
        if message_data:
            return message_data["body"]
        return None
    except requests.exceptions.RequestException:
        if try_count < 4:
            time.sleep(5)
            return get_message(email, inbox_id, try_count + 1)
        return None

# Function to extract links from HTML content
def extract_links_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    href_links = soup.find_all('a', href=True)
    links = [link['href'] for link in href_links]
    return links

# Function to follow a link and get the final destination URL
def follow_link(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            final_url = response.url
            return final_url
        return None
    except requests.exceptions.RequestException:
        return None

# Function to extract verification link from list of links
def extract_verify_link(links):
    for link in links:
        final_url = follow_link(link)
        if final_url:
            match = re.search(r'https:\/\/onmi.io\/\?verify_code=([\w-]+)', final_url)
            if match:
                return match.group(1)
    return None

# Function to verify the user using the extracted code
def verify_user(code):
    url = "https://onmi-waitlist.rand.wtf/api/activate"
    headers = {
        "Host": "onmi-waitlist.rand.wtf",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "id,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://onmi.io/",
        "Content-Type": "application/json; charset=utf-8",
        "Origin": "https://onmi.io",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Te": "trailers",
    }
    payload = {"code": code}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Verification failed: {e}")
        return None

# Function to login and perform actions
def login_and_perform_actions(email, password):
    login_url = "https://onmi-waitlist.rand.wtf/api/login"
    login_headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json; charset=utf-8",
        "origin": "https://onmi.io",
        "priority": "u=1, i",
        "referer": "https://onmi.io/",
        "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }

    login_data = json.dumps({
        'email': email,
        'password': password
    })

    response = requests.post(login_url, headers=login_headers, data=login_data)
    http_code = response.status_code

    if http_code == 200:
        response_data = response.json()
        token = response_data['token']
        print(f"Login berhasil untuk {email}\nToken: {token}")

        link_social_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://onmi.io",
            "priority": "u=1, i",
            "referer": "https://onmi.io/",
            "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "authorization": f"Bearer: {token}",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }

        actions = [
            json.dumps({'source': 'follow_twitter_nk'}),
            json.dumps({'source': 'follow_instagram_nk'}),
            json.dumps({'source': 'follow_instagram'}),
            json.dumps({'source': 'follow_twitter'}),
            json.dumps({'source': 'follow_discord'}),
            json.dumps({'source': 'follow_telegram'}),
            json.dumps({'content': 'https://twitter.com/onmi_ar', 'type': 'tweet'}),
            json.dumps({'content': 'https://youtu.be/sRKaRK5X5cw?si=7wTsCB8PQY-dxXLJ', 'type': 'like_youtube_nk_2'}),
            json.dumps({'content': 'https://youtu.be/ZEKRm8xOJ4c?si=N_inAM-INoXixlD', 'type': 'like_youtube_nk_3'})
        ]

        def linked(url, var, head):
            response = requests.post(url, headers=head, data=var)
            data = response.json()
            return data['status']

        responses = [linked("https://onmi-waitlist.rand.wtf/api/link_social", action, link_social_headers) for action in actions[:6]]
        responses += [linked("https://onmi-waitlist.rand.wtf/api/verifications", action, link_social_headers) for action in actions[6:]]

        print(f"Response for linking social for {email}: " + " ".join([f"{i+1} {resp}" for i, resp in enumerate(responses)]))
    else:
        print(f"Login gagal untuk {email}: {response.text}")

# Main function to get email, register, get inbox ID, get message, and extract verification link
def main():
    try:
        print("=========================================================================")
        invite_code = input("Masukan Invite Code: ")
        num_accounts = int(input("Mau berapa banyak akun: "))

        for i in range(num_accounts):
            email = get_email()
            print(f'Generated Email: {email}')
            password, registration_response = register(email, invite_code)
            print(registration_response)
            if not password:
                continue
            
            inbox_id = get_inbox_id(email)
            print(f'Inbox ID: {inbox_id}')  # Print inbox ID
            
            if inbox_id:
                message_data = get_message(email, inbox_id)
                if message_data:
                    html_content = message_data
                    links = extract_links_from_html(html_content)
                    verification_code = extract_verify_link(links)
                    if verification_code:
                        print(f'Verification Code: {verification_code}')
                        verification_response = verify_user(verification_code)
                        if verification_response:
                            print("Akun Berhasil di verfikasi")
                            # Save to file
                            with open("acc.txt", "a") as file:
                                file.write(f"{email}:{password}\n")
                            
                            # Immediately login and perform actions
                            login_and_perform_actions(email, password)
                        else:
                            print("Akun Gagal di verfikasi")
                    else:
                        print("Gk ada verif code atau email mati coba mulai ulang")
                else:
                    print("Failed to retrieve message data: No message data returned")
            else:
                print("Failed to retrieve inbox ID")
            print(f"Akun ke-{i+1} Telah selesai")
            print("=========================================================================")
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    main()
