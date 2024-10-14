import streamlit as st
import pandas as pd
from visual import Visualizer
from insights import Insight

st.set_page_config(layout="wide")

def main():
    st.sidebar.title("File and Column Selection")
    sheet_name = None
    df = None

    st.title("DataLens")
    uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                excel_file = pd.ExcelFile(uploaded_file, engine='openpyxl')
                sheet_name = st.sidebar.selectbox("Select a sheet", excel_file.sheet_names)
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name, engine='openpyxl')

            
            st.write("Data Preview:")
            st.dataframe(df, use_container_width=True)

            
            columns = df.columns.tolist()
            selected_columns = st.sidebar.multiselect("Select the columns you want to visualize", columns)

            task_selection = st.sidebar.radio(
                "Select task:",
                ("Generate Visualization", "Question Answering (Insights)"),
                key="task_selection"
            )

            if "last_task_selection" not in st.session_state:
                st.session_state["last_task_selection"] = task_selection
            elif st.session_state["last_task_selection"] != task_selection:
                st.session_state["last_task_selection"] = task_selection
                st.rerun()

            user_prompt = None
            question = None

            if task_selection == "Generate Visualization":
                user_prompt = st.text_area("Enter your query for visualizations", 
                                           placeholder="E.g., Show me the distribution of selected columns")
            
            if task_selection in ["Question Answering (Insights)"]:
                question = st.text_area("Enter your question about the data insights",
                                        placeholder="E.g., Which department has the highest salary?")

            if st.button("Generate"):
                if task_selection in ["Generate Visualization"] and user_prompt and selected_columns:
                    columns_str = ", ".join(selected_columns)
                    full_prompt = f"{user_prompt} using the columns: {columns_str}"

                    try:
                        response_obj = Visualizer(uploaded_file, full_prompt, None, sheet_name=sheet_name)
                        response_obj.execute(st)
                        st.session_state["response_obj"] = response_obj
                    except Exception as e:
                        st.error(f"An error occurred while generating visualization: {str(e)}")

                if task_selection in ["Question Answering (Insights)"] and question:
                    try:
                        insight_obj = Insight(uploaded_file, question, sheet_name=sheet_name)
                        insight_obj.execute(st)
                    except Exception as e:
                        st.error(f"An error occurred while generating insights: {str(e)}")

        except Exception as e:
            st.error(f"An error occurred while reading the file: {str(e)}")
    else:
        st.info("Please upload a file to proceed.")

if __name__ == "__main__":
    main()
