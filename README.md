# GUI for Large Language Models API

This project is a graphical user interface (GUI) developed using PyQt6 for interacting with the Large Language Models API using Commands. The GUIto input text for processing by the API or Local LLM's.

## Prerequisites

Before running the GUI, make sure you have the following installed:

- Python 3.8 or above
- Large Language Models API credentials

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/haithemyoucefkhoudja/Quick-GPT.git  
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Set up the Large Language Models API credentials:

   - Obtain an API key from the Large Language Models API provider.
   - Create `.env` File
   - place the `API_KEY in .env` to start use it.
   
## Usage

To run the GUI, execute the following command:

```
python main.py
```

To create an executable app, you can run the following commands:

```
pip install pyinstaller
Pyinstaller --noconsole --add-data "Config.json;." --add-data "static_files;static_files" --icon=window-icon.ico --hidden-import=tiktoken_ext.openai_public --hidden-import=tiktoken_ex .\main.py
```
The GUI window will open

## License

This project is licensed under the [MIT License](LICENSE).
