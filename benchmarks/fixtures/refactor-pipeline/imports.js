export function importFiles(files, importFile, done) {
  let index = 0;

  function next(error) {
    if (error) return done(error);
    if (index === files.length) return done();

    importFile(files[index++], (fileError) => {
      if (fileError) return retry(fileError, next);
      next();
    });
  }

  next();
}

function retry(error, next) {
  setTimeout(() => next(error), 10);
}
