import sys
import math
import random
import numpy as np
import rasterio
import polyscope as ps

def main():
    #-- open the DSM with rasterio
    inputfile = "../ahn3_data/ahn3_dsm50cm_bk_small.tif"
    d = rasterio.open(inputfile)
    
    #-- the 2 points: ground+sun
    px = 85169.3 
    py = 446863.7
    pz = 0
    sx = 85300
    sy = 446990
    sz = 150

    band1 = d.read(1)
    t = d.transform
    pts = []
    #-- put 1 for no thinning, 10 for factor 10, etc
    thinning = 1 
    for i in range(band1.shape[0]):
        for j in range(band1.shape[1]):
             x = t[2] + (j * t[0]) + (t[0] / 2)
             y = t[5] + (i * t[4]) + (t[4] / 2)
             z = band1[i][j]
             if (z != d.nodatavals) and (random.randint(0, thinning) == 1):
                 pts.append([x, y, z])
    verts = np.asarray(pts)
    losp = np.zeros((2, 3))
    losp[0][0] = px
    losp[0][1] = py
    losp[0][2] = pz
    losp[1][0] = sx
    losp[1][1] = sy
    losp[1][2] = sz
    lose = np.array([[1, 0]])

    ps.set_program_name("myviz")
    ps.set_up_dir("z_up")
    ps.set_ground_plane_mode("shadow_only")
    ps.set_ground_plane_height_factor(0.01, is_relative=True)
    ps.set_autocenter_structures(True)
    ps.set_autoscale_structures(True)
    ps.init()
    ps_net = ps.register_curve_network("my network", losp, lose, radius=0.0015)
    ps_cloud = ps.register_point_cloud("mypoints", verts, radius=0.0015, point_render_mode='quad')
    ps_cloud.add_scalar_quantity("rand vals", verts[:, 2], enabled=True)
    ps_net.reset_transform()
    ps_cloud.reset_transform()
    ps.show()

if __name__ == '__main__':
    main()

