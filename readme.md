
# Automotive Sales & Financial Forecasting Dashboard 🚗

This project provides an end-to-end solution for cleaning financial data, generating time-series forecasts, and visualizing the results in an interactive web dashboard. It uses Python with Pandas for data manipulation, Prophet for forecasting, and Streamlit for the user interface.


## ✨ Features

* **Automated Data Cleaning**: Ingests raw CSV data and performs cleaning, standardization, and aggregation to create a reliable master dataset.
* **Time-Series Forecasting**: Utilizes Facebook's Prophet library to generate monthly forecasts for every financial KPI in the dataset.
* **Interactive Dashboard**: A web-based dashboard built with Streamlit to explore historical data and future predictions.
* **KPI Deep Dive**: Select any KPI to view a detailed chart comparing historical performance against the forecast, including confidence intervals.
* **Scenario Planning Tool**: Interactively model how a percentage change in a "Driver KPI" (e.g., Total Vehicle Sales) could impact a related "Impacted KPI" (e.g., Total Gross Profit) based on their historical correlation.

## 📂 Project Structure


├── FS-data-80475.csv           
 Raw input data file
 
├── sales-prediction.ipynb      
#Jupyter Notebook for data processing, EDA, and model training

├── dashboard.py               
 The Streamlit dashboard application script
 
├── requirements.txt      

Python dependencies for the project

└── README.md                


After running the pipeline, the following files will be generated:
* `cleaned_master_data.csv`: The cleaned and aggregated data, ready for analysis.
* `forecast_master_data.csv`: The final output containing historical data and future predictions for all KPIs.

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

* Python 3.8+
* `pip` package manager

### 1. Clone the Repository

Clone this repository to your local machine:
```bash
git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd your-repository-name
2. Set Up a Virtual Environment
It's highly recommended to create and activate a virtual environment to manage project dependencies.

Bash

# For macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# For Windows
python -m venv .venv
.venv\Scripts\activate
3. Install Dependencies
Install all the required Python libraries using the requirements.txt file.

Bash

pip install -r requirements.txt
⚙️ How to Run the Project
The project runs in two main steps: first, you run the data processing and forecasting pipeline, and second, you launch the interactive dashboard.

Step 1: Run the Data & Forecasting Pipeline
Open and run all the cells in the sales-prediction.ipynb Jupyter Notebook. This script will:

Load the raw FS-data-80475.csv file.

Clean and Aggregate the data, saving the result to cleaned_master_data.csv.

Train a Prophet forecasting model for every KPI.

Save the final predictions to forecast_master_data.csv.

Step 2: Launch the Dashboard
Once the forecast_master_data.csv file has been generated, you can launch the Streamlit dashboard. Run the following command in your terminal:

Bash

streamlit run dashboard.py
Your web browser should automatically open to the dashboard's local URL (usually http://localhost:8501).

📊 Using the Dashboard
Key Financial Forecast: The top section provides a quick glance at the predicted values for the next three months for primary KPIs like Gross Profit and Sales.

Scenario Planner: Use the sidebar controls under "Scenario Planning" to select a Driver KPI and an Impacted KPI. Adjust the slider to see how a change in the driver's forecast could potentially affect the other KPI.


KPI Deep Dive: In the sidebar, select any KPI from the dropdown menu to view its detailed historical vs. forecast performance chart and a bar chart of its 3-month forecast.




