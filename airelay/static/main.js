// custom javascript

(function() {
  console.log('Sanity Check!');
})();

// function handleClick(type) {
//   fetch('/tasks', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json'
//     },
//     body: JSON.stringify({ type: type }),
//   })
//   .then(response => response.json())
//   .then(data => {
//     getStatus(data.task_id)
//   })
// }

(function() {
  fetch('/api/v1/threads', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(res => {
    res.forEach((el) => {
      const newRow = document.getElementById('thread').insertRow(0);
      newRow.innerHTML = `
       <tr>
         <td>${el.thread_id}</td>
         <td>${el.name}</td>
         <td>${el.description}</td>
         <td>${el.timestamp}</td>
       </tr>`;
    })
  })
  .catch(err => console.log(err));

  fetch('/api/v1/roles', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(res => {
    console.log(res.msg)
    for (let k in res.msg) {
      console.log(k);
      console.log(res.msg[k]);

      const newRow = document.getElementById('roles').insertRow(0);
      newRow.innerHTML = `
       <tr>
         <td>${k}</td>
         <td><md-block>${res.msg[k].description}</md-block></td>
       </tr>`;
    }
  })
  .catch(err => console.log(err));

})();
