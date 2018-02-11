import os, platform, subprocess

IS_MACOS = platform.system() == 'Darwin'
IS_WINDOWS = platform.system() == 'Windows'

def node_socket(bin, args=[]):
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
			p = subprocess.Popen(['node', bin] + args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, env=env, startupinfo=startupinfo, universal_newlines=True)
	except OSError:
			raise Exception('Couldn\'t find Node.js. Make sure it\'s in your $PATH by running `node -v` in your command-line.')
	return p