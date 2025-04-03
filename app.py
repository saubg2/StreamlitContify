import streamlit as st
import pandas as pd
import json

def load_data(file):
    df = pd.read_csv(file)
    return df

def parse_json(df):
    parsed_data = {}
    fields = set()
    for model in df.columns:
        parsed_data[model] = []
        for x in df[model]:
            try:
                json_str = x.replace("'", '"')  # Fix single quotes issue
                parsed_obj = json.loads(json_str)
                parsed_data[model].append(parsed_obj)
                fields.update(parsed_obj.keys())
            except json.JSONDecodeError:
                parsed_data[model].append({})  # Handle malformed JSON
    return parsed_data, sorted(fields)

def field_level_view(parsed_data, field):
    result = {"Story Number": list(range(len(next(iter(parsed_data.values())))))}
    for model, responses in parsed_data.items():
        result[model] = [response.get(field, "N/A") for response in responses]
    return pd.DataFrame(result)

st.title("LLM Output Comparator")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    parsed_data, fields = parse_json(df)
    
    # Field Level View for all fields
    st.subheader("Field Level View for All Fields")
    for field in fields:
        st.write(f"### Field: {field}")
        field_df = field_level_view(parsed_data, field)
        st.dataframe(field_df)
