# MacVim auto-generated web documentation 

This repository contains automation scripts to generate online web version of MacVim documentation. It uses [vimhelp](https://github.com/c4rlo/vimhelp) as a backend to generate HTML versions of MacVim's documentation and publishes them as a GitHub page. The repository is named "docs" so that it would show up as the same URL under the root domain under GitHub Pages.

## vimhelp

The subfolder `vimhelp` is a forked version of vimhelp using Git subtree (we avoid using submodules to avoid having to make another repository just for the downstream changes). It contains changes to add support for a "MacVim" project and to change the output to match MacVim's needs. It also has some improvements to the offline mode (e.g. manual light/dark mode selection). There's also a custom filter to make `gui_mac.txt` render a little fancier, including showing the MacVim icon.

Command used to add the subtree:
```
git remote add -f vimhelp git@github.com:c4rlo/vimhelp.git
git subtree add --prefix=vimhelp vimhelp/master --squash
```

Command used for staying in sync and pulling from upstream:
```
git subtree merge --prefix=vimhelp vimhelp/master --squash
```

## Running locally

To run the scripts locally, follow vimhelp's [README](vimhelp/README.md) to set up a venv first:

```
cd vimhelp
python3 -m venv --upgrade-deps .venv
.venv/bin/pip install -r requirements.txt
```

Source the venv:

```
. .venv/bin/activate
```

Then run the script (make sure to substitute `$macvim_dir` with the directory that you have MacVim cloned to):

```
scripts/h2h.py -i $macvim_dir/runtime/doc -o ../build --project macvim --web-version --output-tags-json
```

You can then run a simple web server in the build folder and browser to it. E.g. Use Python to server a server (it will be available at http://localhost:8000):

```
cd build
python3 -m http.server
```
