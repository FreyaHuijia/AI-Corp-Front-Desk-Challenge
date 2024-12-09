Flask App Instructions

General Notes for Running this Flask App

To run the tool locally, download the code and follow the steps below:

1. Open Command Prompt: Change the directory to the project folder:
   ```bash
   cd <folder_path>
   ```

2. Ensure Python Version: Make sure your Python version is >= 3.12.

3. Set Up a Virtual Environment:
   - For Windows:
     ```bash
     python -m venv .venv
     .venv\Scripts\activate.bat
     ```
   - For macOS:
     ```bash
     pip install virtualenv
     virtualenv .venv
     source .venv/bin/activate
     ```
   - Note: ".venv" is the name of the environment; you can use any name you prefer.

4. Install Dependencies: Once the virtual environment is active, install the required packages (only if you are running the app for the first time or if there are changes in `requirements.txt`):
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` File: This file will store all the environment variables for Flask, Hugging Face, OpenAI, and Langchain. Copy the following code into the `.env` file:
   ```plaintext
   FLASK_APP=app
   FLASK_RUN_PORT=8080
   FLASK_DEBUG=True
   HF_TOKEN=""
   OPENAI_API_KEY=""
   ```

6. Run the Application: Start the Flask application using the following command:
   ```bash
   flask run
   ```

## Additional Information

- Ensure that you have the necessary API keys for Hugging Face and OpenAI in your `.env` file.
- If you encounter any issues, check the console for error messages and ensure all dependencies are correctly installed.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the contributors and libraries that made this project possible.