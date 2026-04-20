# 🔬 Prompt Improvement Workbench

An AI-powered prompt evaluation tool built with Python, Streamlit, and the Claude API.
Write a prompt and a second Claude instance grades it across 5 dimensions and rewrites it for you.

## 📸 Screenshot

<img width="1651" height="816" alt="image" src="https://github.com/user-attachments/assets/b0ab35f3-4147-4f84-9619-119f11c495c9" />

<img width="1090" height="1015" alt="image" src="https://github.com/user-attachments/assets/b92c0c84-aa71-4238-bab8-40a4bee115ee" />

<img width="1015" height="1063" alt="image" src="https://github.com/user-attachments/assets/2099159e-817c-4fdb-8fa8-067bc5b3975b" />

## 💡 What It Does

- User selects a preset analytics task or writes their own custom task
- User submits a prompt they want to test against that task
- **Claude Instance 1** executes the prompt and generates a response
- **Claude Instance 2** (the grader) evaluates the quality of the original prompt
- The grader returns a structured report including an overall grade, dimension scores,
  what worked, improvement suggestions, and a fully rewritten improved prompt
- Supports fully custom tasks: bring your own task, expected solution, and prompt

## 🧠 Key Concepts Practiced

- **LLM-as-a-Judge** pattern. Using one Claude call to evaluate the output of another
- Designing two distinct system prompts for two different roles in the same app
- Passing structured context (task + prompt + response + expected solution) to a grader model
- Building a reusable `call_claude()` function shared across multiple workflows
- Preset scenario design for consistent, repeatable prompt evaluation

## 🔁 How It Works

User Prompt
│
▼
Claude Instance 1 (Analytics Assistant)
│ generates a response
▼
Claude Instance 2 (Grader)
│ receives: task + expected solution + prompt + response
▼
Structured Evaluation Report
│
├── Overall Grade (A / B / C / D / F)
├── Dimension Scores (1-10 each)
├── What Worked
├── Improvement Suggestions
└── Revised Prompt


