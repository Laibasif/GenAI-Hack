import json
import re
import requests
import google.generativeai as genai

class MemeGenerator:
    def __init__(self):
        GENAI_API_KEY = "AIzaSyAnfEvhg0Uz6Oahgvyoyy1FLGIWKzd6LhI"  # Replace with your actual Gemini API key
        genai.configure(api_key=GENAI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        self.imgflip_username = 'ManuAdam'
        self.imgflip_password = 'Cyberme@50'
        self.model = model

    def extract_json_from_output(self, llm_output: str) -> dict:
        """
        Extracts the JSON from the LLM output based on the defined structure.

        Parameters:
            llm_output (str): The string output from the LLM.

        Returns:
            dict: The extracted JSON as a Python dictionary.
        """
        try:
            
            # Use regex to locate the JSON structure in the output
            json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # Parse the JSON string into a Python dictionary
                
                
                return json.loads(json_str)
            else:
                raise ValueError("No JSON structure found in the output.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    def generate_meme_post(self, content, tone):
        """
        Generate meme top and bottom text dynamically based on content and tone.
        
        :param content: The content to use for meme generation.
        :param tone: The desired tone of the meme.
        :return: A dictionary with 'top_text' and 'bottom_text'.
        """
        try:
            prompt = f"""
            Role: Expert MEME generator from content
            Task: generate a meme top text and bottom text from the content below.

            Desired Tone: {tone}

            Content:
                {content}

            Instructions:
            - Always return a JSON format.

            Output:
            {{
                "top_text": "",
                "bottom_text": ""
            }}
            """

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            return self.extract_json_from_output(response_text)

        except Exception as e:
            print(f"Error generating meme post: {e}")
            return {"top_text": "Error", "bottom_text": "Error"}

    def create_meme(self, template_id, content, tone):
        """
        Create a meme using Imgflip API with dynamic text generation.

        :param template_id: ID of the meme template.
        :param content: The content to generate the meme text from.
        :param tone: The desired tone of the meme.
        :return: URL of the generated meme.
        """
        # Generate meme text
        meme_text = self.generate_meme_post(content, tone)
        top_text = meme_text.get("top_text", "Default Top Text")
        bottom_text = meme_text.get("bottom_text", "Default Bottom Text")

        # Prepare Imgflip API payload
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
