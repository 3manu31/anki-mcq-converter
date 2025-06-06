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
                        <!-- Options will be dynamically generated and shuffled -->
                    </div>
                    <div id="selected-option" style="display:none;">{{selected-option}}</div>
                    <div id="answers" style="display:none;">{{Answers}}</div>
                    
                    <!-- Hidden option data -->
                    <div style="display:none;" id="option-data">
                        <div data-index="0">{{Q_1}}</div>
                        <div data-index="1">{{Q_2}}</div>
                        <div data-index="2">{{Q_3}}</div>
                        <div data-index="3">{{Q_4}}</div>
                    </div>
                    
                    <script>
                    // Shuffle array function
                    function shuffleArray(array) {
                        const shuffled = [...array];
                        for (let i = shuffled.length - 1; i > 0; i--) {
                            const j = Math.floor(Math.random() * (i + 1));
                            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
                        }
                        return shuffled;
                    }
                    
                    // Initialize options with shuffle
                    function initializeOptions() {
                        const container = document.getElementById('options-container');
                        const optionData = document.getElementById('option-data');
                        const options = Array.from(optionData.children).filter(el => el.textContent.trim() !== '');
                        
                        // Create option objects with original indices
                        const optionObjects = options.map((el, i) => ({
                            text: el.textContent.trim(),
                            originalIndex: parseInt(el.getAttribute('data-index')),
                            displayIndex: i
                        }));
                        
                        // Shuffle the options
                        const shuffledOptions = shuffleArray(optionObjects);
                        
                        // Clear container and add shuffled options
                        container.innerHTML = '';
                        shuffledOptions.forEach((option, i) => {
                            const wrapper = document.createElement('div');
                            wrapper.className = 'option-wrapper';
                            wrapper.setAttribute('data-index', option.originalIndex);
                            wrapper.onclick = function() { ankiSelectOption(option.originalIndex); };
                            
                            const optionDiv = document.createElement('div');
                            optionDiv.className = 'option';
                            optionDiv.textContent = String.fromCharCode(65 + i) + ') ' + option.text;
                            
                            wrapper.appendChild(optionDiv);
                            container.appendChild(wrapper);
                        });
                    }
                    
                    function checkAnswer(index) {
                        var answersStr = document.getElementById('answers').textContent.trim();
                        var answers = answersStr.split(" ");
                        return answers[index] === "1";
                    }

                    function showFeedback(isCorrect) {
                        // Remove existing feedback
                        var existing = document.querySelectorAll('.answer-feedback');
                        existing.forEach(el => el.remove());
                        
                        var feedbackDiv = document.createElement('div');
                        feedbackDiv.className = 'answer-feedback';
                        feedbackDiv.textContent = isCorrect ? '✓ Correct!' : '✗ Incorrect';
                        feedbackDiv.style.backgroundColor = isCorrect ? '#4CAF50' : '#f44336';
                        feedbackDiv.style.color = 'white';
                        feedbackDiv.style.position = 'fixed';
                        feedbackDiv.style.bottom = '20px';
                        feedbackDiv.style.left = '50%';
                        feedbackDiv.style.transform = 'translateX(-50%)';
                        feedbackDiv.style.padding = '12px 24px';
                        feedbackDiv.style.borderRadius = '8px';
                        feedbackDiv.style.fontWeight = 'bold';
                        feedbackDiv.style.zIndex = '1000';
                        document.body.appendChild(feedbackDiv);
                    }

                    function ankiSelectOption(index) {
                        var allOptions = document.querySelectorAll('.option-wrapper');
                        allOptions.forEach(opt => opt.className = 'option-wrapper');
                        
                        var selected = document.querySelector('.option-wrapper[data-index="' + index + '"]');
                        if (selected) {
                            var isCorrect = checkAnswer(index);
                            selected.className = 'option-wrapper ' + (isCorrect ? 'selected-correct' : 'selected-incorrect');
                            
                            showFeedback(isCorrect);
                            
                            if (!isCorrect) {
                                // Show correct answer
                                var answers = document.getElementById('answers').textContent.trim().split(" ");
                                answers.forEach((ans, i) => {
                                    if (ans === "1") {
                                        var correct = document.querySelector('.option-wrapper[data-index="' + i + '"]');
                                        if (correct) correct.className += ' correct';
                                    }
                                });
                            }
                            
                            var hidden = document.getElementById('selected-option');
                            if (hidden) hidden.textContent = index;
                        }
                    }
                    
                    // Initialize when page loads
                    document.addEventListener('DOMContentLoaded', initializeOptions);
                    // Also initialize immediately in case DOMContentLoaded already fired
                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', initializeOptions);
                    } else {
                        initializeOptions();
                    }
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
                                var correct = document.querySelector('.option-wrapper[data-index="' + i + '"]');
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
                # Pad options to 4 elements
                options = mcq['options'] + [''] * (4 - len(mcq['options']))
                
                # Create note with the MCQ data (no shuffling here - done dynamically in JavaScript)
                note = genanki.Note(
                    model=self.model,
                    fields=[
                        '',  # Title (blank)
                        html.escape(mcq['question']),
                        '2',  # Q type (2 for single choice)
                        html.escape(options[0]),  # Q_1
                        html.escape(options[1]),  # Q_2
                        html.escape(options[2]),  # Q_3
                        html.escape(options[3]),  # Q_4
                        '',  # Q_5 (optional 5th option)
                        mcq['answers'],  # Original answer mapping
                        '',  # ShuffleOrder (not used with dynamic shuffling)
                        '',  # selected-option (empty initially)
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
