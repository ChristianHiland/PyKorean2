from googletrans import Translator
from textblob import TextBlob
from google import genai
import os

translator = Translator()
GEMINI_KEY = os.getenv('GEMINI_TOKEN')
geminiClient = None
if GEMINI_KEY != None:
    geminiClient = genai.Client(api_key=GEMINI_KEY)

def advanced_translate_logic(sentence):
    blob = TextBlob(sentence)
    print(f"Sentence: {sentence}")
    print(f"Tagged: {blob.tags}")

    
    # Buckets for sentence parts
    subject = ""
    objects = []
    modifiers = [] # Adjectives
    verb_final = ""
    
    # Special flags
    is_mental_thought = False
    mental_verbs = ['think', 'say', 'believe', 'know', 'hope']
    ignore_list = ['the', 'a', 'an', 'to', "they", "'re"]


    # Simple context check
    current_word_index = 0
    # 1. Classification Loop
    for word, tag in blob.tags:
        current_word_index = 1 + current_word_index
        next_word = ""
        next_tag = ""
        
        clean_word = word.lower()
        
        # Skip filler words
        if clean_word in ignore_list:
            continue

        if len(blob.tags) > current_word_index:
            next_word = blob.tags[current_word_index][0]
            next_tag = blob.tags[current_word_index][1]
            
        # Translate the word
        ko_word = translator.translate(clean_word, src='en', dest='ko').text
        
        # LOGIC: Subject (I, He, Name)
        if tag in ['PRP', 'NNP'] and not subject:
            subject = ko_word + "는"
            
        # LOGIC: Main Verb (at the end)
        elif tag.startswith('VB'):
            if clean_word in mental_verbs:
                is_mental_thought = True
                verb_final = ko_word
            elif not verb_final:
                verb_final = ko_word
            else:
                # If we already have a verb, the extra ones become objects (actions)
                objects.append(ko_word)
                
        # LOGIC: Adjectives
        elif tag == 'JJ':
            modifiers.append(ko_word)
            
        # LOGIC: Nouns
        elif tag.startswith('NN'):
            # If it's a thought like "wolves are cute", inner nouns use '가'
            if is_mental_thought:
                objects.append(ko_word + "가")
            else:
                # Basic checking for a "FANBOYS" to attach a particle needed.
                if next_tag == "CC":
                    if next_word == "and":
                        objects.append(ko_word+"과")
                else:
                    objects.append(ko_word)

    # 2. Assembly (SOV Structure)
    # Join objects/actions with commas
    obj_str = ", ".join(objects)
    mod_str = " ".join(modifiers)
    
    # 3. Particle Selection
    if is_mental_thought:
        # Structure: Subj + [Noun-가 + Adj] + 고 + Verb
        return f"{subject} {obj_str} {mod_str}고 {verb_final}"
    else:
        # Structure: Subj + [Noun/Actions] + 를 + Verb
        # Add '를' only if there are objects
        particle = "를" if objects else ""
        return f"{subject} {obj_str}{particle} {mod_str} {verb_final}".strip()
    
def translate_final_logic(sentence):
    # Split the sentence if there is a comma to handle two separate thoughts
    parts = sentence.split(',')
    translated_clauses = []

    for part in parts:
        blob = TextBlob(part.strip())
        subject, verb, objects, modifiers = "", "", [], []
        
        # Extended ignore list to stop the 'Reply' and 'And' bugs
        ignore_list = ['the', 'a', 'an', 'to', 'and', "'re", "they", "it", "is", "are"]

        for i, (word, tag) in enumerate(blob.tags):
            clean = word.lower()
            if clean in ignore_list: continue

            # Look ahead for list logic
            next_tag = blob.tags[i+1][1] if i + 1 < len(blob.tags) else ""
            
            ko = translator.translate(clean, src='en', dest='ko').text
            
            # 1. SUBJECTS
            if tag in ['PRP', 'NNP'] and not subject:
                subject = ko + "는"
            
            # 2. VERBS (Action at the end)
            elif tag.startswith('VB'):
                # Special fix for 'like'
                if clean == 'like': ko = "좋아한다"
                verb = ko
                
            # 3. NOUNS (Objects)
            elif tag.startswith('NN'):
                # Clean up translation artifacts like '과' or '를' if they were pre-attached
                ko = ko.replace('과', '').replace('를', '').replace('와', '')
                
                if next_tag == 'CC' or (i + 1 < len(blob.tags) and blob.tags[i+1][0] == ','):
                    objects.append(ko + "와") # Add "and" particle
                else:
                    objects.append(ko)

            # 4. ADJECTIVES
            elif tag in ['JJ', 'RB']:
                # If an adjective is at the end of a clause, it acts as the verb
                if i == len(blob.tags) - 1:
                    verb = ko 
                else:
                    modifiers.append(ko)

        # Assemble Clause: Subj + Obj + Mod + Verb
        obj_str = " ".join(objects)
        if objects and verb == "좋아한다": 
            obj_str += "를" # Only add '를' to the end of the object list
            
        clause = f"{subject} {obj_str} {' '.join(modifiers)} {verb}".strip()
        translated_clauses.append(clause)

    return " ".join(translated_clauses)

class GeminiLearning:
    def __init__(self):
        self.client = geminiClient
        self.basePrompt = ""
        self.model_name = "gemini-2.5-flash"
        self.learnFile = "LearningProgress.txt"

    def Generate(self) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=self.prompt + f" {self.fileContents}"
            )

    