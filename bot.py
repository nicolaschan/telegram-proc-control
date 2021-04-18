import sys
import subprocess
import shlex

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

class ProcessController:
    def __init__(self, command):
        self.command = shlex.split(command)
        self.proc = None
    def spawn(self):
        if self.is_running():
            return False, self.pid()
        else:
            self.proc = subprocess.Popen(self.command)
            return True, self.pid()
    def get_proc(self):
        if self.proc:
            self.proc.poll()
            return self.proc
    def is_running(self):
        if self.get_proc():
            return self.proc.returncode is None
        return False
    def pid(self):
        if self.get_proc():
            return self.proc.pid
    def return_code(self):
        self.proc.poll()
        if not self.is_running() and self.proc is not None:
            return self.proc.returncode
    def stop(self):
        if self.is_running():
            self.proc.kill()
            self.proc.wait()
            self.proc.poll()
            returncode = self.proc.returncode
            self.proc = None
            return returncode
        return None

def make_stop_handler(controller: ProcessController):
    def stop_handler(update: Update, _: CallbackContext):
        if controller.is_running():
            return_code = controller.stop()
            response = f'Exited with return code {return_code}'
        else:
            response = 'Process not running'
        update.message.reply_text(response)
    return stop_handler

def make_status_handler(controller: ProcessController):
    def status_handler(update: Update, _: CallbackContext):
        proc = controller.get_proc()
        if controller.is_running():
            response = f'Process running:\nPID: {controller.pid()}'
        else:
            if controller.return_code() is not None:
                response = f'Process finished:\nReturn Code: {controller.return_code()}'
            else:
                response = 'No process managed'
        update.message.reply_text(response)
    return status_handler

def make_start_handler(controller: ProcessController):
    def start_handler(update: Update, _: CallbackContext):
        try:
            status, pid = controller.spawn()
            response = f'Process started with PID {pid}' if status else f'Process already running with PID {pid}'
        except Exception as e:
            response = str(e)
        update.message.reply_text(response)
    return start_handler

def test_handler(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(f'Hi {user.mention_markdown_v2()}')

def main(token, command):
    controller = ProcessController(command)
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", make_start_handler(controller)))
    dispatcher.add_handler(CommandHandler("status", make_status_handler(controller)))
    dispatcher.add_handler(CommandHandler("stop", make_stop_handler(controller)))
    dispatcher.add_handler(CommandHandler("test", test_handler))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    token = sys.argv[1]
    command = sys.argv[2]
    main(token, command)
