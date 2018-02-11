const _ = require('ramda');
const Maybe = require('data.maybe');

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

module.exports = verifyImportChange;