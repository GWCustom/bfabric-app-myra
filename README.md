# bfabric-app-template
Template Application for Bfabric Webapp Concept (written in Python3) 

## Deployment 

1) Fork the Repo 

2) Clone your Repo

``` 
git clone https://github.com/your/bfabric-app-template/fork.git && cd bfabric-app-template
```
3) Set up virtual environment:

For using virtualenv: 
``` 
python3 -m venv my_app_1
source my_app_1/bin/activate
```

For using conda: 

```
conda create -n my_app_1 pip
conda activate my_app_1
```

For using mamba: 
```
mamba create -n my_app_1 pip
conda activate my_app_1
```

4) Install bfabricpy: 

```
git clone https://github.com/fgcz/bfabricPy.git && cd bfabricPy
git checkout bfabric12 
cd bfabricPy
python3 setup.py sdist && pip3 install dist/bfabric-0.13.*.tar.gz
cd ..
```

5) Install remaining dependencies:

```
pip install -r requirements.txt
``` 

6) Create a PARAMS.py file with your host and port!

```
# PARAMS.py
HOST = 0.0.0.0
PORT = 8050 
```

7) Run the application 

```
python3 index.py
```

8) Check it out! 

Visit http://localhost:8050 to see your site in action.
