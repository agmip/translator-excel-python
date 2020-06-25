

from Translator.config import Config
from Translator.excel_helper import ExcelHelper
from Translator.excel_json_helper import ExcelJsonHelper

import sys

def close():
   sys.exit(2)

#CONTANS
EVENTS_LABEL_LIST=["events"] # special process for events section in excel file 
OBSERVATIONS_LABEL="observations" # special process for observatioins 
SUMMARY_LABEL="summary" # special process for observations 


class Translator:
    """
    A class to run all the process related to the translation. 
    
    It depends on  Config, ExcelHelper, ExcelJsonHelper
    Step 1 extract data, using configuration defined in Config manipulate the excel file and create Json-like items
    Step 2 join by IDs and created paths, then data should be linked with others sheets to create corresponding path in the consolidated JSON file  
    Step 3 format a cleaned, some items are list or dictionaries, in this process Json data is cleaned to be uniform
    
    """
    @classmethod
    def translate(cls, excel_name, outputfile):
        
        child_grouper={}# grouper for children ex {initial_conditions:[List], management:[list]}
        json_parameters= Config.get_configuration()# template to define the json structure
        my_excel_helper = ExcelHelper()

        
        my_excel_helper.load_file(excel_name)
        
            
         
        sheets_names= my_excel_helper.get_sheets_names()
       

        #Step 1 extract data from excel
        for data in  json_parameters:
            

            # events process
            if(data["name"] in EVENTS_LABEL_LIST):
               
                list_objects=ExcelJsonHelper.several_sheets_reader(data["eventsType"], data,  my_excel_helper, "addEvents")
                child_grouper["events"]=ExcelJsonHelper.group_by_linker(list_objects)
            
            #  observed data process    
            elif (data["name"] in [OBSERVATIONS_LABEL,SUMMARY_LABEL ] ):
                
                sheetsList=list(filter(lambda x: data["sheetPattern"] in x, sheets_names ))
                list_objects=ExcelJsonHelper.several_sheets_reader(sheetsList, data,  my_excel_helper)
                child_grouper[data["name"]]=ExcelJsonHelper.group_by_linker(list_objects)

            # other sheets
            else:    
                list_objects=ExcelJsonHelper.get_data_json_like(data,my_excel_helper)
                child_grouper[data["name"]]=ExcelJsonHelper.group_by_linker(list_objects)
        

        ## step 2 organice data joining based on ids that link elements, create paths when applies
        for local_data in  json_parameters: 
    
            if len(local_data["path"]) >1 :# has a long path, it is not a root element
        
                base_path=local_data["path"].pop(0) # remove first elements, root element
        
                for key, value in child_grouper[base_path].items():
            
                    temp_path=list(local_data["path"]) # copy object because reference pass produce mutable effect
            
                    set_object= None
                    existKeys= ExcelJsonHelper.validate_keys([local_data["name"], key], child_grouper )# validate that the keys exists in path
            
                    if existKeys:# validate that the keys exists in path
                        if local_data["type"]=="list":
                            set_object=   child_grouper[local_data["name"]][key]
                        else :    
                            set_object=   child_grouper[local_data["name"]][key][0]

                        ExcelJsonHelper.recursivity_json_path(temp_path, value[0], set_object  )
                #ExcelJsonHelper.writeJson(child_grouper[local_data["name"]],"examples/json/parts"+local_data["name"])
                if local_data["name"] in child_grouper.keys():
                    del child_grouper[local_data["name"]]  # memory clean

        ## step 3 format json extract objects 
        for key, value in child_grouper.items():
            new_list=[]
            for key2, value2 in child_grouper[key].items():
                new_list.append(value2[0])
        
            child_grouper[key]= new_list

        # write in disk the json file
        ExcelJsonHelper.write_json(child_grouper,outputfile)