import streamlit as st
import pandas as pd
import ast


def load_data(file):
    df = pd.read_csv(file, skipinitialspace=True, engine='python')
    return df


def parse_json(df):
    parsed_data = {}
    fields = set()
    
    for model in df.columns:
        if model.lower() in ["description", "story number"]:
            continue  # Skip description and story number columns

        parsed_data[model] = []
        for x in df[model]:
            if pd.isna(x):
                parsed_data[model].append({})
                continue

            try:
                parsed_obj = ast.literal_eval(x)
                if isinstance(parsed_obj, dict):
                    # Skip inner 'description' key
                    parsed_obj.pop("description", None)
                    parsed_data[model].append(parsed_obj)
                    fields.update(k for k in parsed_obj.keys() if k != "description")
                else:
                    parsed_data[model].append({})
            except Exception:
                parsed_data[model].append({})

    return parsed_data, sorted(fields)


def field_level_view(parsed_data, field):
    result = {"Story Number": list(range(len(next(iter(parsed_data.values())))))}
    for model, responses in parsed_data.items():
        result[model] = [response.get(field, "N/A") for response in responses]

    df = pd.DataFrame(result)

    def highlight_values(row):
        colors = [""]
        for val in row[1:]:
            if val == "N/A":
                colors.append("background-color: lightgrey")
            else:
                colors.append("background-color: lightgreen")
        return colors

    styled_df = df.style.apply(highlight_values, axis=1)
    return styled_df, df


# Streamlit UI
st.set_page_config(page_title="Fact Comparison by Field", layout="wide")
st.sidebar.title("Fact Comparison by Field")

st.title("LLM Output Comparator")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    parsed_data, fields = parse_json(df)
    st.write("Raw Uploaded Data")
    st.dataframe(df)

    st.subheader("Summary of Facts Count")
    summary_data = {}
    for field in fields:
        _, field_df = field_level_view(parsed_data, field)
        summary_data[field] = field_df.iloc[:, 1:].apply(lambda col: (col != "N/A").sum()).to_dict()

    summary_df = pd.DataFrame(summary_data).T
    st.dataframe(summary_df)

    st.subheader("Field Level View for All Fields")
    for field in fields:
        st.write(f"### Field: {field}")
        styled_df, field_df = field_level_view(parsed_data, field)
        st.dataframe(styled_df)

        non_na_counts = field_df.iloc[:, 1:].apply(lambda col: (col != "N/A").sum())
        st.write("#### Count of Non-NA Values:")
        st.write(non_na_counts.to_frame().T)
