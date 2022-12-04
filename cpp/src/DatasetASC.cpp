// ------------------------------------------------------------------------------
// DO NOT MODIFY THIS FILE!!!
// ------------------------------------------------------------------------------
#include <string>
#include <iostream>
#include <fstream>

#include "DatasetASC.h"

DatasetASC::DatasetASC(std::string ifile) {
  std::cout << "Reading file: " << ifile << std::endl;
  std::ifstream infile(ifile.c_str(), std::ifstream::in);
  validity = true;
  if (!infile)
  {
    std::cerr << "Input file not found." << std::endl;
    validity = false;
  }
  std::string tmp;
  //-- ncols
  infile >> tmp;
  infile >> ncols;
  //-- nrows
  infile >> tmp;
  infile >> nrows;
  //-- xllcorner
  infile >> tmp;
  infile >> xllcorner;
  //-- yllcorner
  infile >> tmp;
  infile >> yllcorner;
  //-- cellsize
  infile >> tmp;
  infile >> cellsize;
  //-- nodata_value
  infile >> tmp;
  infile >> nodata_value;
  //-- read the data in a 2D array (here a vector or vector)
  double v;
  //-- read each row/line
  for (int i = 0; i < nrows; i++) {
    std::vector<double> onerow;
    for (int j = 0; j < ncols; j++) {
      infile >> v;
      onerow.push_back(v);
    }
    data.push_back(onerow);
  }
  // std::cout << ds.data[1][3] << std::endl;
  infile.close();
}


//-- returns centre of the pixel from (row, col)
//-- origin is top-left, 0-based index
//-- false if outside
bool DatasetASC::rc2xy(int row, int col, double& x, double& y)
{
  if ( (row < 0) || (row > (nrows - 1)) ) {
    return false;
  }
  if ( (col < 0) || (col > (ncols - 1)) ) {
    return false;
  }
  x = xllcorner + (col * cellsize) + (cellsize / 2);
  y = yllcorner + ((nrows - 1 - row) * cellsize) + (cellsize / 2);
  return true;
}


//-- returns the row/col in the variables passed by reference
//-- if xy inside the ds, then true; otherwise false
bool DatasetASC::xy2rc(double x, double y, int& row, int& col){
  if ( (x < xllcorner) || (x > (xllcorner + (ncols * cellsize))) ) {
    return false;
  }
  if ( (y < yllcorner) || (y > (yllcorner + (nrows * cellsize))) ) {
    return false;
  }
  col = (x - xllcorner) / cellsize;
  row = nrows - ((y - yllcorner) / cellsize);
  return true;
}


