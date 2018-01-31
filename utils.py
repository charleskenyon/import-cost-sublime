import os
import platform
import subprocess

IS_MACOS = platform.system() == 'Darwin'
IS_WINDOWS = platform.system() == 'Windows'

def node_bridge(data, bin, args=[]):
	env = None
	startupinfo = None
	if IS_MACOS:
			env = os.environ.copy()
			env['PATH'] += os.path.expanduser('~/n/bin')
			env['PATH'] += ':/usr/local/bin'
			if IS_WINDOWS:
					startupinfo = subprocess.STARTUPINFO()
					startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			try:
					p = subprocess.Popen(['node', bin] + args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, env=env, startupinfo=startupinfo)
			except OSError:
					raise Exception('Couldn\'t find Node.js. Make sure it\'s in your $PATH by running `node -v` in your command-line.')
			stdout, stderr = p.communicate(input=data.encode('utf-8'))
			stdout = stdout.decode('utf-8')
			stderr = stderr.decode('utf-8')
			if stderr:
					raise Exception('Error: %s' % stderr)
			else:
					return stdout

			# return p rather than output - try and open socket once and stream data
			# python ValueError: Cannot send input after starting communication

def npm_install(view, path):
	if not 'node_modules' in [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]:
		try:
			command = ["npm", "install"]
			process = subprocess.Popen(command, stdout=subprocess.PIPE)
			out, err = process.communicate()
		except OSError:
			raise Exception('Couldn\'t find npm. Make sure it\'s in your $PATH by running `npm -v` in your command-line.')