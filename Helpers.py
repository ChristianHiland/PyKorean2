from textblob import TextBlob
from googletrans import Translator

translator = Translator()

def translate_and_reorder(sentence):
    blob = TextBlob(sentence)
    translated_parts = []
    
    # Define our SOV buckets
    structure = {'SUBJ': [], 'OBJ': [], 'VERB': [], 'OTHER': []}
    print(blob.tags)
    for word, tag in blob.tags:
        # 1. Skip articles like 'the', 'a', 'an'
        if tag == 'DT': 
            continue
            
        # 2. Translate the word
        ko_text = translator.translate(word.string, src='en', dest='ko').text
        
        # 3. Assign to bucket based on Tag
        # NN = Noun, PRP = Pronoun, VB = Verb, JJ = Adjective
        if tag in ['PRP', 'NNP'] and not structure['SUBJ']:
            structure['SUBJ'].append(ko_text + "는") # Subject + Particle
        elif tag in ['NN', 'NNS']:
            structure['OBJ'].append(ko_text + "에")   # Object/Location + Particle
        elif tag.startswith('VB'):
            structure['VERB'].append(ko_text)       # Verb (ends the sentence)
        else:
            structure['OTHER'].append(ko_text)

    # 4. Construct: Subject -> Other -> Object -> Verb
    result = structure['SUBJ'] + structure['OTHER'] + structure['OBJ'] + structure['VERB']
    return " ".join(result)

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
    ignore_list = ['the', 'a', 'an', 'to', 'and']

    # 1. Classification Loop
    for word, tag in blob.tags:
        clean_word = word.lower()
        
        # Skip filler words
        if clean_word in ignore_list:
            continue
            
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