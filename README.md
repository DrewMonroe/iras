# Internet Routing Automated/Autonomous Security

## Installation
These scripts require the `PyBGPStream` python module in order to run.
While there is a version that exists in pip, you need the `libBGPStream` library, [install documentation for which can be found here](https://bgpstream.caida.org/docs/install/pybgpstream).
Furthermore, the version of `PyBGPStream` that exists in pip does not support python3.
If you want python3 support, you need to build `libBGPStream` from source (not from a release on their github page).
See the troubleshooting section in this README if you run into issues.

## Troubleshooting

### python3 error
The version of `PyBGPStream` available in pip only supports python2.7.
If you want python3 support, you must build `libBGPStream` from source, and then follow the build instructions in the `pybgpstream` folder inside of the `libBGPStream` repository.

### error: wandio HTTP support required

This error has been [documented in the bgpstream repository, with a fix in the comments](https://github.com/CAIDA/bgpstream/issues/32).
If you have this issue, check to see if the `LD_LIBRARY_PATH` environment variable contains the install directory where you installed `wandio` (by default `/usr/local/lib`).
If this directory is not in the environment variable, try to add the directory, and then rerun `./configure`.
This should solve the issue.
A more permanent solution, as described in [this stackoverflow post](https://stackoverflow.com/questions/1099981/why-cant-python-find-shared-objects-that-are-in-directories-in-sys-path/1100297#1100297) is to add `/usr/local/lib` to `/etc/ld.so.conf.d`, and then run `ldconfig`.

### ImportError: libbgpstream.so.2: cannot open shared object file: No such file or directory

See the troubleshooting message about 'wandio HTTP support required' to set your `LD_LIBRARY_PATH` environment variable.
