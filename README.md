PROJECT SYNOPSIS: AI-BASED MILITARY INTELLIGENCE DASHBOARD

1. Project Overview & Abstract
The AI-Based Military Intelligence Dashboard is an interactive web-based analytics and machine learning application designed to analyze historical conflict data from the Global Terrorism Database (GTD). The platform processes over 180,000 incident records to deliver geospatial visualization, tactical attack predictions, regional risk classification, and long-term threat forecasting for strategic decision-making.

2. Core Modules & Functionality

Executive Home & Overview: Provides top-level KPIs (incidents, casualties, attack success rates) alongside dual-axis temporal trend lines and regional threat breakdowns.

Geospatial GIS Threat Map: Interactive 2D and 3D orthographic map projections with dynamic performance-sampling to render spatial incident density without browser latency.

Country-Level Intelligence Brief: Comparative metric scorecards, top perpetrator profiles, and targeted sector distributions filtered by nation and time range.

Attack Type Prediction Engine: Machine learning classification module using a trained Random Forest model (~86% accuracy) to predict tactical attack categories based on operational inputs.

AI Threat Level Classifier: Evaluates operational threat levels (Low, Medium, High) based on casualty impact indicators and spatial attributes using a Random Forest model.

Trend Forecasting Engine: Time-series analysis utilizing Linear Regression to project future incident volumes and calculate projected growth trajectories.

Automated AI Intelligence Summary & Data Explorer: Generates structured executive intelligence briefings and provides multi-variable dataset filtering and CSV exports.

3. Technology Stack

Programming Language: Python 3.x

User Interface Framework: Streamlit

Data Engineering: Pandas, NumPy

Machine Learning & Modeling: Scikit-Learn (Random Forest, Linear Regression), Joblib

Data Visualization & GIS: Plotly Express, Plotly Graph Objects

4. Key Results & Performance Metrics

Model Accuracy: ~85.88% test accuracy achieved on multi-class attack type prediction.

Performance Optimization: Integrated @st.cache_data and memory downsampling to render high-volume spatial data smoothly.
