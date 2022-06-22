import speech_recognition as sr
import spacy
import pandas as pd
import pm4py
import copy
import datetime
import os

# NLP
nlp = spacy.load('de_core_news_sm')

# Recognizer
r = sr.Recognizer()
r.energy_threshold = 300

AUDIO_DIR = '../audio'

class Speech2Process():
    """
    
    """
 
    def from_audio(self, audio_files):
        """
        
        """
        text = self.__transcribe_audio(audio_files)
        print("Transcribed text:\n", text)
        print(" ")
        return self.from_text(text)

    def from_text(self, text):
        """
        
        """
        activity_log_df = self.__generate_activity_log(self.__extract_infos(text))
        
        activity_log = pm4py.format_dataframe(
            activity_log_df.copy(),
            case_id='case_id',
            activity_key='activity',
            timestamp_key='timestamp'
        )

        # XES
        self.__export(activity_log, format='xes')
        self.__export(activity_log, format='bpmn')
        self.__export(activity_log, format='png')

        return {
            'activity_log_html': activity_log_df.to_html(index=False, justify='left')
        }

    def __transcribe_audio(self, audio_files):
        """
        
        """
        try:
            transcribed_sentences = []
            # Transcribe in right order
            audio_files.sort()
            for audio_file in audio_files:
                with sr.AudioFile(f'{AUDIO_DIR}/{audio_file}') as source:
                    #r.adjust_for_ambient_noise(source, duration=0.2)
                    audio = r.record(source)

                transcribed_sentences.append(r.recognize_google(audio, language='de-DE'))
        except:
            raise Exception('Cant recognise any text... try again.')
        return transcribed_sentences
    
    def __extract_infos(self, text):
        """
        
        """
        extracted_infos = []
        trace = 0
        # Junction traces
        junction_counter = 0

        for index, sentence in enumerate(text):
            doc = nlp(sentence)
            tokens = {token.pos_:token.text for token in doc}

            # Split CCONJ e.g. "and" to seperate items
            if 'CCONJ' in tokens.keys():
                sentence_parts = sentence.split(tokens.get('CCONJ'))
                doc = nlp(sentence_parts[0]) # Overwrite old doc for new parted sentence
                tokens = {token.pos_:token.text for token in doc}
                text = text[:index] + sentence_parts + text[index+1:]
                return self.__extract_infos(text)

            # Exclusive OR = new trace
            if 'SCONJ' in tokens.keys():
                junction_counter += 1 
                if junction_counter > 2:
                    trace += 1 # Count trace up
                    update = {'TRACE':trace}
                    extracted_infos_copy = [{**d,**update} for d in extracted_infos_copy]
                    extracted_infos = extracted_infos + extracted_infos_copy
                else:
                    # After first junction, make copy with disjunct entries
                    extracted_infos_copy = copy.deepcopy(extracted_infos)
            else:
                junction_counter = 0
            
            # Extract information for extracted_infos
            extraction = {'TRACE':trace, 'OBJECT':'%', 'VERB':'%', 'SUBJECT':'%', 'STEP':index}
            for token in doc:
                if (token.pos_ == 'VERB'):
                    extraction['VERB'] = token.lemma_
                elif (token.dep_=='sb'):
                    extraction['SUBJECT'] = token.text
                elif (token.dep_=='oa'):
                    extraction['OBJECT'] = token.text
                elif (token.dep_ in ['pg','nk']):
                    extraction['OBJECT'] += " " + token.text
                elif (token.dep_ in ['svp']):
                    extraction['VERB'] = token.text + " " + extraction['VERB']
            extracted_infos.append(extraction)
            
        return extracted_infos

    def __generate_activity_log(self, information_extraction: dict):
        """
        Transform information extraction to activity_log df
        """
        activity_log = []
        for event in information_extraction:
            activity_log.append({
                'case_id'       : event['TRACE'],
                'activity'      : f"{event['OBJECT']} {event['VERB']}",
                'timestamp'     : datetime.datetime.now() + datetime.timedelta(seconds=event['STEP']),
                'ressource'     : event['SUBJECT']
            })

        return pd.DataFrame(activity_log)

    def __export(self, activity_log, format: str = 'png') -> str:
        path = '/static/assets'
        if format == 'bpmn':
            file = os.path.relpath(os.getcwd() + f'{path}/bpm/process.bpmn')
            tree = pm4py.discover_process_tree_inductive(activity_log)
            bpmn_graph = pm4py.objects.conversion.process_tree.converter.apply(tree, variant=pm4py.objects.conversion.process_tree.converter.Variants.TO_BPMN)
            pm4py.write_bpmn(bpmn_graph, file, enable_layout=True)
        elif format == 'xes':
            file = os.path.relpath(os.getcwd() + f'{path}/bpm/process.xes')
            pm4py.write_xes(activity_log, file)
        else:
            file = os.path.relpath(os.getcwd() + f'{path}/images/process.png')
            process_tree = pm4py.discover_tree_inductive(activity_log)
            bpmn_model = pm4py.convert_to_bpmn(process_tree)
            pm4py.save_vis_bpmn(bpmn_model,file)

        return file