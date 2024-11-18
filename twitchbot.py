import asyncio
import requests
import random
from twitchio.ext import commands

# Twitch API credentials
CLIENT_ID = "gp762nuuoqcoxypju8c569th9wz7q5"
OAUTH_TOKEN = "4wco6szkbonz9agwa0gvr1khuim08a"
BASE_URL = "https://api.twitch.tv/helix"


def get_random_color():
    """
    Generate a random color in hexadecimal format.
    """
    return f"#{random.randint(0, 0xFFFFFF):06x}"


def fetch_badge_urls(badges_string, broadcaster_id):
    """
    Fetch badge image URLs from Twitch API based on the badges string.

    Parameters:
        badges_string (str): Badges from the message.tags["badges"].
        broadcaster_id (str): The broadcaster's Twitch ID.

    Returns:
        List[str]: List of badge image URLs.
    """
    headers = {
        "Authorization": f"Bearer {OAUTH_TOKEN}",
        "Client-Id": CLIENT_ID,
    }

    # Fetch global badges
    global_badges_response = requests.get(f"{BASE_URL}/chat/badges/global", headers=headers).json()
    global_badges = global_badges_response.get("data", [])
    print("Global Badges:", global_badges)  # Debug global badge data

    # Fetch channel-specific badges
    channel_badges_response = requests.get(f"{BASE_URL}/chat/badges?broadcaster_id={broadcaster_id}", headers=headers).json() if broadcaster_id else {"data": []}
    channel_badges = channel_badges_response.get("data", [])
    print("Channel Badges:", channel_badges)  # Debug channel badge data

    # Combine global and channel badges
    all_badges = global_badges + channel_badges

    # Extract badge image URLs
    badge_urls = []
    if badges_string:
        for badge in badges_string.split(","):
            try:
                badge_id, version = badge.split("/")
                badge_id = badge_id.lower().strip()  # Normalize badge ID
                version = version.strip()

                # Find the matching badge
                matching_badge = next(
                    (badge_data for badge_data in all_badges if badge_data["set_id"] == badge_id),
                    None
                )

                if matching_badge:
                    # Find the correct version
                    matching_version = next(
                        (version_data for version_data in matching_badge["versions"] if version_data["id"] == version),
                        None
                    )

                    if matching_version:
                        image_url = matching_version["image_url_1x"]
                        badge_urls.append(image_url)
                        print(f"Badge Found: {badge_id}, Version: {version}, URL: {image_url}")
                    else:
                        print(f"Badge Version Not Found: {badge_id}, Version: {version}")
                else:
                    print(f"Badge ID Not Found: {badge_id}")
            except ValueError as e:
                print(f"Error processing badge: {badge}, Error: {e}")

    return badge_urls


class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=OAUTH_TOKEN, prefix="?", initial_channels=["TodBenford"])
        self.broadcaster_id = None

    async def event_ready(self):
        """
        Triggered when the bot is successfully connected to Twitch.
        """
        print(f'Logged in as | {self.nick}')
        # Fetch the broadcaster ID when the bot is ready
        channel_name = self.connected_channels[0].name if self.connected_channels else None
        if channel_name:
            self.broadcaster_id = self.fetch_broadcaster_id(channel_name)
            print(f"Broadcaster ID: {self.broadcaster_id}")

    def fetch_broadcaster_id(self, channel_name):
        """
        Fetch the broadcaster's ID using the Twitch API.

        Parameters:
            channel_name (str): The name of the Twitch channel.

        Returns:
            str: The broadcaster's ID.
        """
        headers = {
            "Authorization": f"Bearer {OAUTH_TOKEN}",
            "Client-Id": CLIENT_ID,
        }
        response = requests.get(f"{BASE_URL}/users?login={channel_name}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["data"]:
                return data["data"][0]["id"]
        return None

    async def event_message(self, message):
        """
        Triggered whenever a new message is received in the chat.
        """
        if message.echo:
            return

        # Assign color: Default to random if empty
        color = message.tags.get("color", "").strip()
        if not color:
            color = get_random_color()

        # Fetch badge image URLs
        badges_string = message.tags.get("badges", "")
        badges = fetch_badge_urls(badges_string, self.broadcaster_id)

        # Extract message details
        chat_data = {
            "author": message.author.name,
            "content": message.content,
            "badges": badges,
            "color": color,  # Assign color dynamically
        }

        print(chat_data)  # Print the message details for debugging

        # Send the chat message to the server
        try:
            response = requests.post("https://chathihglight-2.onrender.com/api/chat", json=chat_data)
            if response.status_code == 200:
                print(f"Message sent: {chat_data}")
            else:
                print(f"Failed to send message: {response.status_code}")
        except Exception as e:
            print(f"Error sending message to server: {e}")


if __name__ == "__main__":
    bot = TwitchBot()
    asyncio.run(bot.run())
