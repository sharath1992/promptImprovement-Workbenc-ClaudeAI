import anthropic
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── 1. ANTHROPIC CLIENT ───────────────────────────────────────────────
client = anthropic.Anthropic()

# ── 2. SYSTEM PROMPTS ─────────────────────────────────────────────────
# Handles the actual task
SYSTEM_PROMPT = """
        You are an expert analytics assistant with deep knowledge of 
        SQL, Python, Tableau, and data analysis workflows.
        
        Your job is to respond to the user's prompt as faithfully and 
        specifically as possible. Do not add caveats or explanations 
        unless asked. Just solve the task.
    """

# Evaluates the quality of the user's prompt across 5 dimensions
GRADER_SYSTEM_PROMPT = """
        You are an expert analytics prompt evaluator.
        You will be given:
            1. A task description
            2. The prompt that was tested
            3. The response that was generated from that prompt

        Evaluate the prompt (NOT the response) across these dimensions:
            - Correctness:        Did the response actually solve the task?
                                  If not, was the prompt too vague to guide it there?
            - Specificity:        Did the prompt produce precise output or 
                                  generic generalities?
            - Assumption Handling: Did the prompt leave dangerous gaps?
            - Reproducibility:    Would a different model or run produce
                                  a wildly different answer from this prompt?
            - Edge Case Awareness: Did the response account for NULLs, 
                                  duplicates, date boundaries, or other
                                  analytics data quality issues? If not,
                                  did the prompt fail to ask for it?

        Return your evaluation in this exact structure:
            - Overall Grade:          A / B / C / D / F
            - Dimension Scores:       Score (1-10) + onex line reason for each dimension
            - What Worked:            2-3 things the prompt did well
            - Improvement Suggestions: Specific rewrites, not generic advice
            - Revised Prompt:         An improved version of the original prompt
"""

# ── 3. HELPER FUNCTIONS ───────────────────────────────────────────────
# Shared API call used by both generateResponse and grader
def call_claude(system_prompt: str, messages: list) -> str:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=system_prompt,
        messages=messages
    )
    return message.content[0].text

# Sends the user's prompt to Claude and returns the task, prompt, and response as a dict
def generateResponse(taskDescription: str, userPrompt: str) -> dict:
    local_messages = [{"role": "user", "content": userPrompt}]
    claude_response = call_claude(SYSTEM_PROMPT, local_messages)
    
    return {
        "task": taskDescription,
        "prompt": userPrompt,
        "response": claude_response
    }

# Takes the output of generateResponse and grades the quality of the original prompt
def grader(generateOutput: dict, expectedSolution: str):
    taskDescription = generateOutput["task"]
    userPrompt = generateOutput["prompt"]
    response = generateOutput["response"]

    # Bundles all context into a single message for the grader
    graderUserMessage = f"""
                        Task Description: {taskDescription},
                        Expected Solution: {expectedSolution}
                        User Prompt: {userPrompt},
                        Response: {response}
                        """
    local_messages = [{"role": "user", "content": graderUserMessage}]
    graderOutput = call_claude(GRADER_SYSTEM_PROMPT, local_messages)

    return graderOutput

# ── 4. PAGE CONFIG ────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Prompt Improvement Workbench"
)

# ── 5. FIXED HEADER ───────────────────────────────────────────────────
st.markdown("""
    <style>
        header[data-testid="stHeader"] {
        background-color: transparent;
    }
            
        .fixed-header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999;
            background-color: black;
            padding: 16px 2.5rem 12px 2.5rem;
            border-bottom: 1px solid #e0e0e0;
        }
        .fixed-header h1 {
            margin: 0 0 4px 0;
            font-size: 2rem;
        }
        .fixed-header p {
            margin: 0;
            color: #666;
            font-size: 0.95rem;
        }
        .block-container {
            padding-top: 160px !important;
        }
    </style>

    <div class="fixed-header">
        <h1>🔬 Prompt Improvement Workbench</h1>
        <p>Test and improve your analytics prompts using AI-powered evaluation</p>
    </div>
""", unsafe_allow_html=True)

# ── 6. PRESET SCENARIOS ───────────────────────────────────────────────
# Built-in tasks with a weak prompt and expected solution for grading
scenarios = {
    "Task 1 - Top 5 Customers by Purchase": {
        "task": "Write a SQL query to find the top 5 customers by total purchase amount in the last 30 days, excluding any cancelled orders.",
        "expected_solution": "A SQL query that uses SUM to aggregate purchase amounts, filters records to the last 30 days using a date condition, excludes cancelled orders using a WHERE clause, groups by customer, and uses ORDER BY with LIMIT 5.",
        "user_prompt": "Write a SQL query to get the top customers by purchases."
    },
    "Task 2 - Stock Price Moving Average": {
        "task": "Write a Python script to read a CSV file of daily stock prices and calculate the 30-day moving average, then identify the top 3 days where the price crossed above the moving average.",
        "expected_solution": "A Python script using pandas that reads a CSV, computes a 30-day rolling mean, compares daily price against the moving average to identify upward crossovers specifically, and returns the top 3 crossover dates sorted by the magnitude of the crossover.",
        "user_prompt": "Write Python code to calculate a moving average on stock prices and find crossover points."
    }
}

# ── 7. TASK SELECTOR ──────────────────────────────────────────────────
options = st.selectbox(
    "Select a Task (optional)",
    list(scenarios.keys()) + ["Custom - write your own"],
    index=None,
    placeholder="Select a task or write your own...",
)

# Stop rendering until the user makes a selection
if not options:
    st.stop()
elif options == "Custom - write your own":
    # Free-text inputs for fully custom evaluation
    taskDescription = st.text_area("Write your own custom task:")
    expected_soln = st.text_area("Write your expected solution:")
    userPrompt = st.text_area("Write your prompt:")
else:
    # Pre-fill fields from the selected scenario
    taskDescription = scenarios[options]["task"]
    expected_soln = scenarios[options]["expected_solution"]
    userPrompt = scenarios[options]["user_prompt"]
    st.text_area("Task Description", value=taskDescription, disabled=True)
    st.text_area("Your Prompt Being Tested", value=userPrompt, disabled=True)

# ── 8. EVALUATE BUTTON ────────────────────────────────────────────────
if st.button("Evaluate Prompt"):
    if not taskDescription or not expected_soln or not userPrompt:
        st.warning("Please enter a task, expected solution and prompt before evaluating:")
    else:
        with st.spinner("Evaluating your prompt..."):
            try:
                # Step 1: generate a response from the user's prompt
                result = generateResponse(taskDescription, userPrompt)
                # Step 2: grade the prompt based on the response and expected solution
                grade = grader(result, expected_soln)
                st.divider()
                st.subheader("📊 Evaluation Results")
                st.chat_message("assistant").write(grade)
            except anthropic.AuthenticationError:
                st.error("API key not found or invalid. Set ANTHROPIC_API_KEY in your environment.")
            except anthropic.RateLimitError:
                st.error("Rate limit hit. Please wait a moment and try again.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")