# Crawl_data_with_scrapy

------------------------------------------------------------------------

the first project: we will start crawl data with the simple projects

------------------------------------------------------------------------

More information at https://github.com/hoanganhbk1235/Crawl_data_with_scrapy

----------------

Requirements: 
+ install Python and Numpy, Scrapy, pdb libraries

  pip install numpy
  
  conda install -c conda-forge scrapy
  
  pip install scrapy
  
  pip install pdb
  
+ tool: sublime text

  wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
  
  echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
  
  sudo apt-get update
  
  sudo apt-get install sublime-text
    
----------------
the Steps create a new project:
+ Create a new project: scrapy startproject "folder_name_contain_project"
+ cd ./"folder_name_contain_project"/
+ Create spider file : scrapy genspider "file_main_name" "domain (google.com, ...)"
+ Run project: scrapy crawl "class_name"
+ or you can save the result into csv or json file follow the statement:

    scrapy crawl "class_name" -o "file_name".csv (or scrapy crawl prime02 -o "file_name".json)
