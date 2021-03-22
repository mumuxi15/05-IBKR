Package 

Start by

```bash
#start env 
python3 -m build
```

Install IBKR api

1. Download api from https://interactivebrokers.github.io/
2. Unzip the folder and place inside env 
3. Go to `tws-api/IBJts/source/pythonclient/`
4. Build a wheel with: `python3 setup.py bdist_wheel`
5. Install wheel with: `pip install dist/ibapi-9.76.1-py3-none-any.whl`
6. Remove the folder

