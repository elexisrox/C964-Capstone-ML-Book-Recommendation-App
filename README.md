# Book Recommendation System

## Overview
This project is a standalone book recommendation system built using Python, Jupyter Notebooks, and Tkinter. The system suggests books to users based on a title they input, using a machine learning model trained on a dataset from Kaggle.

## Setup Instructions

### Prerequisites
- Python 3.8 (or Anaconda with Python 3.8)
- Anaconda (recommended for simplified environment management)

### Setting Up the Environment

**1. Download and Install Anaconda:**
- Go to the [Anaconda website](https://www.anaconda.com/products/individual) and download the installer for your operating system.
- Run the installer and follow the instructions. You may see an option to "Register Anaconda3 as my default Python 3.12" when prompted. You will see a warning message if you already have Python 3.12 installed.

**2. Create a New Conda Environment:**
- Open Anaconda Prompt (or your terminal) and create a new environment:
   ```bash
   conda create --name book-recommender python=3.8
   ```
- Activate the environment:
   ```bash
   conda activate book-recommender
   ```

**3. Install Required Packages:**
- Install Jupyter Notebook and other necessary packages:
   ```bash
   conda install jupyter pandas numpy scikit-learn matplotlib seaborn
   ```

### Running the Jupyter Notebook
1. **Launch Jupyter Notebook:**
   ```bash
   jupyter notebook
   ```
   - This will open the Jupyter Notebook interface in your web browser.
  
2. **Open the Analysis Notebook**
   - Navigate to the 'notebooks' directory and open the 'analysis.ipynb' notebook.
   - Use the notebook to explore the data, train models, and visualize results.
  
### Running the Book Recommendation Tkinter Application
1. **Run the Book Recommendation Tkinter GUI:**
   - Navigate to the 'scripts' directory:
   ```bash
   cd scripts
   ```
   -Run the Tkinter application:
   ```bash
   python main.py
   ```

### Usage
**Jupyter Notebook**
- Use the notebook to explore the data, train models, and visualize results.
**Tkinter Application**
- Use the GUI to input a book title and get recommendations displayed interactively.

### License
This project was created by Elexis Rox, 2024, and is licensed under the MIT License.


   