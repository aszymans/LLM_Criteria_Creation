import os
import openai
import tqdm
import pandas as pd
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_prompt_only(instruction, model="gpt-4o"):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful and precise assistant that can create binary evaluation criteria for a given user instruction. Your task is to generate evaluation criteria for assessing a large language model's performance. Each criterion should be a statement in which you would answer true/false. The criteria should not be in the form of a question. You should return your final answer as a valid JSON object."},
            {"role": "user", "content": "Create evaluation criteria for the given prompt instruction.\n" + instruction}
        ]
    )
    return completion.choices[0].message.content

def generate_prompt_and_output(instruction, evaluation_criteria, output1, output2, output3, model="gpt-4o"):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful and precise assistant that can refine and create new binary evaluation criteria for a given user instruction and set out outputs. Your task is to generate evaluation criteria for assessing a large language model's performance. Each criterion should be a statement in which you would answer true/false. The criteria should not be in the form of a question. You should return your final answer as a valid JSON object."},
            {"role": "user", "content": f"Consider the initial evaluation criteria \n{evaluation_criteria}\n. After reviewing the outputs attached, either refine the intial criteria or create new evaluation criteria for the given prompt instruction and three outputs.\n{instruction}\n[The Start of Assistant 1’s Response] {output1} [The End of Assistant 1’s Response]\n[The Start of Assistant 2’s Response] {output2} [The End of Assistant 2’s Response]\n[The Start of Assistant 3’s Response] {output3} [The End of Assistant 3’s Response]"}
        ]
    )
    return completion.choices[0].message.content

def main():
    # Load the Excel file
    file_path = 'nutrition_instructions.xlsx'
    df = pd.read_excel(file_path)

    # Ensure all necessary columns are present
    if {'Prompts', 'Output 1', 'Output 2', 'Output 3'}.issubset(df.columns):
        model = "gpt-4o"

        # Processing each prompt
        for index, row in tqdm.tqdm(df.iterrows(), total=df.shape[0], desc="Processing Prompts"):
            prompt = row['Prompts']
            output1 = row['Output 1']
            output2 = row['Output 2']
            output3 = row['Output 3']

            # Generate outputs using both functions
            prompt_only_output = generate_prompt_only(prompt, model=model)
            prompt_and_output = generate_prompt_and_output(prompt, prompt_only_output, output1, output2, output3, model=model)

            # Add the results back into the DataFrame
            df.at[index, f'{model}_Output'] = prompt_only_output
            df.at[index, f'{model}_Prompt_and_Output'] = prompt_and_output

        # Save the results to a new Excel file
        output_file_path = 'LLM_criteria_nutrition3.xlsx'
        df.to_excel(output_file_path, index=False)
        return output_file_path
    else:
        print("The required columns are not present in the Excel file.")
        return None

if __name__ == "__main__":
    output_file_path = main()
    if output_file_path:
        print(f"Results saved to {output_file_path}")
    else:
        print("Processing failed due to missing columns.")