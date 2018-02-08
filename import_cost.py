import sublime, sublime_plugin
import threading, subprocess, json, os, functools
from .utils import node_socket, npm_install

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
FILE_EXTENSIONS = ['.js', '.jsx']
NODE_SOCKET = None
NODE_OUTPUT_CACHE = None


def plugin_loaded():
	global NODE_SOCKET
	NODE_SOCKET = NodeSocket()


class NodeSocket():
	def __init__(self):
		self._p = self.open_node_socket()

	@property
	def p(self):
		if self._p.poll() is not None:
			self._p = self.open_node_socket()
		return self._p

	def open_node_socket(self):
		try:
			node_path = os.path.join(sublime.packages_path(), DIR_PATH, 'import-cost.js')
			return node_socket(node_path)
		except Exception as error:
			# sublime.error_message('import-cost\n%s' % error)
			sublime.active_window().status_message('import-cost\n%s' % error)

	# def get_process(self):
	# 	if self.p.poll() is not None:
	# 		self.p = self.open_node_socket()
	# 	return self.p

	def terminate_process(self):
		self._p.terminate()


class ImportCostExec(threading.Thread):

	def __init__(self, view):
		self.view = view
		threading.Thread.__init__(self)

	def run(self):
		region = sublime.Region(0, self.view.size())
		file_string = self.view.substr(region)
		file_path = self.view.file_name()
		json_data = json.dumps({'file_string': file_string, 'file_path': file_path}) + '\n'

		NODE_SOCKET.p.stdin.write(json_data)
		node_output = NODE_SOCKET.p.stdout.readline()[:-1]
		
		if node_output:
			global NODE_OUTPUT_CACHE
			NODE_OUTPUT_CACHE = json.loads(node_output)
			self.view.run_command('write_output', {'output': NODE_OUTPUT_CACHE})


class WriteOutputCommand(sublime_plugin.TextCommand):

	def __init__(self, view):
		self.view = view
		self.phantom_set = sublime.PhantomSet(view, 'import_cost')

	def run(self, edit, output):
		if output is None: return None

		# for x in json.loads(output):
		# 	print(x['html'])

		# short circuit if not change to region
		# only if change on line containing phantom - cache line in list
		
		phantoms = [
			sublime.Phantom(self.get_region(x['line']), x['html'], sublime.LAYOUT_INLINE)
			for x in output
		]

		print(phantoms)

		self.view.erase_phantoms('import_cost')
		self.phantom_set.update(phantoms)
		
		# self.view.erase_phantoms("test")

	def get_region(self, line):
		a = self.view.text_point(line, 0)
		return sublime.Region(a - 1)

		# add blank region to right of import self.view.insert(edit, point, string)


class ImportCostCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		ImportCostExec(self.view).start()

		
class EventEditor(sublime_plugin.EventListener):

	def __init__(self):
		self.pending = 0

	def handle_timeout(self, view):
		self.pending = self.pending - 1
		if self.pending == 0:
			view.run_command('import_cost')

	def on_modified(self, view):
		if view.file_name():
			file_extension = os.path.splitext(view.file_name())[1]
			if file_extension in FILE_EXTENSIONS:
				
				# sel1 = view.sel()[0]
				# character = view.substr(sel1.a - 1)
				# print(character)
				# print((character == ';') or character == ')')

				# line, col = view.rowcol(view.sel()[0].begin())
				# point = view.text_point(line, 0)
				# print(view.substr(sublime.Region(point - 1, 1)))
				
				# global NODE_OUTPUT_CACHE
				# line, col = view.rowcol(view.sel()[0].begin())

				# if line + 1 in [x['line'] for x in NODE_OUTPUT_CACHE]:
				# 	NODE_OUTPUT_CACHE[:] = [x for x in NODE_OUTPUT_CACHE if x.get('line') != line + 1]
				# 	print(NODE_OUTPUT_CACHE)
				# 	view.run_command('write_output', {'output': NODE_OUTPUT_CACHE})

				# break into function and Memoize - check to see if charecter was semi colon
				# return tuple: boolean and updated output
				# if added charecter is semicolon and line in NODE_OUTPUT_CACHE

				self.pending = self.pending + 1
				sublime.set_timeout(functools.partial(self.handle_timeout, view), 1000)

	def on_new_async(self, view):
		npm_install(DIR_PATH) # status_message(string) view.set_status - add error handling

	def on_activated(self, view):
		view.run_command('import_cost')

	def on_deactivated(self, view):
		view.erase_phantoms('import_cost')
		NODE_SOCKET.terminate_process()

		# view.run_command('import_cost')

	# on switch view remove phantom sets


# ImportCostCommand(sublime_plugin.TextCommand) --> view.run_command(import_cost)system

# file_path = view.file_name()

# eslint_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'node_modules', 'eslint', 'bin', 'eslint.js')

# sublime.Phantom to show data

# http://horsed.github.io/articles/sublime-build-system-for-npm-install/

# installing npm modules... /-------/ node/npm not installed - please install node to use this plugin

# [forkpty: Resource temporarily unavailable]
# [Could not create a new process and open a pseudo-tty.]

# worker 646 appears stuck while processing file /Users/bmck/Documents/projects/ri-web-ui-library/node_modules/diff/dist/diff.js, killing process
# indexing: crawler exited while processing /Users/bmck/Documents/projects/ri-web-ui-library/node_modules/diff/dist/diff.js, no symbols recorded

# NameError: name 'NodeSocket' is not defined

# indexing [job 16]: no files were indexed out of the 1 queued, abandoning crawl
