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
        if model.lower() == "description":  # Ignore description column
            continue
        parsed_data[model] = []
        for x in df[model]:
            try:
                json_str = x.replace("'", '"')  # Fix single quotes issue
                parsed_obj = json.loads(json_str)
                parsed_data[model].append(parsed_obj)
                fields.update(parsed_obj.keys())
            except json.JSONDecodeError:
                parsed_data[model].append({})  # Handle malformed JSON
    fields.discard("description")  # Ensure 'description' field is not processed
    return parsed_data, sorted(fields)

def field_level_view(parsed_data, field):
    result = {"Story Number": list(range(len(next(iter(parsed_data.values())))))}
    for model, responses in parsed_data.items():
        result[model] = [response.get(field, "N/A") for response in responses]
    df = pd.DataFrame(result)
    
    # Highlight discrepancies
    def highlight_differences(row):
        unique_values = row[1:].unique()  # Ignore Story Number column
        colors = [""]  # Keep Story Number column uncolored
        for val in row[1:]:
            if val == "N/A":
                colors.append("background-color: lightgrey")
            elif len(unique_values) == 1:
                colors.append("background-color: lightgreen")  # All values match
            else:
                colors.append("background-color: lightpink")  # Values differ (changed to light pink)
        return colors
    
    styled_df = df.style.apply(highlight_differences, axis=1)
    
    return styled_df

st.title("LLM Output Comparator")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    parsed_data, fields = parse_json(df)
    
    # Field Level View for all fields
    st.subheader("Field Level View for All Fields")
    for field in fields:
        if field.lower() == "description":  # Do not display table for description field
            continue
        st.write(f"### Field: {field}")
        field_df = field_level_view(parsed_data, field)
        st.dataframe(field_df)
