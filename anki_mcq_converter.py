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
                    <div id="shuffle-order" style="display:none;">{{ShuffleOrder}}</div>
                    
                    <!-- Hidden option data -->
                    <div style="display:none;" id="option-data">
                        {{#Q_1}}<div data-index="0">{{Q_1}}</div>{{/Q_1}}
                        {{#Q_2}}<div data-index="1">{{Q_2}}</div>{{/Q_2}}
                        {{#Q_3}}<div data-index="2">{{Q_3}}</div>{{/Q_3}}
                        {{#Q_4}}<div data-index="3">{{Q_4}}</div>{{/Q_4}}
                    </div>
                    
                    <script>
                    // Create a unique identifier for this card based on its content
                    function getCardId() {
                        const question = document.querySelector('.question').textContent.trim();
                        const optionData = document.getElementById('option-data');
                        const options = Array.from(optionData.children).map(el => el.textContent.trim()).join('|');
                        return btoa(question + '|||' + options).substring(0, 20); // Base64 encoded, shortened
                    }
                    
                    // Simple random shuffle function
                    function shuffleArray(array) {
                        const shuffled = [...array];
                        for (let i = shuffled.length - 1; i > 0; i--) {
                            const j = Math.floor(Math.random() * (i + 1));
                            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
                        }
                        return shuffled;
                    }
                    
                    // Get options and create shuffle order - ONLY ONCE per card
                    function getOrCreateShuffleOrder() {
                        const cardId = getCardId();
                        const sessionKey = 'cardShuffle_' + cardId;
                        
                        // Check if we have a session shuffle order for this specific card
                        if (window[sessionKey]) {
                            return window[sessionKey];
                        }
                        
                        // Check if we have a stored shuffle order in the hidden field
                        const shuffleOrderEl = document.getElementById('shuffle-order');
                        const storedOrder = shuffleOrderEl.textContent.trim();
                        
                        if (storedOrder && storedOrder !== '{{ShuffleOrder}}' && storedOrder !== '') {
                            try {
                                const parsed = JSON.parse(storedOrder);
                                window[sessionKey] = parsed; // Store in session
                                return parsed;
                            } catch (e) {
                                // If parsing fails, create a new shuffle order
                            }
                        }
                        
                        // Create new shuffle order for this card
                        const optionData = document.getElementById('option-data');
                        const options = Array.from(optionData.children).filter(el => el.textContent.trim() !== '');
                        
                        if (options.length === 0) return [];
                        
                        // Create option objects with original indices for THIS CARD'S options
                        const optionObjects = options.map((el, i) => ({
                            text: el.textContent.trim(),
                            originalIndex: parseInt(el.getAttribute('data-index'))
                        }));
                        
                        // Create shuffle order and store it for this card
                        const shuffledOrder = shuffleArray(optionObjects);
                        
                        // Store in both session and hidden field
                        window[sessionKey] = shuffledOrder;
                        shuffleOrderEl.textContent = JSON.stringify(shuffledOrder);
                        
                        return shuffledOrder;
                    }
                    
                    // Initialize front side options
                    function initializeFrontSide() {
                        const container = document.getElementById('options-container');
                        const shuffledOptions = getOrCreateShuffleOrder();
                        
                        if (shuffledOptions.length === 0) return;
                        
                        // Display options in shuffled order
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
                        
                        // Remove feedback after 2 seconds
                        setTimeout(function() {
                            feedbackDiv.remove();
                        }, 2000);
                    }

                    function ankiSelectOption(index) {
                        // Prevent multiple selections
                        var allOptions = document.querySelectorAll('.option-wrapper');
                        var alreadyAnswered = Array.from(allOptions).some(opt => 
                            opt.className.includes('selected-') || opt.className.includes('correct'));
                        
                        if (alreadyAnswered) return; // Don't allow re-selection
                        
                        // Clear all option styles first
                        allOptions.forEach(opt => opt.className = 'option-wrapper disabled');
                        
                        var selected = document.querySelector('.option-wrapper[data-index="' + index + '"]');
                        if (selected) {
                            var isCorrect = checkAnswer(index);
                            selected.className = 'option-wrapper ' + (isCorrect ? 'selected-correct' : 'selected-incorrect');
                            
                            showFeedback(isCorrect);
                            
                            // Always show the correct answer(s) for learning
                            var answers = document.getElementById('answers').textContent.trim().split(" ");
                            answers.forEach((ans, i) => {
                                if (ans === "1") {
                                    var correct = document.querySelector('.option-wrapper[data-index="' + i + '"]');
                                    if (correct && !correct.className.includes('selected-')) {
                                        correct.className = 'option-wrapper correct disabled';
                                    }
                                }
                            });
                            
                            // Store selection
                            var hidden = document.getElementById('selected-option');
                            if (hidden) hidden.textContent = index;
                            
                            // Disable clicking on all options
                            allOptions.forEach(opt => {
                                opt.onclick = null;
                                opt.style.cursor = 'default';
                            });
                            
                            // Show native Anki review buttons by triggering answer state
                            setTimeout(function() {
                                // Trigger Anki's native answer state to show review buttons
                                if (typeof pycmd !== 'undefined') {
                                    pycmd('ans');
                                }
                            }, 2000); // Give time to see the feedback
                        }
                    }
                    
                    // Initialize when page loads - FRONT SIDE ONLY
                    document.addEventListener('DOMContentLoaded', initializeFrontSide);
                    if (document.readyState !== 'loading') {
                        initializeFrontSide();
                    }
                    </script>
                ''',
                'afmt': '''
                    <div class="question">{{Question}}</div>
                    <div id="options-container-back">
                        <!-- Options will be displayed with answer highlighting -->
                    </div>
                    <div id="selected-option" style="display:none;">{{selected-option}}</div>
                    <div id="answers" style="display:none;">{{Answers}}</div>
                    <div id="shuffle-order" style="display:none;">{{ShuffleOrder}}</div>
                    
                    <!-- Hidden option data -->
                    <div style="display:none;" id="option-data">
                        {{#Q_1}}<div data-index="0">{{Q_1}}</div>{{/Q_1}}
                        {{#Q_2}}<div data-index="1">{{Q_2}}</div>{{/Q_2}}
                        {{#Q_3}}<div data-index="2">{{Q_3}}</div>{{/Q_3}}
                        {{#Q_4}}<div data-index="3">{{Q_4}}</div>{{/Q_4}}
                    </div>
                    
                    <script>
                    // Create a unique identifier for this card based on its content
                    function getCardId() {
                        const question = document.querySelector('.question').textContent.trim();
                        const optionData = document.getElementById('option-data');
                        const options = Array.from(optionData.children).map(el => el.textContent.trim()).join('|');
                        return btoa(question + '|||' + options).substring(0, 20); // Base64 encoded, shortened
                    }
                    
                    // Get the SAME shuffle order that was created on the front side
                    function getStoredShuffleOrder() {
                        const cardId = getCardId();
                        const sessionKey = 'cardShuffle_' + cardId;
                        
                        // First check if we have it in session storage
                        if (window[sessionKey]) {
                            return window[sessionKey];
                        }
                        
                        // Try to get stored shuffle order from hidden field
                        const shuffleOrderDiv = document.getElementById('shuffle-order');
                        const storedOrder = shuffleOrderDiv.textContent.trim();
                        
                        if (storedOrder && storedOrder !== '{{ShuffleOrder}}' && storedOrder !== '') {
                            try {
                                const parsed = JSON.parse(storedOrder);
                                window[sessionKey] = parsed; // Store in session for consistency
                                return parsed;
                            } catch (e) {
                                // If parsing fails, fall back to original order
                            }
                        }
                        
                        // Fallback: create original order from this card's options
                        const optionData = document.getElementById('option-data');
                        const options = Array.from(optionData.children).filter(el => el.textContent.trim() !== '');
                        return options.map((el, i) => ({
                            text: el.textContent.trim(),
                            originalIndex: parseInt(el.getAttribute('data-index'))
                        }));
                    }
                    
                    // Initialize back side with EXACT same shuffle order and selection state from front side
                    function initializeBackSide() {
                        const container = document.getElementById('options-container-back');
                        const shuffleOrder = getStoredShuffleOrder();
                        
                        if (shuffleOrder.length === 0) return;
                        
                        const selectedOptionDiv = document.getElementById('selected-option');
                        const selectedIndex = selectedOptionDiv.textContent.trim() !== '' && 
                                           selectedOptionDiv.textContent.trim() !== '{{selected-option}}' ? 
                                           parseInt(selectedOptionDiv.textContent.trim()) : -1;
                        
                        // Display options in SAME shuffled order as front side
                        container.innerHTML = '';
                        shuffleOrder.forEach((option, i) => {
                            const wrapper = document.createElement('div');
                            wrapper.className = 'option-wrapper disabled';
                            wrapper.setAttribute('data-index', option.originalIndex);
                            
                            const optionDiv = document.createElement('div');
                            optionDiv.className = 'option';
                            optionDiv.textContent = String.fromCharCode(65 + i) + ') ' + option.text;
                            
                            // Apply highlighting to match front side state
                            const isSelected = option.originalIndex === selectedIndex;
                            const isCorrect = checkAnswerBack(option.originalIndex);
                            
                            if (isSelected) {
                                // Show user's selection with appropriate styling
                                wrapper.className = 'option-wrapper ' + (isCorrect ? 'selected-correct' : 'selected-incorrect') + ' disabled';
                            } else if (isCorrect) {
                                // Always show correct answers highlighted for learning
                                wrapper.className = 'option-wrapper correct disabled';
                            } else {
                                // Regular options remain neutral
                                wrapper.className = 'option-wrapper disabled';
                            }
                            
                            wrapper.appendChild(optionDiv);
                            container.appendChild(wrapper);
                        });
                        
                        // Show the same feedback message on back side if user made a selection
                        if (selectedIndex !== -1) {
                            const isCorrect = checkAnswerBack(selectedIndex);
                            showBackSideFeedback(isCorrect);
                        }
                    }
                    
                    // Show feedback message on back side to match front side experience
                    function showBackSideFeedback(isCorrect) {
                        // Remove any existing feedback first
                        const existing = document.querySelectorAll('.answer-feedback');
                        existing.forEach(el => el.remove());
                        
                        const feedbackDiv = document.createElement('div');
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
                        feedbackDiv.style.animation = 'fadeIn 0.3s ease';
                        
                        document.body.appendChild(feedbackDiv);
                        
                        // Keep feedback visible longer on back side since it's more permanent
                        setTimeout(function() {
                            feedbackDiv.remove();
                        }, 4000); // 4 seconds instead of 2
                    }
                    
                    function checkAnswerBack(index) {
                        var answersStr = document.getElementById('answers').textContent.trim();
                        var answers = answersStr.split(" ");
                        return answers[index] === "1";
                    }
                    
                    // Initialize when page loads - only on back side
                    document.addEventListener('DOMContentLoaded', initializeBackSide);
                    if (document.readyState !== 'loading') {
                        initializeBackSide();
                    }
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
                #options-container, #options-container-back {
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
                .option-wrapper:hover:not(.disabled) {
                    background-color: #f5f5f5;
                    border-color: #bbb;
                    transform: translateY(-1px);
                }
                .option-wrapper.disabled {
                    cursor: default !important;
                    pointer-events: none;
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
                @keyframes slideDown {
                    from { opacity: 0; transform: translateY(-10px); }
                    to { opacity: 1; transform: translateY(0); }
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
                # Create note with the MCQ data
                note = genanki.Note(
                    model=self.model,
                    fields=[
                        '',  # Title (blank)
                        html.escape(mcq['question']),
                        '2',  # Q type (2 for single choice)
                        *[html.escape(opt) for opt in mcq['options']],
                        *('' for _ in range(4 - len(mcq['options']))),  # Pad with empty strings if less than 4 options
                        '',  # Q_5 (optional 5th option)
                        mcq['answers'],
                        '',  # ShuffleOrder (empty initially)
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
