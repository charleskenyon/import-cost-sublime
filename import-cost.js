const _ = require('ramda');
const Rx = require('rxjs/Rx');
Rx.Node = require('rx-node');
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

const importCostStream = (data) => {
  return Rx.Observable.fromEvent(
    importCost(data['file_path'], data['file_string'], JAVASCRIPT)
  , 'done');
}

Rx.Node.fromReadableStream(process.stdin, 'data')
  .map(JSON.parse)
  .startWith(null)
  .pairwise()
  // .filter(verifyImportChange)
  // .pluck(1)
  // .switchMap(importCostStream)
  // .do(_ => cleanup())
  .map(JSON.stringify)
  .subscribe(
    output => process.stdout.write(output),
    err => process.exit()
  );

  // /Users/bmck/Library/Application Support/Sublime Text 3/Packages/import-cost-sublime

  // process.stdin.resume();