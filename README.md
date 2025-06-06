# Quiz to Anki Converter

This application converts multiple choice quiz questions into Anki flashcards.

## Requirements

- Python 3.6+
- Required packages (listed in requirements.txt)

## Installation

1. Clone or download this repository
2. Install the required packages:

```
pip install -r requirements.txt
```

## Usage

1. Prepare your quiz questions in a text file following this format:

```
Q1: Question text here?
A) Option A
B) Option B
C) **Correct Answer**
D) Option D

Q2: Next question here?
...
```

Note: Mark the correct answer with ** (double asterisks) surrounding it.

2. Run the script:

```
python quiz_to_anki.py
```

By default, the script will read questions from `sample_questions.txt` and generate `flashcards.apkg`.

3. Import the generated .apkg file into Anki:
   - Open Anki
   - Click "File" > "Import"
   - Select the generated .apkg file

## Customization

You can modify the script to:
- Use a different input file
- Customize the output filename
- Add explanations to questions
- Change the formatting of the cards

## License

MIT