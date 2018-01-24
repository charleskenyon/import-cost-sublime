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

Rx.Observable.fromPromise(getStdin())
  .map(JSON.parse)
  .startWith(null)
  .pairwise()
  .filter(verifyImportChange)
  .pluck(1)
  .switchMap(mapImportCost)
  .do(_ => cleanup())
  .map(JSON.stringify)
  .subscribe(
    output => process.stdout.write(output),
    err => process.exit()
  );

function getStdin() {
  let chunk, data = '';
  return new Promise((resolve, reject) => {
    process.stdin.setEncoding('utf8');
    process.stdin.on('readable', () => {
      if ((chunk = process.stdin.read())) data += chunk;
    });
    process.stdin.on('end', () => {
      resolve(data);
    });
  });
}

function mapImportCost(data) {
  return Rx.Observable.fromEvent(
    importCost(data.file_name, data.file_string, JAVASCRIPT)
  , 'done');
}