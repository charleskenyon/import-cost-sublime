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

	@functools.lru_cache(maxsize=64)
	def pipe(self, node_input):
		try:
			self.p.stdin.write(node_input)
			return self.p.stdout.readline()[:-1]
		except BrokenPipeError:
			return None

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
		node_output = NODE_SOCKET.pipe(json_data)
		
		if node_output:
			global NODE_OUTPUT_CACHE
			NODE_OUTPUT_CACHE = json.loads(node_output)
			self.view.run_command('write_output', {'output': NODE_OUTPUT_CACHE})


class WriteOutputCommand(sublime_plugin.TextCommand):

	def __init__(self, view):
		self.view = view
		self.phantom_set = sublime.PhantomSet(view, 'import_cost')

	def run(self, edit, output):
		phantoms = [
			sublime.Phantom(self.get_region(x['line']), x['html'], sublime.LAYOUT_INLINE)
			for x in output
		]
		self.view.erase_phantoms('import_cost')
		self.phantom_set.update(phantoms)

	def get_region(self, line):
		a = self.view.text_point(line, 0)
		return sublime.Region(a - 1)


class ImportCostCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		ImportCostExec(self.view).start()

		
class EventEditor(sublime_plugin.EventListener):

	def on_modified(self, view):
		if view.file_name():
			file_extension = os.path.splitext(view.file_name())[1]
			if file_extension in FILE_EXTENSIONS:
				
				global NODE_OUTPUT_CACHE # remove phantom if line is being edited
				line = view.rowcol(view.sel()[0].begin())[0] + 1
				if line in [x['line'] for x in NODE_OUTPUT_CACHE]:
					NODE_OUTPUT_CACHE[:] = [x for x in NODE_OUTPUT_CACHE if x.get('line') != line]
					view.run_command('write_output', {'output': NODE_OUTPUT_CACHE})

				view.run_command('import_cost')

	def on_activated(self, view):
		view.run_command('import_cost')

	def on_deactivated(self, view):
		view.erase_phantoms('import_cost')
		NODE_SOCKET.terminate_process()

	def on_close(self, view):
		NODE_SOCKET.terminate_process()