//-- my_code_hw02.cpp
//-- hw02 GEO1015.2022
//-- [YOUR NAME]
//-- [YOUR STUDENT NUMBER] 

#include <iostream>
#include <fstream>
#include <chrono>
#include <stdio.h>
#include <sstream>

//-- include that file that is in the same folder
#include "DatasetASC.h"

//-- forward declarations of functions in this unit, this just ensures that
//-- the compiler knows about the functions
std::string GetStdoutFromCommand(std::string cmd);
int is_sunny(DatasetASC &ds, double px, double py, std::string dt);

/*
!!! DO NOT MODIFY main() !!!
*/
int main(int argc, char* argv[])
{
  //-- read parameters passed: file px py date-time
  //-- ./hw02 ../../ahn3_data/ahn3_dsm50cm_bk_small.asc 86000 445000 '2022-09-26 11:35'
  
  if (argc != 5) {
    std::cout << "Usage: hw02 infile px py dt" << std::endl;
    return -1;
  }

  std::string input_file = argv[1];
  double px = std::stod(argv[2]);
  double py = std::stod(argv[3]);
  std::string dt = argv[4];

  // Record start time
  auto start = std::chrono::high_resolution_clock::now();

  DatasetASC ds(input_file);
  if (ds.validity == false) {
    return -1;
  }

  int result = is_sunny(ds, px, py, dt);
  std::cout << "Does the sun shine there? " << result << std::endl;


  // Record end time
  auto finish = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double> elapsed = finish - start;
  std::cout << std::fixed << std::setprecision(3) << "--- " << elapsed.count() << " seconds ---" << std::endl;

  return result;
}


//-- Taken from:
//   https://www.jeremymorgan.com/tutorials/c-programming/how-to-capture-the-output-of-a-linux-command-in-c/
std::string GetStdoutFromCommand(std::string cmd) 
{
  std::string data;
  FILE * stream;
  const int max_buffer = 256;
  char buffer[max_buffer];
  cmd.append(" 2>&1");
  stream = popen(cmd.c_str(), "r");
  if (stream) {
    while (!feof(stream))
      if (fgets(buffer, max_buffer, stream) != NULL) data.append(buffer);
    pclose(stream);
  }
  return data;
}

/*
!!! TO BE COMPLETED !!!
 
Does the sun shine there at that moment?
 
Input:
    ds: the input dataset (DatasetASC)
    px: x-coordinates in EPSG:28992 of the point to test
    py: y-coordinates in EPSG:28992 of the point to test
    dt: ISO-formatted datetime ('YYYY-MM-DD HH:MM'), eg '2022-08-12 13:32'
    
Output:
    0: not illuminated
    1: illuminated
    2: Point given is outside the extent of the dataset
    3: Point given has no_data value
*/
int is_sunny(DatasetASC &ds, double px, double py, std::string dt)
 {

  std::cout << "==> function sunny() !!! TO BE COMPLETED !!! <==" << std::endl;

  //-- here we call the Python script to get the position of the sun (azimuth/altitude)
  //-- at local time in Delft for position (px, py) 
  std::stringstream s;
  s << "python ../python_bin/sunpos.py ";
  s << px << " " << py << " ";
  s << "'" << dt << "'" << std::endl;
  //-- this calls the Python script and reads from stdout what is printed 
  //-- (pretty hacky but hey it works)
  std::string re = GetStdoutFromCommand(s.str());
  std::cout << "azimuth altitude: " << re << std::endl;
  //-- to interpret the results https://github.com/mourner/suncalc#sun-position

  //-- some examples about functions and attributes of DatasetASC
  int row, col;
  bool b1 = ds.xy2rc(85166.0, 446817.9, row, col);
  std::cout << b1 << std::endl;
  std::cout << row << ", " << col << std::endl;
  std::cout << "no_data value:" << ds.nodata_value << std::endl;
  double cx, cy;
  b1 = ds.rc2xy(503, 1, cx, cy);
  std::cout << std::fixed << std::setprecision(1) << "centre" << " : " << cx << ", " << cy << std::endl;

  return 1; //-- or 0 or 2 or 3
}



