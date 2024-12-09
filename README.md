# Content Generation API

A FastAPI-based project to generate content in various formats (text, meme, or video) with customizable tone settings (conversational, formal, or humorous).

## Setup Instructions

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
2. Install the required dependencies:
 - pip install -r requirements.txt
 - Running the FastAPI Server
 - Start the server using the following command:

4. uvicorn app.main:app --reload
 - The server will run on the default URL:
 - http://127.0.0.1:8000/
 - Using the Application
 - Open your web browser and navigate to the root URL:
 - http://127.0.0.1:8000/
   
5. Enter the required details:

 - Prompt: Provide a text prompt for content generation.
 - Tone: Select the desired tone:
   - Conversational
   - Formal
   - Humorous
 - Output Type: Choose the type of output:
   - Text
   - Post
   - Meme
   - Video
     
  - Click the Generate button to generate the content.

6. Expected Output
  The application will process your input and generate the specified content based on the selected parameters. If an error occurs during generation, an appropriate error message will be displayed.
  
  Additional Notes
  Ensure that the backend server is running before interacting with the frontend.
  If you encounter any issues, check the server logs for detailed error messages.
