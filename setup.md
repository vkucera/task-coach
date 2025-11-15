# Setup on Ubuntu-based GNU/Linux

## Prepare

```bash
# Get the code.
git clone --depth=500 https://github.com/taskcoach/taskcoach.git
cd taskcoach

# Create and enter virtual environment.
python3 -m virtualenv env
source env/bin/activate

# Install dependencies.
pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-24.04 wxPython
python -m pip install pubsub pypubsub twisted desktop3 chardet numpy pyparsing lxml dateutil python-dateutil distro lockfile

# Prepare and install.
make prepare
python setup.py install
```

## Run

```bash
taskcoach.py
```
