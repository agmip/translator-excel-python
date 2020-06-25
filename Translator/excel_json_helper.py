#!/usr/bin/python3

import json 
import datetime


map_functions={
    "toLowerCase" :  lambda x: x.lower()   
}
SEPARATOR=","

class ExcelJsonHelper:
    """A class helper with some methods for specific pruporses related to xslx to json manipulation """
    
    @classmethod
    def simple_template(cls,key_name):
        return "\""+key_name+"\":\"{}\""
        
    # create a dictionary to grouped all the items linked with an ID field_id, weather_id or soil_id
    # it is to avoid search in every iteration the elements with the specific ID
    @classmethod
    def group_by_linker(cls,list_objects):
        TRT_COLUMN= 0
        temp_map={}
        for x in list_objects:

            try:
                columnid= list(x.keys())[TRT_COLUMN]
                trtid=x[columnid] # assuming that linked id is in column 0 
                if trtid in temp_map:
                    temp_map[trtid]=temp_map[trtid]+ [x]
                else: 
                    temp_map[trtid]=[x]
            except IndexError:
                print("index error: current value is not a key. Hint: review completly each sheet to find additional cells filled ")
                print(x, TRT_COLUMN, trtid, columnid)
                print(list_objects)
                exit()
            
        return temp_map
        

    ##read an excel sheet and map to a json object list 
    @classmethod
    def get_data_json_like(cls,data,excel_helper):
        
        sheet_name=data.get('sheetName')
        header_row=int(data.get('headerRow'))
        header_transformation=data.get('transformHeader')
        take_subset = data.get('takeSubset')
        exclude_subset = data.get('excludeSubset')
        
        is_open_sheet= excel_helper.activate_sheet(sheet_name)

        if not is_open_sheet: 
            return []
        #validate that the first row is not empty
        if(excel_helper.validate_empty_cell(header_row)):
            print ("validation error")
            return []
        
        
        header_cells=excel_helper.get_row_values(header_row) # get atribute names using the header row        
        header_cells=list(map( map_functions[header_transformation], header_cells)) #pass to lower case header row
        json_template=list(map( cls.simple_template , header_cells)) # template for creating json data key:{%s} format 
        
        json_template=SEPARATOR.join( json_template )
        
        start=header_row+1
        end = excel_helper.get_last_row_index()
        
        json_list_experiments=[]
        
        for i in range(start, end): # based on the template create row values
            values=excel_helper.get_row_values(i)
            types=excel_helper.get_row_types(i)
            
            
            # format date types
            for index,x in enumerate(types):
                if(x==excel_helper.XL_CELL_DATE):

                    myDate=datetime.datetime(*excel_helper.date_as_tuple(values[index]))
                    myDateStr="{:%Y%m%d}".format(myDate)
                    
                    values[index]=myDateStr
            
            new_row=json_template.format(*values)
            new_row_dic= json.loads("{%s}"%new_row)
            
            # remove keys that have empty values 
            new_row_dic_filtred = dict(filter(lambda elem: elem[1]  != '', new_row_dic.items()))

           
            if take_subset is not None:
                new_row_dic_filtred = dict(filter(lambda elem: elem[0] in take_subset , new_row_dic_filtred.items()))
            
            if exclude_subset is not None:
                new_row_dic_filtred = dict(filter(lambda elem: elem[0] not in exclude_subset , new_row_dic_filtred.items()))

        
            json_list_experiments.append(new_row_dic_filtred)
        return json_list_experiments
    
    
    
    @classmethod
    def validate_keys(cls,keys_list, dictionary):

        if len(keys_list)==0:
            return True
        key=keys_list.pop(0)
        if  key in dictionary :
            
            return cls.validate_keys(keys_list, dictionary[key])
        else:
            
            return False

    @classmethod
    def write_json(cls,my_dict,outputfile):
        my_json = json.dumps(my_dict)
        f = open(outputfile,"w")
        f.write(my_json)
        f.close()

        print("json file created")      

    ## create json structure
    @classmethod
    def recursivity_json_path(cls,path_list, json_object, value ):
        
        item= path_list.pop(0) # path_list len should be >= 1
        if item not in json_object:
            json_object[item]={}
        
        if len(path_list)==0: # it was the last item
            json_object[item]=value
            
        else:
            cls.recursivity_json_path(path_list, json_object[item],value)

    # read entities that are in several sheets 
    @classmethod
    def several_sheets_reader(cls,sheets_list_names, base_data,  excel_helper, apply_func=''):
        listObjects=[]

        for index,sheetName in enumerate(sheets_list_names):
            local_data={}
            local_data["sheetName"]=sheetName
            local_data['headerRow']=base_data['headerRow']
            local_data['transformHeader']=base_data['transformHeader']

            more_settings=  base_data.get("sheetConfig")
            if more_settings is not None:
                sheet_settings= more_settings.get(sheetName)
                if sheet_settings is not None:
                    local_data['takeSubset']=sheet_settings.get('takeSubset')
                    local_data['excludeSubset']=sheet_settings.get('excludeSubset')
        

            sheetElementsList=cls.get_data_json_like(local_data,excel_helper)

            if apply_func=="addEvents" :
                sheetElementsList=cls.add_events(sheetElementsList ,base_data["eventsName"][index])

            if sheetName in ["Metadata","Planting"]:
                listObjects=cls.flatten_planting_events(listObjects , sheetElementsList)
            else:
                listObjects=listObjects + sheetElementsList
        
        return listObjects
    @classmethod
    def add_events(cls,myList, event_name):
        def loc_fun(x):# add the event name to each element as other value
            x["event"]= event_name 
            return x

        myList= list(map(loc_fun , myList))
        return myList

    @classmethod
    def flatten_planting_events(cls,accum_list,sheet_list):

        EVENT_TYPE = "planting"
        IDS = "id"

        for sheet_element in sheet_list:
            
            if(sheet_element["event"]==EVENT_TYPE):
                find_index= next(index for index, accum_element in enumerate(accum_list) \
                    if accum_element[IDS] == sheet_element[IDS])

                if find_index is None: 
                    accum_list.append(element)
                else:
                    accum_list[find_index]= {**sheet_element, **accum_list[find_index]}
            else:
                accum_list.append(element)

        return accum_list     
# swld