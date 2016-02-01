SublimeText - StringUtilities
===============
StringUtilities is a Sublime Text 3 plugin, which adds to the editor useful string functions like:

* Convert Tabs to Spaces
* Convert Spaces to Tabs
* Convert Chars to Html Entities
* Convert Html Entities to Chars
* Convert Camel Case <-> Underscores
* Convert Single Quotes To Double
* Convert Double Quotes To Single
* Encode as URL Notation
* Decode from URL Notation
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
* Generate Password (6 char)
* Generate Password (8 char)
* Generate Password (12 char)
* Generate Password (16 char)
* Generate Password (32 char)
* Generate Password (40 char)
* Generate Password (64 char)
* Insert Internal IP Address
* Insert External IP Address
* Pretify JSON String


Sponsors
-----
No sponsors yet.. :(

If you like the software, don't forget to donate to further development of it!

[![PayPal donate button](https://www.paypalobjects.com/webstatic/en_US/btn/btn_donate_pp_142x27.png)](https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=akalongman@gmail.com&item_name=Donation to Sublime Text - StringUtilities&item_number=1&no_shipping=1 "Donate to this project using Paypal")


Installation
------------------

 * Install [Package Manager][0].
 * Use `Cmd+Shift+P` or `Ctrl+Shift+P` then `Package Control: Install Package`.
 * Look for `StringUtilities` and install it.

If you prefer to install manually, install git, then:

Clone the repository in a subfolder "StringUtilities" in your Sublime Text "Packages" directory:

    git clone https://github.com/akalongman/sublimetext-stringutilities "<Sublime Text 3 Packages folder>/StringUtilities"


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
