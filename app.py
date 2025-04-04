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
                parsed_obj.pop("description", None)  # Skip 'description' key if present
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
    
    # Highlight filled and empty values
    def highlight_values(row):
        colors = [""]  # Keep Story Number column uncolored
        for val in row[1:]:
            if val == "N/A":
                colors.append("background-color: lightgrey")  # Mark N/A as grey
            else:
                colors.append("background-color: lightgreen")  # Mark filled values as green
        return colors
    
    styled_df = df.style.apply(highlight_values, axis=1)
    
    return styled_df, df

st.set_page_config(page_title="Fact Comparison by Field", layout="wide")
st.sidebar.title("Fact Comparison by Field")

st.title("LLM Output Comparator")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    parsed_data, fields = parse_json(df)
    print (df)
    
    # Summary Table
    st.subheader("Summary of Facts Count")
    summary_data = {}
    for field in fields:
        _, field_df = field_level_view(parsed_data, field)
        summary_data[field] = field_df.iloc[:, 1:].apply(lambda col: (col != "N/A").sum()).to_dict()
    
    summary_df = pd.DataFrame(summary_data).T
    st.dataframe(summary_df)
    
    # Field Level View for all fields
    st.subheader("Field Level View for All Fields")
    for field in fields:
        st.write(f"### Field: {field}")
        styled_df, field_df = field_level_view(parsed_data, field)
        st.dataframe(styled_df)
        
        # Count non-NA values
        non_na_counts = field_df.iloc[:, 1:].apply(lambda col: (col != "N/A").sum())
        st.write("#### Count of Non-NA Values:")
        st.write(non_na_counts.to_frame().T)
