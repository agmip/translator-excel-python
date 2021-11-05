# translator-excel-python
Python translator from spreadsheet format to ACEB used in AgMIP Wheat work on potential yield.

# How to run the example?

The executable file can be downloaded from the release link. Executable's name: "PythonTranslatorExcelAgMIP.exe".
Then,copy the file into the folder ```<project>/examples/```. From there in a command line execute: 

``` 
PythonTranslatorExcelAgMIP.exe -i "<file_name>.xlsx" -o "output.json"
```
The executable runs in a windows 64 bits machine, for other architectures it is neccesary to create a new exe file as mentioned in the next sections.

# Project Structure

| File | Function |
| ------------- | ------------- |
| PythonTranslatorExcelAgMIP.py  | Get Console arguments and invoke the translator  |
| ./translator_pkg  | Folder containing translator package  |
| ./translator_pkg/translator.py  | Python class that represents the translator logic this file imports **excel_json_helper.py**, **excel_helper.py**, **config.py**  |
| ./translator_pkg/ excel_json_helper.py  | Python class helper with utils to create a specific JSON  based on the configuration for the processed sheet   |
| ./translator_pkg/excel_helper.py | Python class helper to manage all the methods related to excel file manipulation  |
| ./translator_pkg/config.py | A Python dictionary that indicates how each excel sheet should be explored and located in the JSON file     |

# How to start coding in this project?

Since this is a Python project, (1) programmers should install Python Dev Tools in visual studio and
(2) configure a python3 environment.


## Installing Python Dev Tools in Visual Studio

Open *visual studio installer*, this is an application installed with visual studio, search for it in windows explorer and open it. Address your used version,    
Click on **more** then go to **modify**, finally check *Python development* then click in **Install**.

The detailed process is in https://docs.microsoft.com/en-us/visualstudio/python/installing-python-support-in-visual-studio?view=vs-2019#visual-studio-2017-and-2019


## Import/ Export environment using conda

Python environments are used to explicitly keep project dependencies in an isolated way. You can use conda: https://docs.anaconda.com/anaconda/install/windows/
 to manage them, by installing conda you will have a new console in windows call Anaconda Prompt, open it and type 
```conda --version``` to check the installation. As you see in the console there is a (base) word on the left side, it means this is the activated environment. Writing ```conda env list``` you will see available environments.

The first process to do is to import the environment previously created, go to the root python project using the Anaconda Prompt:
```
cd ./Code/PythonTranslatorExcelAgMIP/
```

Then created the environment

```
conda  create --name  envTranslator --file environment/env_translator.txt 
```

Check if the environment was created  ```conda env list```



### Integrated the environment with visual studio

After creating the environment, open the project in the solution explorer and click right over *Python environments*
go to *View All Python Environments* select the envTranslator.



# How to create the executable from Python files?

This process was reached using the PyInstaller program. To install you should go to the root file using Anaconda Prompt.
```
cd ./Code/PythonTranslatorExcelAgMIP/
```

Then activate the environment.
```
activate envTranslator
```

Finally to run 

```
pip install pyinstaller
```

After installation, in the root folder you should run this command:

```
pyinstaller --onefile --distpath "../../Released"  --workpath  "./Pyinstaller/" PythonTranslatorExcelAgMIP.py
```

The .exe file will be located in the ./Released folder

# How to run the executable?
After creation the file will be located in 
``` 
cd ./Released/
``` 
Then execute the file
``` 
PythonTranslatorExcelAgMIP.exe -i "input/file.xlsx" -o "output/file.json"
```