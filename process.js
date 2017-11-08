const { importCost, cleanup, JAVASCRIPT } = require('import-cost');

getStdin().then(function(data) {
  const { file_string: fileString, file_path: filePath } = JSON.parse(data);
  // const emitter = importCost(filePath, fileString, JAVASCRIPT);
  process.stdout.write(JSON.stringify(filePath));
}).catch(function(err) {
  process.stderr.write(err.message);
});

// (async () => {
//   try {

//     var data = await getStdin();
//     process.stdout.write(data);

//   } catch(error) {
//     process.stderr.write(err.message);
//   }

// })();

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

// observable