// Get the elements
const generateButton = document.getElementById('generate-button');
const userInput = document.getElementById('user-input');
const toneSelect = document.getElementById('tone');
const contentTypeSelect = document.getElementById('content-type');
const outputContainer = document.getElementById('output-container');

// Event listener for the Generate button
generateButton.addEventListener('click', function () {
    const userPrompt = userInput.value.trim();
    const selectedTone = toneSelect.value;
    const selectedContentType = contentTypeSelect.value;

    if (userPrompt === '') {
        alert('Please enter a prompt.');
        return;
    }

    // Generate content based on user input
    let generatedContent = `Prompt: ${userPrompt}<br>`;
    generatedContent += `Tone: ${selectedTone}<br>`;
    generatedContent += `Content Type: ${selectedContentType}<br><br>`;

    // Display generated content
    generatedContent += `<strong>Generated Content:</strong><br>`;
    generatedContent += `This is where your content would appear based on your input.`;
    
    outputContainer.innerHTML = generatedContent;
});
