import sublime, sublime_plugin, threading
import subprocess, json, os
from .src.utils import node_bridge, npm_install

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class ImportCostExec(threading.Thread):

	def __init__(self, view):
		self.view = view
		threading.Thread.__init__(self)

	def run(self):
		region = sublime.Region(0, self.view.size())
		file_string = self.view.substr(region)
		file_path = self.view.file_name()
		json_data = json.dumps({'file_string': file_string, 'file_path': file_path})
		node_output = self.open_node_socket(json_data)
		self.view.run_command('write_output', {'output': node_output})

	def open_node_socket(self, data):
		try:
			node_path = os.path.join(sublime.packages_path(), DIR_PATH, 'process.js')
			return node_bridge(data, node_path)
		except Exception as error:
			sublime.error_message('import-cost\n%s' % error)


class WriteOutputCommand(sublime_plugin.TextCommand):

	def run(self, edit, output):
		region = sublime.Region(0, self.view.size())
		self.view.replace(edit, region, output)


class ImportCostCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		ImportCostExec(self.view).start()

		
class EventEditor(sublime_plugin.EventListener):

  def on_new_async(self, view):
    npm_install(view, DIR_PATH)

    # view.run_command('import_cost')


# ImportCostCommand(sublime_plugin.TextCommand) --> view.run_command(import_cost)system

# file_path = view.file_name()

# eslint_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node_modules', 'eslint', 'bin', 'eslint.js')

# sublime.Phantom to show data

# http://horsed.github.io/articles/sublime-build-system-for-npm-install/

# installing npm modules... /-------/ node/npm not installed - please install node to use this plugin