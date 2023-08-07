# GUI for Large Language Models API

This project is a graphical user interface (GUI) developed using PyQt6 for interacting with the Large Language Models API. The GUI allows users to upload documents and use a voice recorder to input text data for processing by the API.
## Donation
Donate Bitcoin:
```markdown
[<img src="https://s18955.pcdn.co/wp-content/uploads/2018/02/github.png" width="25"/>](https://www.blockonomics.co/pay-url/aac9917abdc443b4)
```
## Features
- Chromadb Vectore Store: Users can store their PDF locally without needing third party DB

- Upload Documents: Users can select and upload documents to be processed by the Large Language Models API. The uploaded documents can be in PDF.

- Voice Recorder: The GUI includes a voice recorder feature that allows users to record their voice and convert it into text. This text data can then be sent to the Large Language Models API for processing.

- Customization: You can edit largelanguagemodel.py to fit your needs make sure to keep pysignal!
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
   - Replace the placeholder `API_KEY` in Settings panel to start use it.

## Usage

To run the GUI, execute the following command:

```
python QuickGPT.py
```

To create an executable app, you can run the following commands:

```
pip install pyinstaller
Pyinstaller --noconsole --icon=quick-gpt-logo.ico --hidden-import=tiktoken_ext.openai_public --hidden-import=tiktoken_ex .\QuickGPT.py
```

The GUI window will open, providing options for uploading documents and using the voice recorder. Follow the on-screen instructions to interact with the GUI and utilize the features.

## Contributing

Contributions are welcome! If you have any suggestions or improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

```
