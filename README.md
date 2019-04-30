# remotepixel-tiler

[![CircleCI](https://circleci.com/gh/RemotePixel/remotepixel-tiler.svg?style=svg)](https://circleci.com/gh/RemotePixel/remotepixel-tiler)

[![codecov](https://codecov.io/gh/RemotePixel/remotepixel-tiler/branch/master/graph/badge.svg)](https://codecov.io/gh/RemotePixel/remotepixel-tiler)

Sentinel / Landsat / CBERS / COGEO Serverless dynamic tiler

Bundle of `landsat-tiler`, `sentinel-tiler`, `cbers-tiler` and `cogeo-tiler` powering RemotePixel [viewer](https://viewer.remotepixel.ca).

![viewer](https://user-images.githubusercontent.com/10407788/34139036-873c23e2-e440-11e7-9699-a2da6046a494.jpg)

# Deployment

##### Requirement
  - AWS Account
  - Terraform
  - Docker

```bash
#Clone the repo
$ git clone https://github.com/RemotePixel/remotepixel-tiler.git
$ cd remotepixel-tiler/


$ docker login

# Fetch Amazon linux AMI docker container + Install Python modules + create package
# Create package using custom GDAL install
$ make package && make test

# Deploy sentinel, landsat and cbers lambda functions
$ terraform init
$ terraform apply --var token=MySuperSecretToken
```

#### Infos & links
- [rio-tiler](https://github.com/mapbox/rio-tiler) rasterio plugin that process Landsat data hosted on AWS S3.
- [landsat-tiler](https://github.com/mapbox/landsat-tiler)
- [sentinel-tiler](https://github.com/mapbox/sentinel-tiler)
- [cbers-tiler](https://github.com/mapbox/cbers-tiler)



## Changes in this fork
- Added variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to the Dockerfile.
  - For some reason, the package built could not find those values. Those variables must be added to the system's env (e.g: 'export AWS_ACCESS_KEY_ID=<VALOR_AQUI>', inside ~/.bashrc or ~/.profile).

- Changed the region of the modules on the Terraform config file (remotepixel-tiler.tf) to those where the corresponding images are stored.

- In the case the Terraform commands raise errors, the changes below may be helpful:

`$ terraform init -reconfigure`

and

`$terraform apply -lock=false --var token=MySuperSecretToken`
