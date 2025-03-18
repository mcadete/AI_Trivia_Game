from typing import List, Dict
from pydantic import BaseModel

class GameSettings(BaseModel):
    difficulty_levels: List[str] = [
        "High School",
        "College",
        "Graduate",
        "Expert",
        "Genius"
    ]
    
    categories: List[str] = [
        "Science",
        "History",
        "Literature",
        "Arts",
        "Technology",
        "Sports",
        "Geography",
        "Entertainment",
        "General Knowledge",
        "Math",
        "LLMs",
        "Artificial Intelligence"
    ]
    
    points_per_difficulty: Dict[str, int] = {
        "High School": 100,
        "College": 200,
        "Graduate": 300,
        "Expert": 400,
        "Genius": 500
    }
    
    max_players: int = 8
    min_players: int = 1
    default_questions_per_game: int = 10
    
    # AI Model settings
    default_model: str = "gpt-3.5-turbo"
    fallback_model: str = "gpt-4-turbo-preview"
    
    # Database settings
    chroma_persist_directory: str = ".chromadb"
    
    # Memory settings
    max_memory_items: int = 50 