from google import genai
from app.core.config import GEMINI_API_KEY

# Create Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Send request using the current Interactions API
interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input="Explain RAG in one simple sentence."
)

print("\nGemini Response:")
print(interaction.output_text)