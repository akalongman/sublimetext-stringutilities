SublimeText - StringUtilities
===============
StringUtilities is a Sublime Text 2 plugin, which adds to the editor useful string functions like:

* Convert Tabs to Spaces
* Convert Spaces to Tabs
* Convert Chars to Html Entities
* Convert Html Entities to Chars
* Convert Camel Case <-> Underscores
* Convert To Unicode Notation
* Convert From Unicode Notation
* Convert To Base64
* Convert From Base64
* Convert To Hex
* Convert From Hex
* Convert HTML Color From Hex To RGB
* Convert HTML Color From RGB To Hex
* Calculate Selection MD5
* Calculate Selection SHA1
* Convert Unixtime <-> Datetime
* Insert Current Datetime
* Insert Short Password
* Insert Medium Password
* Insert Long Password
* Insert Internal IP Address
* Insert External IP Address


Installation
------------------

 * Install [Package Manager][0].
 * Use `Cmd+Shift+P` or `Ctrl+Shift+P` then `Package Control: Install Package`.
 * Look for `StringUtilities` and install it.

If you prefer to install manually, install git, then:

Clone the repository in a subfolder "StringUtilities" in your Sublime Text "Packages" directory:

    git clone https://github.com/LONGMANi/sublimetext-stringutilities "<Sublime Text 2 Packages folder>/StringUtilities"


The "Packages" directory is located at:

* Linux: `~/.config/sublime-text-2/Packages/`
* OS X: `~/Library/Application Support/Sublime Text 2/Packages/`
* Windows: `%APPDATA%/Sublime Text 2/Packages/`

Or enter
```python
sublime.packages_path()
```
into the console (`` Ctrl-` ``).

Usage
------------------

* Right click on editor window (first select text if function is convert type) and select String Utilities menu item.

Todo
------------------

 * Add some missed functions


## Libraries ##

- **dateutil** by Gustavo Niemeyer is used for adding extensions to the standard python 2.3+ datetime module.. **PSF License**

[0]: http://wbond.net/sublime_packages/package_control
