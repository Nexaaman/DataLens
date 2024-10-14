import pandas as pd
from groq import Groq
import matplotlib.pyplot as plt
from io import BytesIO
from dotenv import load_dotenv
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # To prevent GUI windows from popping up in non-interactive environments

class Visualizer():
    def __init__(self, file, user_prompt=None, question=None, sheet_name=None):
        if file.name.endswith('.csv'):
            self.df = pd.read_csv(BytesIO(file.getvalue()))
        elif file.name.endswith('.xlsx'):
            self.df = pd.read_excel(file, sheet_name=sheet_name, engine='openpyxl')
        
        self.columns_list = list(self.df.columns) if self.df is not None else []
        
        load_dotenv()

        self.client = Groq()

        self.system_prompt = f"""
        You are a world-class data analyst. 
        Your task is to write Python code to create visualizations from the data based on the user's query. 
        You will be provided with the list of column names from a CSV or Excel file. 
        Use these columns to write the code. 
        The list of columns is enclosed between two backticks (''). 
        Columns are: '{self.columns_list}'. 
        IMPORTANT: Always refer to the dataframe as 'df' and only use the provided column names. 
        IMPORTANT: Do not create new dataframes or read CSV/Excel files. Assume 'df' already exists and contains the data. 
        IMPORTANT: Only output the Python code necessary for visualization, nothing else. 
        IMPORTANT: Do not initialize a web server or Flask application. Only create plots using Matplotlib and Seaborn.
        """

        self.user_prompt = user_prompt if user_prompt else ""

    def response(self):
        if not self.user_prompt.strip():
            return None

        response = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {'role': "system", "content": self.system_prompt},
                {'role': 'user', "content": self.user_prompt}
            ], temperature=0
        )
        return response.choices[0].message.content

    def remove_code_fence(self):
        code = self.response()
        if not code:
            return None
        cleaned_code = code.strip().lstrip('```python').rstrip('```').strip()
        return cleaned_code

    def execute(self, st):
        cleaned_code = self.remove_code_fence()
        if not cleaned_code:
            st.warning("User prompt is missing or invalid. Please enter a valid query.")
            return
        
        local_namespace = {}
        try:
            exec(cleaned_code, {'df': self.df, 'plt': plt, 'sns': sns, 'pd':pd}, local_namespace)

            figures = [plt.figure(fig_num) for fig_num in plt.get_fignums()]
            if not figures:
                st.warning("No figures were generated!")
                return

            for fig in figures:
                st.pyplot(fig)
            plt.close("all")
        except Exception as e:
            st.error(f"An error occurred during code execution: {str(e)}")

