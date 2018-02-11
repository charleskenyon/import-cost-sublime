const Rx = require('rxjs/Rx');
const { importCost, cleanup, JAVASCRIPT } = require('import-cost');
const verifyImportChange = require('./verify-import-change');
const formatPayload = require('./format-payload');

Rx.Observable.fromEvent(process.stdin, 'readable', () => process.stdin.read())
	.map(v => v.toString('ascii'))
	.map(JSON.parse)
	.startWith(null)
	.pairwise()
	.mergeMap(importChangeStream)
	.subscribe(
		output => process.stdout.write(output),
		err => process.exit()
	);

function importChangeStream(data) {
	return verifyImportChange(data) ? continueStream(data) : Rx.Observable.of('\n');
}

function continueStream(data) {
	return Rx.Observable.of(data)
		.pluck(1)
		.switchMap(importCostStream)
		.do(_ => cleanup())
		.map(formatPayload) // memoize
		.map(JSON.stringify)
		.map(v => v + '\n')
}

function importCostStream(data) {
	return Rx.Observable.fromEvent(
		importCost(data['file_path'], data['file_string'], JAVASCRIPT)
			.on('error', err => {})
	, 'done');
}