import requests
import json
from colorama import Fore, Style, init

# Inisialisasi colorama
init(autoreset=True)

# Judul Script dan Channel
SCRIPT_TITLE = "Aigo Auto Completed"
CHANNEL_LINK = "https://t.me/ugdairdrop"

# URL endpoint GraphQL
url = "https://api.aigo.network/graphql"

# Membaca token autentikasi dari file
def read_auth_tokens(filename='aigo.txt'):
    with open(filename, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Header HTTP dengan autentikasi
def get_headers(auth_token):
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

# Query GraphQL untuk mengambil quest
query = """
query getQuests {
  web3FarmingProfile {
    quests {
      id
      title
      completed
    }
  }
}
"""

# Payload untuk permintaan POST
payload = {
    "query": query,
    "operationName": "getQuests"
}

def fetch_quests(auth_token):
    headers = get_headers(auth_token)
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        quests = data.get('data', {}).get('web3FarmingProfile', {}).get('quests', [])
        
        # Menyaring quest yang belum selesai
        unfinished_quests = [
            quest for quest in quests if not quest.get('completed', False)
        ]
        
        return unfinished_quests
    else:
        print(Fore.RED + Style.BRIGHT + f"Request failed with status code {response.status_code}")
        print(Fore.RED + response.text)
        return []

def complete_quests(quests, auth_token):
    mutation_query = """
    mutation web3FarmingVerifyQuestAndClaimPoints($questId: String) {
      web3FarmingVerifyQuestAndClaimPoints(questId: $questId) {
        id
        type
        title
        description
        URL
        androidDownloadLink
        appleDownloadLink
        GOPoints
        completed
      }
    }
    """
    
    completed_count = 0
    failed_count = 0
    
    for quest in quests:
        quest_title = quest.get('title')
        
        # Payload untuk permintaan POST
        mutation_payload = {
            "query": mutation_query,
            "variables": {
                "questId": quest.get('id')
            },
            "operationName": "web3FarmingVerifyQuestAndClaimPoints"
        }
        
        headers = get_headers(auth_token)
        # Mengirim permintaan POST untuk memperbarui status quest
        mutation_response = requests.post(url, json=mutation_payload, headers=headers)
        
        if mutation_response.status_code == 200:
            result = mutation_response.json()
            print(Fore.GREEN + Style.BRIGHT + f"✓ Quest '{quest_title}' completed successfully.")
            completed_count += 1
        else:
            print(Fore.RED + Style.BRIGHT + f"✗ Failed to complete quest '{quest_title}'. Status code: {mutation_response.status_code}")
            print(Fore.RED + mutation_response.text)
            failed_count += 1
    
    return completed_count, failed_count

def main():
    # Menampilkan judul script
    print(Fore.GREEN + "=" * 40)
    print(Fore.YELLOW + Style.BRIGHT + SCRIPT_TITLE)
    print(Fore.YELLOW + "Channel: " + CHANNEL_LINK)
    print(Fore.GREEN + "=" * 40)
    print("\n")
    
    auth_tokens = read_auth_tokens()
    
    for auth_token in auth_tokens:
        print(Fore.YELLOW + Style.BRIGHT + f"Processing with token: {auth_token[:10]}...")  # Menampilkan bagian awal token untuk identifikasi
        # Ambil daftar quest yang belum selesai
        unfinished_quests = fetch_quests(auth_token)
        
        if unfinished_quests:
            print(Fore.YELLOW + f"Found {len(unfinished_quests)} unfinished quests.")
            # Update status quest yang belum selesai
            completed_count, failed_count = complete_quests(unfinished_quests, auth_token)
            print(Fore.YELLOW + Style.BRIGHT + f"Summary for token {auth_token[:10]}:")
            print(Fore.GREEN + Style.BRIGHT + f"Completed quests: {completed_count}")
            print(Fore.RED + Style.BRIGHT + f"Failed quests: {failed_count}")
        else:
            print(Fore.YELLOW + "No quests to complete.")
        
        print(Fore.CYAN + "-" * 50)

if __name__ == "__main__":
    main()
