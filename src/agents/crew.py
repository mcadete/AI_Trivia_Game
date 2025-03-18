from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from typing import List, Dict

class TriviaCrewAgents:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.7
        )
    
    def create_question_master(self) -> Agent:
        return Agent(
            role='Question Master',
            goal='Create engaging and accurate trivia questions',
            backstory="""You are an expert at creating challenging and interesting
            trivia questions. You have deep knowledge across multiple fields and
            can adjust difficulty levels appropriately.""",
            llm=self.llm,
            verbose=True
        )
    
    def create_fact_checker(self) -> Agent:
        return Agent(
            role='Fact Checker',
            goal='Verify accuracy of questions and answers',
            backstory="""You are a meticulous researcher who verifies the accuracy
            of trivia questions and answers. You have access to various knowledge
            sources and ensure all information is correct.""",
            llm=self.llm,
            verbose=True
        )
    
    def create_difficulty_calibrator(self) -> Agent:
        return Agent(
            role='Difficulty Calibrator',
            goal='Ensure questions match intended difficulty level',
            backstory="""You are an expert at assessing the difficulty of questions
            and ensuring they match the intended level, from high school to genius.""",
            llm=self.llm,
            verbose=True
        )

class TriviaTaskCreator:
    @staticmethod
    def create_question_generation_task(
        agent: Agent,
        category: str,
        difficulty: str,
        context: str = ""
    ) -> Task:
        return Task(
            description=f"""Create a challenging trivia question in the {category} category
            at {difficulty} difficulty level. If context is provided, incorporate it naturally.
            Context: {context}
            
            The question should be formatted as a dictionary with these keys:
            - question: the actual question text
            - choices: list of 4 multiple choices for the correct answer
            - correct_answer: the correct answer
            - explanation: detailed explanation of the correct answer
            """,
            expected_output="""A JSON string containing a dictionary with the following structure:
            {
                "question": "The question text",
                "choices": ["Choice 1", "Choice 2", "Choice 3", "Choice 4"],
                "correct_answer": "The correct answer",
                "explanation": "Detailed explanation of why the correct answer is correct"
            }""",
            agent=agent
        )
    
    @staticmethod
    def create_validation_task(
        agent: Agent,
        question_data: Dict
    ) -> Task:
        return Task(
            description=f"""Verify the accuracy of this trivia question and its answers:
            {question_data}
            
            Check for:
            1. Factual accuracy
            2. Clear and unambiguous wording
            3. One definitively correct answer
            4. Plausible incorrect answers
            5. Accurate explanation
            
            Return the validated question or suggest corrections.""",
            expected_output="""A JSON string containing the validated or corrected question with the following structure:
            {
                "question": "The verified question text",
                "choices": ["Choice 1", "Choice 2", "Choice 3", "Choice 4"],
                "correct_answer": "The verified correct answer",
                "explanation": "Verified explanation"
            }""",
            agent=agent
        )

def create_trivia_crew(
    category: str,
    difficulty: str,
    context: str = "",
    model_name: str = "gpt-3.5-turbo"
) -> Crew:
    # Initialize agents
    agents = TriviaCrewAgents(model_name)
    question_master = agents.create_question_master()
    fact_checker = agents.create_fact_checker()
    difficulty_calibrator = agents.create_difficulty_calibrator()
    
    # Create tasks
    tasks = [
        TriviaTaskCreator.create_question_generation_task(
            question_master, category, difficulty, context
        ),
        TriviaTaskCreator.create_validation_task(
            fact_checker,
            "{{question_master_output}}"
        )
    ]
    
    # Create and return crew
    return Crew(
        agents=[question_master, fact_checker, difficulty_calibrator],
        tasks=tasks,
        verbose=True
    ) 