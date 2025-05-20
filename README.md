## **SER Credit Rating – Interim Thesis Submission**

Description

This repository contains the **\*\*interim submission\*\*** of Tiantian Zhang's Master's thesis at the **\*\*University of Groningen (2025)\*\***.    
The project explores the use of **\*\*Speech Emotion Recognition (SER)\*\*** for correlating **\*\*credit ratings\*\*** based on acoustic and semantic features extracted from speech.

---
## **Directory Structure**

ser\_credit\_rating/  
 ├── features/ \# Feature extraction modules  
 │ └── semantic/ \# Scripts for semantic features (e.g., embeddings, models)  
 ├── ratings/ \# Utilities related to processing credit ratings  
 ├── scripts/ \# Training, evaluation, and data preprocessing scripts  
 ├── requirements.txt \# Python dependencies used in this project  
 ├── .gitignore \# Files and folders ignored by Git  
 └── README.md \# Project overview and usage instructions


---

## **Requirements**

This project requires Python 3.12 and the packages listed in requirements.txt.    
Main dependencies include:

transformers ≥ 4.52.0  
datasets ≥ 3.6.0  
torch  
pandas ≥ 2.2.3  
numpy ≥ 2.2.6  
tqdm  
matplotlib ≥ 3.10.3  
pydub  
opensmile (for audio feature extraction)

Install them all with:

pip install \-r requirements.txt

---

## **How to Run**

### **1\. Clone the repository**

git clone https://github.com/anit-z/thesis-interim-submission.git  
cd thesis-interim-submission

### **2\. Create and activate a virtual environment (optional but recommended)**

python3 \-m venv venv  
source venv/bin/activate

### **3\. Install dependencies**

pip install \-r requirements.txt

### **4\. Run a script (example)**


python scripts/your\_script.py

Replace `your_script.py` with the actual script name you want to execute.

---

## **Project Highlights**

* Utilizes both **acoustic** (e.g., low-level descriptors via openSMILE) and **semantic** (e.g., transformer embeddings) features from speech.  
* Combines speech signals with financial indicators.  
* Modular codebase: allows easy experimentation with different models and features.

---

## **License**

This interim codebase is licensed under the **Apache License 2.0**.

**Note:** Future versions may be subject to different licensing considerations.  


---


## **🏫 Acknowledgements**

This repository is part of an academic thesis submitted to the **University of Groningen**.  
 Thanks to all supervisors, peers, and contributors who supported the research and development process.


