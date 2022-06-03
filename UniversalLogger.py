from datetime import datetime
import json

class UniversalLogger:
    log_entry = []
    tls_error_dict = {}
    click_error_dict = {}
    time_out_error_dict = {} 

    def __init__(self):
        self.log_entry = []
        for key in ['mobile','desktop']:
            self.tls_error_dict[key] = 0
            self.click_error_dict[key] = 0
            self.time_out_error_dict[key] = 0

    def log(self,entry):
        entry_log = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") +' '+ str(entry) 
        print(entry_log)
        self.log_entry.append(entry_log)

    def dump_json(self):
        with open('log.json','w') as output_file:
            output_file.write(json.dumps(self.log_entry,indent=4))

    def dump_counter_logs(self):
        with open('tls_error_logs.json','w') as tls_output_file:
            tls_output_file.write(json.dumps(self.tls_error_dict, indent=4)) 
        with open('click_error_logs.json','w') as click_output_file:
            click_output_file.write(json.dumps(self.click_error_dict, indent=4)) 
        with open('time_out_error_logs.json','w') as click_output_file:
            click_output_file.write(json.dumps(self.time_out_error_dict, indent=4)) 