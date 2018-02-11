import sublime, sublime_plugin
import threading, subprocess, json, os, functools
from .utils import node_socket, npm_install

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
FILE_EXTENSIONS = ['.js', '.jsx']
NODE_SOCKET = None
NODE_OUTPUT_CACHE = []


def plugin_loaded():
	global NODE_SOCKET
	NODE_SOCKET = NodeSocket()

	if not 'node_modules' in os.listdir(DIR_PATH):
		args = {"cmd": ["npm", "install"], "working_dir": DIR_PATH}
		sublime.active_window().run_command("exec", args)


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
			node_path = os.path.join(sublime.packages_path(), DIR_PATH, 'node-socket.js')
			return node_socket(node_path)
		except Exception as error:
			sublime.active_window().status_message('import-cost\n%s' % error)

	def pipe(self, node_input):
		self.p.stdin.write(node_input)
		return self.p.stdout.readline()[:-1]

	def terminate_process(self):
		self.p.terminate()


class ImportCostExec(threading.Thread):

	def __init__(self, view):
		self.view = view
		threading.Thread.__init__(self)

	def run(self):
		region = sublime.Region(0, self.view.size())
		file_string = self.view.substr(region)
		file_path = self.view.file_name()
		json_data = json.dumps({'file_string': file_string, 'file_path': file_path}) + '\n'
		print(json_data)
		node_output = NODE_SOCKET.pipe(json_data)
		print(node_output)
		
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
				
				# global NODE_OUTPUT_CACHE
				# line = view.rowcol(view.sel()[0].begin())[0] + 1
				# if line in [x['line'] for x in NODE_OUTPUT_CACHE]:
				# 	NODE_OUTPUT_CACHE[:] = [x for x in NODE_OUTPUT_CACHE if x.get('line') != line]
				# 	view.run_command('write_output', {'output': NODE_OUTPUT_CACHE})
				
				# character = view.substr(point - 1)
				# view.command_history(0)[0]

				self.pending = self.pending + 1
				sublime.set_timeout(functools.partial(self.handle_timeout, view), 1000)

	def on_activated(self, view):
		view.run_command('import_cost')

	def on_deactivated(self, view):
		view.erase_phantoms('import_cost')
		NODE_SOCKET.terminate_process()

	def on_close(self, view):
		NODE_SOCKET.terminate_process()

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

# def parse_file_string(self, file_string):
# 	return '\n'.join([
# 		x + ('//' + str(i)) 
# 		for i, x in enumerate(file_string.split('\n')) 
# 		if re.search(r'\bimport\s|\brequire\(', x)
# 	])

# def parse_file_string(self, file_string):
# 		temp_list = []
# 		for i, x in enumerate(file_string.split('\n')):
# 			if re.search(r'\bimport\s|\brequire\(', x):
# 				temp_list.append(x.replace(';', '') + ('//' + str(i)))
# 			else:
# 				temp_list.append('')
# 		return '\n'.join(temp_list)

# @functools.lru_cache(maxsize=None)
# NODE_SOCKET.pipe.cache_clear()
# NODE_SOCKET.pipe.cache_info()