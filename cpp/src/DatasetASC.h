// ------------------------------------------------------------------------------
// DO NOT MODIFY THIS FILE!!!
// ------------------------------------------------------------------------------

#include <vector>

class DatasetASC
{
  public:
    bool validity;
    int ncols;
    int nrows;
    double xllcorner;
    double yllcorner;
    double cellsize;
    double nodata_value;
    std::vector<std::vector<double>> data;

    DatasetASC(std::string ifile);

    bool rc2xy(int row, int col, double& x, double& y);
    bool xy2rc(double x, double y, int& row, int& col);

}; 