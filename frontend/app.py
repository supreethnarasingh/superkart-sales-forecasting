import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend inside the Docker network
BACKEND_URL = "http://backend:7860"

st.set_page_config(page_title="SuperKart Sales Forecasting System", layout="wide")

st.title("🛒 SuperKart Sales Forecasting")
st.write("Enter product and store characteristics below to obtain instant forecast predictions or perform batch forecasts using a CSV file.")

tab1, tab2 = st.tabs(["Single Prediction", "Batch Forecast"])

with tab1:
    st.header("Single Product Sales Forecast")
    col1, col2 = st.columns(2)
    
    with col1:
        Product_Weight = st.number_input("Product Weight (kg)", min_value=0.0, value=12.66, step=0.1)
        Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        Product_Allocated_Area = st.number_input("Product Allocated Area Ratio", min_value=0.0, max_value=1.0, value=0.027, format="%.3f")
        Product_MRP = st.number_input("Product Maximum Retail Price (MRP)", min_value=0.0, value=117.08, step=0.5)
        Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        
    with col2:
        Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
        Store_Type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
        Product_Id_char = st.selectbox("Product ID Characters", ["FD", "DR", "NC"])
        Store_Age_Years = st.number_input("Store Age (Years)", min_value=0, value=16)
        Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

    if st.button("Forecast Sales", type="primary"):
        payload = {
            "Product_Weight": Product_Weight,
            "Product_Sugar_Content": Product_Sugar_Content,
            "Product_Allocated_Area": Product_Allocated_Area,
            "Product_MRP": Product_MRP,
            "Store_Size": Store_Size,
            "Store_Location_City_Type": Store_Location_City_Type,
            "Store_Type": Store_Type,
            "Product_Id_char": Product_Id_char,
            "Store_Age_Years": Store_Age_Years,
            "Product_Type_Category": Product_Type_Category
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload)
            if response.status_code == 200:
                result = response.json()
                st.success(f"🎯 Projected Product Store Sales Total: ₹{result['Sales']:.2f}")
            else:
                st.error(f"Error from backend: HTTP {response.status_code}")
        except Exception as e:
            st.error(f"Unable to connect to the Flask prediction backend: {e}")

with tab2:
    st.header("Bulk / Batch Sales Forecast")
    st.write("Upload a CSV file containing the features required by the forecasting model.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        if st.button("Perform Batch Prediction", type="primary"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch",
                    files={"file": uploaded_file}
                )
                if response.status_code == 200:
                    results = response.json()
                    st.success("Batch forecast execution completed successfully!")
                    
                    # Parse results to a readable format
                    results_df = pd.DataFrame(list(results.items()), columns=["Row Index", "Forecasted Sales (₹)"])
                    st.dataframe(results_df, use_container_width=True)
                else:
                    st.error(f"Backend returned error state: HTTP {response.status_code}")
            except Exception as e:
                st.error(f"Unable to establish API connection: {e}")
