#!/usr/bin/env python3
import genanki
import random
import argparse
import re
import html

class MCQConverter:
    def __init__(self, deck_name="Multiple Choice Questions"):
        self.deck_id = random.randrange(1 << 30, 1 << 31)
        self.deck = genanki.Deck(self.deck_id, deck_name)
        
        # Define the model for AllInOne card type
        self.model = genanki.Model(
            random.randrange(1 << 30, 1 << 31),
            'AllInOne (kprim, mc, sc)',
            fields=[
                {'name': 'Title'},           # Always blank
                {'name': 'Question'},        # Question text
                {'name': 'Q type'},          # Always "2" for single choice
                {'name': 'Q_1'},             # First option
                {'name': 'Q_2'},             # Second option
                {'name': 'Q_3'},             # Third option
                {'name': 'Q_4'},             # Fourth option
                {'name': 'Q_5'},             # Fifth option (optional)
                {'name': 'Answers'},         # Solution string (e.g., "0 1 0 0 0")
                {'name': 'ShuffleOrder'},    # Field to store shuffle order
                {'name': 'selected-option'}, # Store user's selection
            ],
            templates=[{
                'name': 'Card 1',
                'qfmt': '''
                    <div class="question">{{Question}}</div>
                    <div id="options-container">
                        {{#Q_1}}<div class="option-wrapper" data-index="0" onclick="ankiSelectOption(0)">
                            <div class="option">A) {{Q_1}}</div>
                        </div>{{/Q_1}}
                        {{#Q_2}}<div class="option-wrapper" data-index="1" onclick="ankiSelectOption(1)">
                            <div class="option">B) {{Q_2}}</div>
                        </div>{{/Q_2}}
                        {{#Q_3}}<div class="option-wrapper" data-index="2" onclick="ankiSelectOption(2)">
                            <div class="option">C) {{Q_3}}</div>
                        </div>{{/Q_3}}
                        {{#Q_4}}<div class="option-wrapper" data-index="3" onclick="ankiSelectOption(3)">
                            <div class="option">D) {{Q_4}}</div>
                        </div>{{/Q_4}}
                    </div>
                    <div id="selected-option" style="display:none;">{{selected-option}}</div>
                    <div id="answers" style="display:none;">{{Answers}}</div>
                    
                    <script>
                    function checkAnswer(index) {
                        var answersStr = document.getElementById('answers').textContent.trim();
                        var answers = answersStr.split(" ");
                        return answers[index] === "1";
                    }

                    function showFeedback(isCorrect) {
                        var feedbackDiv = document.createElement('div');
                        feedbackDiv.className = 'answer-feedback';
                        feedbackDiv.textContent = isCorrect ? '✓ Correct!' : '✗ Incorrect';
                        feedbackDiv.style.backgroundColor = isCorrect ? '#4CAF50' : '#f44336';
                        document.body.appendChild(feedbackDiv);
                    }

                    function ankiSelectOption(index) {
                        var allOptions = document.querySelectorAll('.option-wrapper');
                        allOptions.forEach(opt => opt.className = 'option-wrapper');
                        
                        var selected = document.querySelector(`.option-wrapper[data-index="${index}"]`);
                        if (selected) {
                            var isCorrect = checkAnswer(index);
                            selected.className = `option-wrapper ${isCorrect ? 'selected-correct' : 'selected-incorrect'}`;
                            
                            showFeedback(isCorrect);
                            
                            if (!isCorrect) {
                                // Show correct answer
                                var answers = document.getElementById('answers').textContent.trim().split(" ");
                                answers.forEach((ans, i) => {
                                    if (ans === "1") {
                                        var correct = document.querySelector(`.option-wrapper[data-index="${i}"]`);
                                        if (correct) correct.className += ' correct';
                                    }
                                });
                            }
                            
                            var hidden = document.getElementById('selected-option');
                            if (hidden) hidden.textContent = index;
                        }
                    }
                    
                    // Function to shuffle an array
                    function shuffleArray(array) {
                        for (let i = array.length - 1; i > 0; i--) {
                            const j = Math.floor(Math.random() * (i + 1));
                            [array[i], array[j]] = [array[j], array[i]];
                        }
                        return array;
                    }
                    
                    // Function to rebuild options with new random order
                    function rebuildOptions() {
                        const optionsContainer = document.getElementById('options-container');
                        
                        // Get all answer fields
                        const answerFields = Array.from(document.querySelectorAll('.answer-field'))
                            .map(field => ({ 
                                text: field.getAttribute('data-value'),
                                index: Array.from(field.parentNode.children).indexOf(field)
                            }));
                        
                        // Shuffle the answer fields
                        shuffleArray(answerFields);
                        
                        // Clear container
                        optionsContainer.innerHTML = '';
                        
                        // Create new options in random order
                        answerFields.forEach((field, i) => {
                            const wrapper = document.createElement('div');
                            wrapper.className = 'option-wrapper';
                            wrapper.setAttribute('data-index', field.index);
                            wrapper.onclick = function() { ankiSelectOption(field.index); };
                            
                            const option = document.createElement('div');
                            option.className = 'option';
                            option.innerHTML = String.fromCharCode(65 + i) + ') ' + field.text;
                            
                            wrapper.appendChild(option);
                            optionsContainer.appendChild(wrapper);
                        });
                        
                        // Store and save the shuffle order
                        var order = Array.from(document.querySelectorAll('.option-wrapper'))
                            .map(opt => opt.getAttribute('data-index'));
                        localStorage.setItem(cardID, order.join(','));
                    }
                    
                    // Function to check if answer is correct
                    function checkAnswer(index) {
                        var answersStr = document.getElementById('answers').textContent.trim();
                        var answers = answersStr.split(" ");
                        return answers[index] === "1";
                    }
                    
                    // Function to show feedback
                    function showFeedback(isCorrect) {
                        // Remove existing feedback
                        var existing = document.querySelectorAll('.answer-feedback');
                        existing.forEach(el => el.remove());
                        
                        // Create feedback element
                        var feedback = document.createElement('div');
                        feedback.className = 'answer-feedback';
                        if (isCorrect) {
                            feedback.innerHTML = '✓ Correct!';
                            feedback.style.backgroundColor = '#4CAF50';
                        } else {
                            feedback.innerHTML = '✗ Incorrect';
                            feedback.style.backgroundColor = '#f44336';
                        }
                        document.body.appendChild(feedback);
                    }
                    
                    // Function to handle option selection
                    function ankiSelectOption(index) {
                        // Remove all selections
                        var allOptions = document.querySelectorAll('.option-wrapper');
                        allOptions.forEach(opt => {
                            opt.className = 'option-wrapper';
                        });
                        
                        // Add selected class and check answer
                        var selected = document.querySelector(`.option-wrapper[data-index="${index}"]`);
                        if (selected) {
                            var isCorrect = checkAnswer(index);
                            selected.className = 'option-wrapper ' + 
                                (isCorrect ? 'selected-correct' : 'selected-incorrect');
                            
                            // Store selection
                            var hidden = document.getElementById('selected-option');
                            if (hidden) {
                                hidden.textContent = index;
                            }
                            
                            showFeedback(isCorrect);
                            
                            // If incorrect, show correct answer
                            if (!isCorrect) {
                                var answers = document.getElementById('answers').textContent.trim().split(" ");
                                answers.forEach((ans, i) => {
                                    if (ans === "1") {
                                        var correct = document.querySelector(`.option-wrapper[data-index="${i}"]`);
                                        if (correct) {
                                            correct.className += ' correct';
                                        }
                                    }
                                });
                            }
                        }
                    }
                    
                    // Initialize on load
                    document.addEventListener('DOMContentLoaded', function() {
                        rebuildOptions();
                    });
                    </script>
                ''',
                'afmt': '''
                    {{FrontSide}}
                    <hr id="answer">
                    <script>
                    // Automatically show correct answer on the back
                    (function() {
                        var answers = document.getElementById('answers').textContent.trim().split(" ");
                        answers.forEach((ans, i) => {
                            if (ans === "1") {
                                var correct = document.querySelector(`.option-wrapper[data-index="${i}"]`);
                                if (correct) correct.className += ' correct';
                            }
                        });
                        
                        // If an option was selected, show it
                        var selected = document.getElementById('selected-option');
                        if (selected && selected.textContent) {
                            ankiSelectOption(parseInt(selected.textContent));
                        }
                    })();
                    </script>
                '''
            }],
            css='''
                .card {
                    font-family: Arial, sans-serif;
                    font-size: 16px;
                    text-align: left;
                    color: black;
                    background-color: white;
                    padding: 20px;
                }
                .question {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }
                #options-container {
                    margin-top: 20px;
                }
                .option-wrapper {
                    margin: 8px 0;
                    padding: 12px 15px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    background-color: white;
                }
                .option-wrapper:hover {
                    background-color: #f5f5f5;
                    border-color: #bbb;
                    transform: translateY(-1px);
                }
                .option-wrapper.correct {
                    background-color: #e8f5e9;
                    border-color: #4caf50;
                    color: #2e7d32;
                }
                .option-wrapper.selected-correct {
                    background-color: #81c784;
                    border-color: #4caf50;
                    color: white;
                    font-weight: bold;
                }
                .option-wrapper.selected-incorrect {
                    background-color: #ffcdd2;
                    border-color: #e57373;
                    color: #c62828;
                }
                .answer-feedback {
                    position: fixed;
                    bottom: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    padding: 12px 24px;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    z-index: 1000;
                    animation: fadeIn 0.3s ease;
                }
                @keyframes fadeIn {
                    from { opacity: 0; transform: translate(-50%, 10px); }
                    to { opacity: 1; transform: translate(-50%, 0); }
                }
            '''
        )

    def parse_mcq_line(self, line):
        """Parse a single MCQ line from Anki export format."""
        parts = line.split('\t')
        if len(parts) != 2:
            return None
        
        question_part, correct_answer = parts
        
        # Split the HTML parts
        parts = [p.strip() for p in question_part.split('<br>') if p.strip()]
        if len(parts) < 5:  # Need at least question + 4 options
            return None
            
        # First part is the question
        question = parts[0]
        # Rest are options
        options = parts[1:][:4]  # Take only first 4 options
        
        # Find which option is correct
        correct_index = next((i for i, opt in enumerate(options) if opt.strip() == correct_answer.strip()), 0)
        
        # Create the answers string (e.g., "0 1 0 0" where 1 marks correct answer)
        answers = ['1' if i == correct_index else '0' for i in range(len(options))]
        
        return {
            'question': question,
            'options': options,
            'answers': ' '.join(answers)
        }

    def convert_file(self, input_file):
        """Convert an Anki export file to a new MCQ deck."""
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Skip header lines starting with #
        content_lines = [line for line in lines if not line.startswith('#')]

        for line in content_lines:
            line = line.strip()
            if not line:
                continue
                
            mcq = self.parse_mcq_line(line)
            if mcq:
                note = genanki.Note(
                    model=self.model,
                    fields=[
                        '',                             # Title
                        html.escape(mcq['question']),   # Question
                        '1',                            # Q type (1 for multiple choice)
                        html.escape(mcq['options'][0]), # Q_1
                        html.escape(mcq['options'][1]), # Q_2
                        html.escape(mcq['options'][2]), # Q_3
                        html.escape(mcq['options'][3]), # Q_4
                        '',                             # Q_5
                        mcq['answers'],                 # Answers
                        '',                             # ShuffleOrder
                        ''                              # selected-option
                    ]
                )
                self.deck.add_note(note)

    def save_deck(self, output_file):
        """Save the deck to an .apkg file."""
        genanki.Package(self.deck).write_to_file(output_file)

def main():
    parser = argparse.ArgumentParser(description='Convert Anki export to MCQ deck')
    parser.add_argument('input_file', help='Input text file (Anki export)')
    parser.add_argument('output_file', help='Output .apkg file')
    parser.add_argument('--deck-name', default='Multiple Choice Questions',
                      help='Name for the Anki deck')
    
    args = parser.parse_args()
    
    converter = MCQConverter(deck_name=args.deck_name)
    converter.convert_file(args.input_file)
    converter.save_deck(args.output_file)
    print(f"Successfully created Anki deck: {args.output_file}")

if __name__ == '__main__':
    main()
