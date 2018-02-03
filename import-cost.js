const _ = require('ramda');
const Rx = require('rxjs/Rx');
const Maybe = require('data.maybe');
const { importCost, cleanup, JAVASCRIPT } = require('import-cost');

const verifyImportChange = _.compose(
  _.not,
  _.apply(_.equals),
  _.map(
    _.compose(
      x => x.getOrElse(null),
      _.map(
        _.compose(
          _.filter(_.test(/\bimport\s|\brequire\(/)),
          _.addIndex(_.map)((v, i) => v + i),
          _.split('\n'),
          _.prop('file_string')
        )
      ),
      Maybe.fromNullable
    )
  )
);

Rx.Observable.fromEvent(process.stdin, 'readable', () => process.stdin.read())
  .map(v => v.toString('ascii'))
  .map(JSON.parse)
  .startWith(null)
  .pairwise()
  // .mergeMap(importChangeStream)
  .map(v => v + '\n')
  .subscribe(
    output => process.stdout.write(output),
    err => process.exit() // need error handling
  );

function importChangeStream(data) {
  return verifyImportChange(data) ? continueStream(data) : Rx.Observable.of('\n');
}

function continueStream(data) {
  return Rx.Observable.of(data)
    .pluck(1)
    .switchMap(importCostStream) // use switchMap
    .do(_ => cleanup())
    .map(JSON.stringify)
    .map(v => v + '\n')
}

function importCostStream(data) {
  return Rx.Observable.fromEvent(
    importCost(data['file_path'], data['file_string'], JAVASCRIPT)
      .on('error', err => {})
  , 'done');
}

// /Users/bmck/Library/Application Support/Sublime Text 3/Packages/import-cost-sublime