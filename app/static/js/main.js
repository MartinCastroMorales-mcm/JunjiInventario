/*const btnDelete= document.querySelectorAll('.btn-delete');
if(btnDelete) {
  const btnArray = Array.from(btnDelete);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if(!confirm('Are you sure you want to delete it?')){
        e.preventDefault();
      }
    });
  })
}
//Código para Datables
$(document).ready(function() { 
  $('#table').DataTable(); //Para inicializar datatables de la manera más simple
});
*/
function fechaPorDefecto() {
  date = new Date();
  year = date.getFullYear();
  month = date.getMonth() + 1;
  day = date.getDate();
  if (month < 10) {
    month = "0" + month
  }
  if (day < 10) {
    day = "0" + day
  }
  formatedDate = year + "-" + month + "-" + day
  document.getElementById("inputFecha")
    .setAttribute("value", formatedDate);

}
console.log("jsLink")

function showDiv(id = "formulario") {
  let div = document.getElementById(id)
  if (div.style.display === "none") {
    div.style.display = "block";
    return
  }
  div.style.display = "none"
  return
}
function showDivHideOthers(id = "formulario") {
  let divs = {
    "tabla-asignaciones": document.getElementById("tabla-asignaciones"),
    "tabla-devoluciones": document.getElementById("tabla-devoluciones"),
    "tabla-traslados": document.getElementById("tabla-traslados"),
    "tabla-incidencias": document.getElementById("tabla-incidencias")
  }
  for (const [key, value] of Object.entries(divs)) {
    if (key != id) {
      value.style.display = "none"
    } else {
      value.style.display = "block"
    }

  }
}

function openWindow(url) {
  window.open(url)
}

function sortTable(n) {
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById("myTableBody");
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 0; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (dir == "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
function busqueda() {
  var input, a, filter, tbody;
  input = document.getElementById("buscador")
  filter = input.value.toLowerCase();
  tbody = document.getElementById("myTBody")
  tr = tbody.getElementsByTagName("tr")
  for (let i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")
    textoClave = td[0].textContent.toLowerCase()
    textoNombre = td[1].textContent.toLowerCase()
    textoCodigo = td[2].textContent.toLowerCase()
    if (textoClave.indexOf(filter) > -1 
    || 
    textoNombre.indexOf(filter) > -1
    ||
    textoCodigo.indexOf(filter) > -1) {
      tr[i].style.display = ""
    } else {
      tr[i].style.display = "none"
    }
  }
}
function todoCheck() {
  checkboxContainer = document.getElementById("checkbox_container")
  checkboxes = checkboxContainer.getElementsByTagName("input")
  for(let i = 0; i < checkboxes.length; i++) {
    checkboxes[i].checked = false
  }
}
function sheetCheck() {
  todo_check = document.getElementById("todo_check")
  todo_check.checked = false
}
function check_all() {
  sheetCheck()
  console.log("checkall")
  checkboxContainer = document.getElementById("checkbox_container")
  checkboxes = checkboxContainer.getElementsByTagName("input")
  checkall_element = document.getElementById("checkall")
  for(let i = 0; i < checkboxes.length; i++) {
    checkboxes[i].checked = checkall.checked
  }
}