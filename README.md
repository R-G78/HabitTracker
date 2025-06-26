

# Stoics - Habit Tracker

A minimalist CLI habit tracker inspired by Stoic philosophy — designed to help you build consistency, reflect on discipline, and master your daily and weekly rituals.

⸻

 ## What is this?

This is a command-line interface (CLI) habit tracker built in Python. It allows you to:

	•	Create habits with a periodicity: daily, weekly, or monthly
	•	Check off completed habits (with built-in constraints to   prevent over-checking)
	•	View your current streak, longest streak, and streak breaks
	•	Analyse your progress per habit
	•	Track all your habits in an embedded SQLite database
	•	Run automated tests to validate behavior

All from your terminal — no fluff, just structure.

⸻

## Why Stoicism?

“We are what we repeatedly do. Excellence, then, is not an act, but a habit.”
— Will Durant (paraphrasing Aristotle)

Stoicism emphasizes self-mastery, discipline, and intentional daily action. This tracker reflects that philosophy:
It’s not about tracking everything, it’s about tracking what matters — and doing it consistently.

⸻

## Installation
	1.	Clone the repository:

`git clone`

	2.	Install dependencies:

`pip install -r requirement.txt`

## Usage

To start the app, run:

`python main.py` 

You’ll be guided through the available actions via an interactive menu:
	•	Add new habits
	•	Check off habits
	•	Analyse progress
	•	View habit lists
	•	Delete or reset habits

All data is stored locally in habits.db.

### Predefined Habits

To get started quickly, the app can load 5 predefined habits. These include:
	•	Daily habits (e.g., Drink water)
	•	Weekly habits (e.g., Workout)
	•	Monthly habits (e.g., Pay bills)

If you want to preload these habits into your database (for demo or testing), you can run:

` python seed.py`

(Or: enable populate_demo_habits() on first run — see main.py)

### Creating a New Habit

To add your own custom habit:
	1.	Run python main.py
	2.	Select “Add a new habit”
	3.	Enter:
		•	The name of the habit (e.g., “Read 10 pages”)
		•	The periodicity:
		•	daily
		•	weekly
		•	monthly

### Checking Off a Habit

To mark a habit as completed:
	1.	Run python main.py
	2.	Select “Check off a habit”
	3.	Pick the habit you want to complete

The app enforces frequency rules:
	•	Daily habits can only be checked off once per day
	•	Weekly habits only once per week
	•	Monthly habits only once per calendar month

If you try to check off a habit again in the same period, the system will prevent it.

### Analysis

You can also:
	•	Analyze specific habits
	•	View longest streaks
	•	Identify how often you broke your streak

Select “Analyse a specific habit” or “Longest overall habit streak” from the main menu to view insights.
⸻

## Running Tests

This app comes with a full test suite using pytest.

To run all tests:

`pytest` 

Tests use a temporary in-memory database and cover:
	•	Habit creation and deletion
	•	Completion constraints (e.g., no double-checks in same period)
	•	Streak calculations
	•	Analysis logic

⸻

This is a simple but powerful tool for anyone who values discipline, reflection, and consistency.

Track less. Do more. Repeat.


