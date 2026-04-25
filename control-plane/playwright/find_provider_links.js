const https = require('https');

https.get('https://akash.network/docs/', (res) => {
  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });
  res.on('end', () => {
    const matches = [...new Set(Array.from(data.matchAll(/\/docs\/[^"' )]+/g)).map((m) => m[0]))]
      .filter((x) => /provider/i.test(x));
    console.log(matches.join('\n'));
  });
}).on('error', (err) => {
  console.error(err);
  process.exit(1);
});
