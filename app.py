import streamlit as st
import os
from src.config.settings import GameSettings
from src.agents.crew import create_trivia_crew
# from src.utils.content_loader import ContentLoader  # Commented out content loader
from src.utils.chat_memory import ChatMemory
from typing import List, Dict
import json
import re
import random

# TODO REMOVE THIS
# import debugpy
# # Enable debugging at the start of the script
# if not debugpy.is_client_connected():
#     debugpy.listen(("localhost", 5679))  # Set the debugging port
#     st.write("Debugger is listening on port 5679...")
#     # Optional: Pause execution until debugger attaches
#     debugpy.wait_for_client()

#     st.title("Debugging Streamlit in VS Code")
#     st.write("This is a sample Streamlit app running in debug mode.")

#     # Example: Add a breakpoint manually
#     debugpy.breakpoint()  # Execution will pause here when debugger attaches

#     st.write("Debugging mode is active!")

# Initialize settings
settings = GameSettings()

#page config
st.set_page_config(
        page_title="AI Trivia Night",
        page_icon="🤖",
        layout="wide"
    )

# Initialize session state
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = ChatMemory()
# Content loader commented out
# if "content_loader" not in st.session_state:
#     st.session_state.content_loader = ContentLoader()
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None
if "previous_player" not in st.session_state:
    st.session_state.previous_player = None
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "game_started" not in st.session_state:
    st.session_state.game_started = False
if "current_player_index" not in st.session_state:
    st.session_state.current_player_index = 0
if "answers_submitted" not in st.session_state:
    st.session_state.answers_submitted = set()
if "question_number" not in st.session_state:
    st.session_state.question_number = 1
if "page_config_set" not in st.session_state:
    st.session_state.page_config_set = False
if "submit_answer" not in st.session_state:
    st.session_state.submit_answer = False
if "show_next_button" not in st.session_state:
    st.session_state.show_next_button = False


#Page config
# if "page_config_set" not in st.session_state:
#     st.set_page_config(
#         page_title="AI Trivia Night",
#         page_icon="🤖",
#         layout="wide"
#     )
#     st.session_state.page_config_set = True

# Sidebar
with st.sidebar:
    st.title("Game Settings")
    
    # API Key input
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    # Game configuration
    n_players = st.number_input(
        "Number of Players",
        min_value=settings.min_players,
        max_value=settings.max_players,
        value=2
    )
    
    player_names = []
    for i in range(n_players):
        name = st.text_input(f"Player {i+1} Name", value=f"Player {i+1}")
        player_names.append(name)
    
    difficulty = st.selectbox(
        "Difficulty Level",
        options=settings.difficulty_levels
    )
    
    categories = st.multiselect(
        "Categories",
        options=settings.categories,
        default=["Science", "History", "Technology", "Sports", "Entertainment", "General Knowledge", "Geography", "Literature", "Arts", "Artificial Intelligence", "LLMs", "Math"]
    )
    
    n_questions = st.number_input(
        "Questions per Game",
        min_value=1,
        max_value=20,
        value=settings.default_questions_per_game
    )

# Main content
st.title("🤖🧠 AI Trivia Game")

# Content ingestion section commented out
# with st.expander("Add Custom Content"):
#     content_type = st.selectbox(
#         "Content Type",
#         ["Web Page", "GitHub Repository", "PDF", "HTML"]
#     )
    
#     if content_type == "Web Page":
#         urls = st.text_area("Enter URLs (one per line)")
#         if st.button("Load Web Content") and urls:
#             with st.spinner("Loading web content..."):
#                 st.session_state.content_loader.load_web_content(urls.split("\n"))
#                 st.success("Content loaded successfully!")
    
#     elif content_type == "GitHub Repository":
#         repo_url = st.text_input("GitHub Repository URL")
#         branch = st.text_input("Branch", value="main")
#         if st.button("Load GitHub Content") and repo_url:
#             with st.spinner("Loading GitHub content..."):
#                 st.session_state.content_loader.load_github_content(repo_url, branch)
#                 st.success("Content loaded successfully!")

# Game interface
if not st.session_state.game_started:
    if st.button("Start Game"):
        if not api_key:
            st.error("Please enter your OpenAI API key first!")
        elif not categories:
            st.error("Please select at least one category!")
        else:
            st.session_state.game_started = True
            st.session_state.scores = {name: 0 for name in player_names}
            st.session_state.current_player_index = 0
            st.session_state.answers_submitted = set()
            st.session_state.question_number = 1
            st.rerun()

