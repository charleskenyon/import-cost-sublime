import sublime, sublime_plugin
import threading, subprocess, json, os, functools
from .utils import node_socket, npm_install

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class ImportCostExec(threading.Thread):

	def __init__(self, view):
		self.view = view
		self.proc = self.open_node_socket()
		threading.Thread.__init__(self)
		print('init')

	def run(self):
		region = sublime.Region(0, self.view.size())
		file_string = self.view.substr(region)
		file_path = self.view.file_name()
		json_data = json.dumps({'file_string': file_string, 'file_path': file_path}) + '\n'
		if self.proc.poll() is not None:
			self.proc = self.open_node_socket()
		self.proc.stdin.write(json_data)
		node_output = self.proc.stdout.readline()[:-1]
		if node_output:
			self.view.run_command('write_output', {'output': node_output})

	def open_node_socket(self):
		try:
			node_path = os.path.join(sublime.packages_path(), DIR_PATH, 'import-cost.js')
			return node_socket(node_path)
		except Exception as error:
			sublime.error_message('import-cost\n%s' % error)


class WriteOutputCommand(sublime_plugin.TextCommand):

	def run(self, edit, output):
		region = sublime.Region(0, self.view.size())
		print(output)
		print(sublime.Region(1))
		self.view.erase_phantoms("test")
		# self.view.add_phantom("test", sublime.Region(self.view.line(3)), "Hello, World!", sublime.LAYOUT_INLINE)
		# self.view.replace(edit, region, output)

		# line = self.view.line(module["region"].a)
		# sublime.Region(self.view.line(3))


class ImportCostCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		ImportCostExec(self.view).start()

		
class EventEditor(sublime_plugin.EventListener):

	pending = 0

	def handle_timeout(self, view):
		self.pending = self.pending - 1
		if self.pending == 0:
			view.run_command('import_cost')

	def on_modified(self, view):
		file_extension = os.path.splitext(view.file_name())[1]
		if file_extension in ['.js', '.jsx']:
			self.pending = self.pending + 1
			sublime.set_timeout(functools.partial(self.handle_timeout, view), 1500)

	def on_new_async(self, view):
		npm_install(view, DIR_PATH) # sublime message when complete

    # view.run_command('import_cost')

  # on switch view remove phantom set


# ImportCostCommand(sublime_plugin.TextCommand) --> view.run_command(import_cost)system

# file_path = view.file_name()

# eslint_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node_modules', 'eslint', 'bin', 'eslint.js')

# sublime.Phantom to show data

# http://horsed.github.io/articles/sublime-build-system-for-npm-install/

# installing npm modules... /-------/ node/npm not installed - please install node to use this plugin