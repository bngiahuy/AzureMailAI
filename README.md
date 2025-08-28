# Email Summarization Application

This application fetches the latest email from a user's Microsoft Graph mailbox, processes it, and generates a summary using Google Gemini LLM.

## Project Structure

- `config.py`: Configuration management using environment variables.
- `mail_client.py`: Handles Microsoft Graph API interactions for fetching and processing emails.
- `llm_client.py`: Manages interactions with Google Gemini LLM for summarization.
- `utils.py`: Utility functions, including a timer context manager.
- `main.py`: Main entry point that orchestrates the email fetching and summarization process.
- `llm_generate.py`: Backward compatibility wrapper for LLM invocation.

## Setup

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   - `AZURE_CLIENT_ID`: Your Azure app client ID
   - `AZURE_CLIENT_SECRET`: Your Azure app client secret
   - `AZURE_TENANT_ID`: Your Azure tenant ID
   - `GEMINI_API_KEY`: Your Google Gemini API key

3. Run the application:
   ```bash
   python main.py
   ```

## Features

- Fetches latest email from a specified user.
- Cleans and processes email content.
- Generates concise summaries using LLM.
- Includes timing for performance monitoring.
- Comprehensive error handling and logging.

## Refactoring Improvements

- **Separation of Concerns**: Split functionality into dedicated modules (config, mail client, LLM client, utils).
- **Environment Variables**: Moved hardcoded credentials to secure environment variables.
- **Error Handling**: Added proper exception handling and logging.
- **Type Safety**: Improved type hints and null checks.
- **Modularity**: Made code more reusable and maintainable.
- **Logging**: Replaced print statements with proper logging.
