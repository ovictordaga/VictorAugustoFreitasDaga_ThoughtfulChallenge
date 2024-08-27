
# Thoughtful AI - Tech Challenge by Victor Augusto Freitas Daga

## Overview

This project is part of a technical challenge for Thoughtful AI, aiming to showcase the ability to automate the process of extracting data from a news site. The automation is built using Robocorp and is designed to streamline tedious but essential business processes through Robotic Process Automation (RPA).

## The Challenge

The objective of this challenge is to build a bot that can:

1. **Extract Data from a News Site**: Automate the process of navigating the site, performing searches, and gathering relevant news articles.
2. **Store Data**: Save the extracted information in an organized manner, preferably in an Excel file, stored in the `/output` directory so that it is accessible in the Robocorp Control Room artifacts list.
3. **Implement Additional Features**:
   - Count the occurrences of the search phrases within the articles.
   - Detect and extract monetary amounts mentioned in the content.
4. **Deploy and Test**: Push the code to this GitHub repository and create a Robocorp Control Room process. Ensure that the process has a successful run before submission.

## Setup Instructions

### Prerequisites

- Robocorp Lab installed.
- Python environment set up with necessary dependencies.
- A Robocorp Control Room account.

### Installation

1. **Clone this Repository:**
   ```bash
   git clone https://github.com/ovictordaga/VictorAugustoFreitasDaga_ThoughtfulChallenge.git
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Up in Robocorp Lab:**
   - Open the project in Robocorp Lab.
   - Ensure all dependencies are correctly installed.

## Usage

### Running Locally

You can test the bot locally using the following command:

```bash
rcc run
```

### Deploying to Robocorp Control Room

1. **Push to GitHub:**
   Ensure that your latest code is pushed to this repository.

2. **Create a Process in Robocorp Control Room:**
   - Create a new process in Robocorp Control Room linked to this GitHub repository.
   - Define parameters such as `search_phrase`, `news_category`, and `time_period`.

3. **Execute the Process:**
   Run the process from Robocorp Control Room, ensuring a successful run.

4. **Submission:**
   Once the process has successfully run, invite `Challenges@thoughtfulautomation.com` to your Robocorp Org to review the solution.

## Project Structure

- **`tasks.py`**: Main script containing the bot logic, including payload management and news scraping functionality.
- **`/output`**: Directory where the extracted data will be stored.



## License

This project is licensed under the MIT License.