else:
    # Display scores and game status
    st.sidebar.markdown("## Current Scores")
    for player, score in st.session_state.scores.items():
        st.sidebar.markdown(f"**{player}:** {score}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Question:** {st.session_state.question_number}/{n_questions}")
    current_player = player_names[st.session_state.current_player_index]
    st.sidebar.markdown(f"**Current Turn:** {current_player}")
    
    # Generate and display question
    if not st.session_state.current_question:
        with st.spinner("Generating question..."):
            random.shuffle(categories)

            crew = create_trivia_crew(
                category=categories[0],  # TODO: Rotate categories
                difficulty=difficulty
            )
            result = crew.kickoff()
            # st.session_state.current_question = crew.kickoff()
            # st.write("Crew Result:", result)  # Print to Streamlit console
            # if 'question' and 'choices' and 'correct_answer' and 'explanation' in result:
            # st.write(type(result.raw))
            # st.write(result)
            # st.write(result.raw)
            
            
            clean_json_string = re.sub(r'^[^{]*|[^}]*$', '', result.raw, flags=re.DOTALL)
            parsed_result = json.loads(clean_json_string)
            
            st.session_state.current_question = {
                "question": str(parsed_result["question"]),
                "choices": [str(choice) for choice in parsed_result["choices"]],
                "correct_answer": str(parsed_result["correct_answer"]),
                "explanation": str(parsed_result["explanation"])
            }

           
    # Display question
    if st.session_state.current_question:
        # Create two columns for layout with more space for question/answers
        question_col, status_col = st.columns([3, 1])
        
        with question_col:
            # Question header with metadata
            # st.markdown("""
            # <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
            #     <h3 style='margin: 0;'>Question {}</h3>
            #     <p style='margin: 0.5rem 0;'><strong>Category:</strong> {} | <strong>Difficu
            # lty:</strong> {}</p>
            # </div>
            # """.format(st.session_state.question_number, categories[0], difficulty), unsafe_allow_html=True)
            st.markdown(f"**Question {st.session_state.question_number}: {categories[0]} | {difficulty}**")

            # Question text in a box
            # st.markdown("""
            # <div style='background-color: white; padding: 1.5rem; border-radius: 10px; border: 2px solid #e0e0e0; margin-bottom: 1.5rem;'>
            #     <h4 style='margin: 0;'>{}</h4>
            # </div>
            # """.format(st.session_state.current_question["question"]), unsafe_allow_html=True)
            question = st.session_state.current_question["question"]
            st.markdown(f"Question: {question}")

            # Combine and shuffle answers
            if "shuffled_answers" not in st.session_state:
                all_answers = st.session_state.current_question['choices']
                
                random.shuffle(all_answers)
                st.session_state.shuffled_answers = all_answers
            
            # Create numbered list of answers
            answer_options = {}
            for i, answer in enumerate(st.session_state.shuffled_answers, 1):
                answer_options[f"{i}. {answer}"] = answer

            # Display answer section with player's turn
            if len(st.session_state.answers_submitted) < len(player_names):
                # Show current player's turn
                st.markdown(f"""
                <div style='background-color: #e8f4ea; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                    <h3 style='margin: 0; color: #2e7d32;'>{current_player}'s Turn</h3>
                </div>
                """, unsafe_allow_html=True)

                # Create a container for answers
                answer_container = st.container()
                with answer_container:
                    # Split answers into two columns
                    left_col, right_col = st.columns([3, 2])
                    
                    with left_col:
                        # Display answer options
                        answer = st.radio(
                            "Choose your answer:",
                            options=list(answer_options.keys()),
                            key="answer_radio",
                            label_visibility="visible"
                        )
                    
                    with right_col:
                        # Show who has answered in a compact format
                        st.markdown("#### Players' Status")
                        for player in player_names:
                            if player in st.session_state.answers_submitted:
                                st.markdown(f"✅ {player}")
                            elif player == current_player:
                                st.markdown(f"👉 {player} (Current)")
                            else:
                                st.markdown(f"⏳ {player}")
                
                # Submit button centered below
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    # if not st.session_state.submit_answer:
                    if not st.session_state.submit_answer:
                        if st.button("Submit Answer", use_container_width=True):
                            st.session_state.submit_answer = True
                            st.session_state.selected_answer = answer_options[answer]
                            
                            # Check if answer is correct
                            if st.session_state.selected_answer == st.session_state.current_question["correct_answer"]:
                                st.success(f"🎉 Correct, {current_player}!")
                                st.session_state.scores[current_player] = st.session_state.scores.get(current_player, 0) + settings.points_per_difficulty.get("medium", 10)
                            else:
                                st.error(f"❌ Sorry {current_player}, that's incorrect. The correct answer is **{st.session_state.current_question['correct_answer']}**")
                            
                            # Show explanation
                            st.markdown(f"**Explanation:** {st.session_state.current_question['explanation']}")
                            
                            st.session_state.previous_player = current_player
                            # Mark player's answer as submitted
                            st.session_state.answers_submitted.add(current_player)

                            # Move to the next player
                            st.session_state.current_player_index = (st.session_state.current_player_index + 1) % len(player_names)
                            
                            # Enable the "Next Player" button
                            st.session_state.show_next_button = True

                            st.rerun()
                    else:
                        if st.session_state.submit_answer:
                            if st.session_state.selected_answer == st.session_state.current_question["correct_answer"]:
                                st.success(f"🎉 Correct, {st.session_state.previous_player}!")
                            else:
                                st.error(f"❌ Sorry {st.session_state.previous_player}, that's incorrect. The correct answer is **{st.session_state.current_question['correct_answer']}**")
                            st.markdown(f"**Explanation:** {st.session_state.current_question['explanation']}")
                            # Reset submission for next player
                            st.session_state.submit_answer = False
                            # st.rerun()  
                        # else:
                        #     st.write("You have already submitted an answer.")
        
        with status_col:
            # Show scores
            st.markdown("""
            <div style='background-color: #f8f9fa; padding: 0rem; border-radius: 8px; margin-bottom: 1rem;'>
                <h3 style='margin: 0 0 1rem 0;'>Scoreboard</h3>
            """, unsafe_allow_html=True)
            
            # Sort players by score
            sorted_scores = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
            for player, score in sorted_scores:
                st.markdown(f"**{player}:** {score}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Show results after all players have answered
            if len(st.session_state.answers_submitted) == len(player_names):
                st.markdown("---")
                correct_num = [i for i, opt in answer_options.items() 
                             if answer_options[opt] == st.session_state.current_question['correct_answer']][0]
                
                # Display correct answer and explanation in styled boxes
                st.markdown("""
                <div style='background-color: #e8f4ea; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                    <h4 style='margin: 0; color: #2e7d32;'>Correct Answer:</h4>
                    <p style='margin: 0.5rem 0; font-size: 1.1em;'>{}</p>
                </div>
                """.format(correct_num), unsafe_allow_html=True)
                
                st.markdown("""
                <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                    <h4 style='margin: 0 0 0.5rem 0;'>Explanation:</h4>
                    <p style='margin: 0;'>{}</p>
                </div>
                """.format(st.session_state.current_question['explanation']), unsafe_allow_html=True)
                
                # Next Question or End Game section
            st.markdown("---")
            if st.session_state.question_number < n_questions:
                if st.button("➡️ Next Question", key="next_question", use_container_width=True):
                    st.session_state.selected_answer = None
                    st.session_state.current_question = None
                    st.session_state.answers_submitted = set()
                    st.session_state.question_number += 1
                    if "shuffled_answers" in st.session_state:
                        del st.session_state.shuffled_answers
                    st.rerun()
            else:
                st.markdown("""
                <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                    <h3 style='margin: 0; text-align: center;'>🎯 Game Complete!</h3>
                </div>
                """, unsafe_allow_html=True)
                
                winner = max(st.session_state.scores.items(), key=lambda x: x[1])
                st.balloons()
                st.success(f"🏆 The winner is {winner[0]} with {winner[1]} points!")
                
                if st.button("🔄 Start New Game", use_container_width=True):
                    st.session_state.game_started = False
                    st.session_state.current_question = None
                    st.session_state.scores = {}
                    st.session_state.current_player_index = 0
                    st.session_state.answers_submitted = set()
                    st.session_state.question_number = 1
                    if "shuffled_answers" in st.session_state:
                        del st.session_state.shuffled_answers
                    st.rerun()
