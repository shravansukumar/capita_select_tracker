from datetime import datetime
import json
import os

class UniversalLogger:
    log_entry = []
    tls_error_dict = {}
    click_error_dict = {}
    time_out_error_dict = {} 
    isMobile = False

    def __init__(self,isMobile):
        self.log_entry = []
        for key in ['mobile','desktop']:
            self.tls_error_dict[key] = 0
            self.click_error_dict[key] = 0
            self.time_out_error_dict[key] = 0
            self.isMobile = isMobile

    def log(self,entry):
        entry_log = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") +' '+ str(entry) 
        print(entry_log)
        self.log_entry.append(entry_log)

    def dump_json(self):
        file_name_prefix = '_mobile' if self.isMobile == True else '_desktop'
        file_name = 'log'+file_name_prefix+'.json'
        with open(file_name,'w') as output_file:
            output_file.write(json.dumps(self.log_entry,indent=4))

    def handle_json_dumping_for_logs_with(self, file_name, log_dict):
        if os.path.isfile(file_name) and os.access(file_name,os.R_OK):
            with open(file_name,'r') as output_file:
                dict_count = json.load(output_file)
                if self.isMobile:
                    dict_count['mobile'] = log_dict['mobile']
                else:
                    dict_count['desktop'] = log_dict['desktop']

            with open(file_name,'w') as click_output_file:    
                click_output_file.write(json.dumps(dict_count, indent=4)) 
        else:
            with open(file_name,'w') as click_output_file:
                click_output_file.write(json.dumps(log_dict, indent=4)) 

    def dump_counter_logs(self):
        self.handle_json_dumping_for_logs_with('tls_error_logs.json',self.tls_error_dict)
        self.handle_json_dumping_for_logs_with('click_error_logs.json',self.click_error_dict)
        self.handle_json_dumping_for_logs_with('time_out_error_logs.json',self.time_out_error_dict)
