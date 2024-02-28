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
Pyinstaller --noconsole --add-data "Config.json;." --add-data "theme.json;." --add-data "static_files;static_files" --icon=window-icon.ico --hidden-import=tiktoken_ext.openai_public --hidden-import=tiktoken_ex .\main.py
```
The GUI window will open
## Python 3.10 Pyinstaller Compatibility Issue

**Description:**
If you're using Python 3.10, you might encounter a specific error related to the way instructions are analyzed `IndexError: tuple index out of range`.  Here's how to fix it:

**Instructions**
1. **Locate the `dis.py` file:**
   * Find your Python installation folder (e.g., `C:\Users\[YourUsername]\AppData\Local\Programs\Python\Python310\Lib`)
   * Open the `Lib` folder and locate the `dis.py` file.

2. **Edit the `dis.py` file:**
   * **Important:** Create a backup copy of `dis.py` before making changes.
   * Open `dis.py` in a text editor (make sure you have the permissions to edit files in this directory).
   * Find the `def _unpack_opargs` function.
   * Inside the `else` statement within this function, add the following line. Ensure correct indentation:

   ```python
   else:
       arg = None
       extended_arg = 0

## License

This project is licensed under the [MIT License](LICENSE).
