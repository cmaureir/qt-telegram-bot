import configparser
import logging
from pprint import pprint

import telegram
from emoji import emojize
from jira import JIRA
from jira.exceptions import JIRAError
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


def escape(x):
    special = [".", "-", "(", ")", "[", "]", ">", "<", "=", "+", "{", "}", "#", "_"]
    for c in special:
        x = x.replace(c, fr"\{c}")
    return x


jira = JIRA("https://bugreports.qt.io")


def control_test(update, context):
    chat_id = str(update.effective_chat.id).replace("-", r"\-")
    pprint(update)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"It's working [Qt for Python Site](https://pyside.org)\nID:{chat_id}",
        parse_mode=telegram.ParseMode.MARKDOWN_V2,
    )


def doc(update, context):
    doc_url = r"https://doc\.qt\.io/qtforpython/"
    wiki_url = r"https://pyside\.org"
    icon1 = emojize(":green_book:", use_aliases=True)
    icon2 = emojize(":notebook:", use_aliases=True)
    msg = f"{icon1} Documentation: {doc_url}\n" f"{icon2} Wiki: {wiki_url}"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=telegram.ParseMode.MARKDOWN_V2,
    )

def gerrit(update, context):
    gerrit_url = r"https://codereview.qt-project.org/q/project:pyside%252Fpyside-setup+status:open"
    msg = f"Gerrit Code Review\n`pyside-setup` repository: [latest changes]({gerrit_url})"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=telegram.ParseMode.MARKDOWN_V2,
    )

def meetings(update, context):
    meetings_url = r"https://wiki.qt.io/Qt_for_Python_Development_Notes"
    msg = f"Qt for Python [meeting notes]({meetings_url})"
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=telegram.ParseMode.MARKDOWN_V2,
    )


def help_handler(update, context):
    msg = (
        "```\n"
        "/help     - This message\n"
        "/issue N  - Information about the PYSIDE-N issue\n"
        "          - Without arguments it shows a summary\n"
        "/doc      - Links to documentation\n"
        "/module   - Differences between PyQt/PySide\n"
        "/gerrit   - Link to the latest open changes\n"
        "/meetings - Link to the public meeting notes\n"
        "```"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=telegram.ParseMode.MARKDOWN_V2,
    )


def module(update, context):
    pyqt_url = r"https://www\.riverbankcomputing\.com/software/pyqt/intro"
    pyside_url = r"https://qt\.io/qt-for-python"
    snake = emojize(":snake:", use_aliases=True)
    msg = (
        f"{snake} Python modules\n\n"
        f"• [PySide]({pyside_url}): Developed by The Qt Company \(LGPL/Commercial\)\n"
        f"• [PyQt]({pyqt_url}): Developed by Riverbank Computing \(GPL/Commercial\)\n\n"
        f"This channel is about the first module, *PySide*, which "
        f"belongs to the *Qt for Python* project, including the"
        f"binding generator tool called *Shiboken*"
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=telegram.ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True,
    )


def issue(update, context):
    base_url = "https://bugreports.qt.io/browse/"
    content = ""
    link = ""
    error_icon = emojize(":x:", use_aliases=True)
    try:
        arg = context.args[0]
        arg = arg.replace("PYSIDE-", "")
        try:
            status = None
            issue_number = int(arg)
            issue_id = f"PYSIDE-{issue_number}"
            try:
                issue = jira.issue(issue_id)
                summary = issue.raw["fields"]["summary"]
                status = issue.raw["fields"]["status"]["name"]
                link = f"[{issue_id}]({base_url}{issue_id})"
                content = f"{summary}]"
            except JIRAError as e:
                link = error_icon
                if e.status_code == 404:
                    content = "Error: Issue not found"
                else:
                    content = "Undefined Error"
        except ValueError:
            link = error_icon
            content = f"Invalid argument '{arg}', use an issue number"

        content = escape(content)
        link = link.replace("-", r"\-")
        msg = f"{link}: {content}"
        if status:
            icon = ""
            if status == "Open":
                icon = emojize(":large_blue_circle:", use_aliases=True)
            elif status == "Closed":
                icon = emojize(":white_check_mark:", use_aliases=True)
            else:
                icon = emojize(":red_circle:", use_aliases=True)
            msg += f"\n*Status*: {icon} {status}"

    except IndexError:
        issues = jira.search_issues(
            "project=PYSIDE and resolution=Unresolved and type=Bug order by created DESC",
            maxResults=200,
        )
        icon = emojize(":information_source:", use_aliases=True)
        msg = f"*Total open issues*: {len(issues)}\n\nLast 5 open issues:"
        for issue in issues[:5]:
            key = issue.key
            key_clean = key.replace("-", r"\-")
            summary = issue.fields.summary
            msg += f"\n• [{key_clean}]({base_url}{key}): {escape(summary)}"
        msg += (
            "\n\nCheck all the issues [on this link](https://bugreports.qt.io/issues/?filter=20338)"
        )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=telegram.ParseMode.MARKDOWN_V2,
    )


def welcome(update, context):
    for new_user_obj in update.message.new_chat_members:
        chat_id = update.message.chat.id
        new_user = ""

        try:
            new_user = "@" + new_user_obj["username"]
        except Exception:
            new_user = new_user_obj["first_name"]

        party = emojize(":tada:", use_aliases=True)
        confetti = emojize(":confetti_ball:", use_aliases=True)
        doc_url = "https://doc.qt.io/qtforpython/"
        wiki_url = "https://pyside.org"
        msg = (
            f"Welcome {new_user} {party} {confetti}\n"
            f"Remember to check the documentation page {doc_url}\n"
            f"and the Wiki: {wiki_url}\n"
            f"if you have some questions\n"
        )

        context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")

def unknown(update, context):
    context.bot.send_message(chat_id=update.message.chat.id,
                             text="Command not found, check `/help`",
                             parse_mode=telegram.ParseMode.MARKDOWN_V2)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )

    config = configparser.ConfigParser()
    config.read("config.ini")
    TOKEN = config["DEFAULT"]["Token"]

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("test", control_test))
    dispatcher.add_handler(CommandHandler("doc", doc))
    dispatcher.add_handler(CommandHandler("module", module))
    dispatcher.add_handler(CommandHandler("help", help_handler))
    dispatcher.add_handler(CommandHandler("issue", issue))
    dispatcher.add_handler(CommandHandler("gerrit", gerrit))
    dispatcher.add_handler(CommandHandler("meetings", meetings))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))

    updater.start_polling()
