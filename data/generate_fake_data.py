import numpy as np
import h5py

from scipy.stats import multivariate_normal

x, y = np.mgrid[3:5:100j, 3:5:100j]
xy = np.column_stack([x.flat, y.flat])
mu = np.array([4.0, 4.0])
sigma = np.array([0.2, 0.3])
covariance = np.diag(sigma ** 2)
z = multivariate_normal.pdf(xy, mean=mu, cov=covariance)
z = z.reshape(x.shape)

f = h5py.File("fake_data.hdf","w")

f.attrs["attr1"] = "File attribute 1"
f.attrs["attr2"] = "File attribute 2"
f.attrs["attr3"] = "File attribute 3"

data_group = f.create_group("data")
data_group.attrs["attr1"] = "This is attribute 1"
data_group.attrs["attr2"] = "This is attribute 2"
data_group.attrs["attr3"] = "This is attribute 3"

dset2d = data_group.create_dataset("fake_data2D",data=z,dtype="d")
dset2d.attrs["info"] = "This is a fake 2D data example"

dset3d = data_group.create_dataset("fake_data3D",data=np.random.uniform(0,1,(400,200,20)),dtype="d")
dset3d.attrs["info"] = "This is a fake 3D data example"

monitor_group = f.create_group("monitor")

temperature = monitor_group.create_dataset("temperature", data=300 + np.random.uniform(-0.1,0.1,(500,)))
temperature.attrs["description"] = "measured temperature"
temperature.attrs["experimentalist"] = "Charles Baudelaire"

pressure = monitor_group.create_dataset("pressure", data=1 + np.random.uniform(-0.5,0.5,(1000,)))
pressure.attrs["description"] = "measured pressure"
pressure.attrs["experimentalist"] = "Arthur Rimbault"

f.close()

