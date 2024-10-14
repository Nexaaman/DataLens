import pandas as pd
from groq import Groq
from io import BytesIO
from dotenv import load_dotenv

class Insight():
    def __init__(self, file, question=None, sheet_name=None):
        if file.name.endswith('.csv'):
            self.df = pd.read_csv(BytesIO(file.getvalue()))
        elif file.name.endswith('.xlsx'):
            self.df = pd.read_excel(file, sheet_name=sheet_name, engine='openpyxl')

        self.columns_list = list(self.df.columns) if self.df is not None else []
        load_dotenv()
        self.client = Groq()

        
        self.insight_prompt = f"""
        You are a world-class data analyst. 
        Your task is to analyze the dataset and provide narrative insights based on the user's questions regarding trends and key information in the data. 
        Focus on generating a detailed, story-like response that explains the findings, rather than just presenting numbers or statistics. 
        Only return the insights based on your analysis of the data. 
        Columns available for analysis: `{self.columns_list}`. 
        The dataframe is referred to as `df`.
        """

        self.question = question if question else ""

    def generate_insights(self):
        if not self.question.strip():
            return None

        response = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {'role': "system", "content": self.insight_prompt},
                {'role': "user", "content": self.question}
            ], temperature=0
        )
        return response.choices[0].message.content

    def execute(self, st):
        insights = self.generate_insights()
        if not insights:
            st.warning("Question is missing or invalid. Please enter a valid question.")
            return

        
        st.subheader("Insights")
        st.write(insights)
