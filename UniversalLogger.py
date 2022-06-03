from datetime import datetime
import json

class UniversalLogger:
    log_entry = []

    def __init__(self):
         self.log_entry = []

    def log(self,entry):
        entry_log = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") +' '+ str(entry) 
        print(entry_log)
        self.log_entry.append(entry_log)

    def dump_json(self):
        with open('log.json','w') as output_file:
            output_file.write(json.dumps(self.log_entry,indent=4))