import requests
import os

class ContentGenerator:
    def __init__(self, tavus_api_key, imgflip_username, imgflip_password):
        """
        Initialize the Content Generator with Tavus API key and Imgflip credentials

        :param tavus_api_key: Tavus API key for video generation
        :param imgflip_username: Imgflip API username
        :param imgflip_password: Imgflip API password
        """
        self.tavus_api_key = tavus_api_key
        self.imgflip_username = imgflip_username
        self.imgflip_password = imgflip_password

    def generate_video_with_tavus(self, script, replica_id, background_url='', video_name='generated_video'):
        """
        Generate a video using Tavus API

        :param script: Text script for the video
        :param replica_id: ID of the video replica/avatar
        :param background_url: Optional background URL
        :param video_name: Name for the generated video
        :return: Response from Tavus API
        """
        url = "https://tavusapi.com/v2/videos"

        payload = {
            "background_url": background_url,
            "replica_id": replica_id,
            "script": script,
            "video_name": video_name
        }

        headers = {
            "x-api-key": self.tavus_api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)

            # Check if request was successful
            if response.status_code == 200:
                response_data = response.json()
                print("Video generation request successful:")
                print(f"Video ID: {response_data.get('video_id')}")
                print(f"Status: {response_data.get('status')}")
                return response_data
            else:
                print(f"Video generation failed. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except requests.RequestException as e:
            print(f"Error in video generation: {e}")
            return None

    def create_meme(self, template_id, top_text, bottom_text):
        """
        Create a meme using Imgflip API

        :param template_id: ID of the meme template
        :param top_text: Text to display at the top of the meme
        :param bottom_text: Text to display at the bottom of the meme
        :return: URL of the generated meme
        """
        imgflip_url = 'https://api.imgflip.com/caption_image'

        payload = {
            'template_id': template_id,
            'username': self.imgflip_username,
            'password': self.imgflip_password,
            'text0': top_text,
            'text1': bottom_text
        }

        try:
            response = requests.post(imgflip_url, data=payload)
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    meme_url = result['data']['url']
                    print(f"Meme generated successfully: {meme_url}")
                    return meme_url
                else:
                    print(f"Meme generation failed: {result.get('error_message', 'Unknown error')}")
                    return None
            else:
                print(f"Meme API request failed. Status code: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error creating meme: {e}")
            return None
