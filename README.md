# AI-Powered Trivia Game

An intelligent trivia game powered by OpenAI, CrewAI, and LangChain. This application creates dynamic, engaging trivia questions across various difficulty levels and categories, perfect for game nights and educational settings.

## Features

- Dynamic question generation using OpenAI and CrewAI agents
- Multiple difficulty levels (High School to Expert)
- Various knowledge categories
- Chat interface with memory
- Content ingestion from multiple sources:
  - Web pages
  - PDF documents
  - GitHub repositories
  - Google Scholar articles
- Knowledge base storage using ChromaDB
- Conversation history tracking

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_key_here
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Enter your OpenAI API key in the sidebar
2. Select game settings:
   - Number of players
   - Difficulty level
   - Categories
   - Question count
3. Start the game and take turns answering questions
4. View scores and track progress

## Deployment

This application is hosted on Hugging Face Spaces. Visit [insert-your-space-url] to play! 