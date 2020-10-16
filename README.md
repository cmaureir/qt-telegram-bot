# Qt Telegram Bot

Simple bot for the [Qt for Python](https://pyside.org) telegram channel.

Currently the interaction is limited to provide information links
regarding the documentation, other Python modules, and the issues
on the [JIRA bugtracker](https://bugreports.qt.io/browse/PYSIDE)

## Commands

```
/qthelp     - This message
/issue N  - Information about the PYSIDE-N issue
          - Without arguments it shows a summary
/doc      - Links to documentation
/module   - Differences between PyQt/PySide
/gerrit   - Link to the latest open changes
/meetings - Link to the public meeting notes
```

## Installation

To implement this on a separate bot, remember to register your own
[with the BotFather](https://core.telegram.org/bots), so you can provide
your Token in the required configuration file, called `config.ini`.
The file should look like this:

```
[DEFAULT]
Token=123456
```

where the numbers will be the Token code you get after the registration.

After that, a simple `pip install -r requirements.txt` in your virtual
environment will be enough to get you started.
