# Personal Fitness Tracker 🏋️‍♂️

A comprehensive, AI-powered personal fitness and diet assistant built with Python. This application functions as a command-line tool, an intelligent backend, and an interactive web application, designed to provide personalized health and fitness plans.

![AI Fitness Tracker App Screenshot](<img width="1917" height="1022" alt="Screenshot 2025-08-31 104337" src="https://github.com/user-attachments/assets/0f439a98-55b2-44a4-ba4c-bca305c2a48d" />
) 

---

## About The Project

This project was developed as a multi-phase portfolio piece to build a lifelong personal assistant. It began as a simple command-line tool for logging workouts and meals and evolved into an intelligent system capable of generating complete, personalized transformation plans using the Google Gemini API. The final phase wrapped the entire backend in a user-friendly web interface built with Streamlit.

---

## Key Features ✨

* **Interactive Web UI**: A clean, multi-page web application built with Streamlit for easy data entry and visualization.
* **AI-Powered Nutrition Analysis**: Automatically calculates nutritional information for meals using the Gemini API.
* **Personalized Plan Generation**: A sophisticated two-step AI process that first assesses the feasibility of a user's fitness goals and then generates a realistic, tailored meal and exercise plan.
* **Data Logging & Viewing**: Simple forms and displays for logging and reviewing workout and meal history.
* **Robust Backend**: A solid SQLite database and a modular, reusable Python backend that also functions as a standalone CLI tool.

---

## Built With 🛠️

* **[Python](https://www.python.org/)**
* **[Streamlit](https://streamlit.io/)** - The web application framework.
* **[Google Gemini API](https://ai.google.dev/)** - For all AI-powered features.
* **[SQLite](https://www.sqlite.org/index.html)** - For the local database.
* **[Argparse](https://docs.python.org/3/library/argparse.html)** - For the command-line interface.

---

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Python 3.8+
* pip

### Installation

1.  **Clone the repo**
    ```sh
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/Shanin-Raj/Fitness_Tracker.git)
    cd your-repo-name
    ```
    2.  **Install required packages**
    ```sh
    pip install -r requirements.txt
    ```

3.  **Set up your API Key**
    * Copy the example config file: `cp config.py.example config.py` (on Windows, use `copy config.py.example config.py`).
    * Open `config.py` and add your Google Gemini API key.

4.  **Set up the Database**
    * Run the database setup script once to create the `.db` file.
    ```sh
    python database_setup.py
    ```

---

## Usage 🚀

To run the web application, use the following command:

```sh
streamlit run app.py
