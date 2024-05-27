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
  //Crea un objeto date para obtener la fecha actual
  date = new Date();
  year = date.getFullYear();
  month = date.getMonth() + 1;
  day = date.getDate();
  //El formato tiene que ser con dos digitos con un 0 a la izquierda
  //de ser nesesario
  if (month < 10) {
    month = "0" + month
  }
  if (day < 10) {
    day = "0" + day
  }
  //Se crea una string con la fecha en el formato que nesesita html
  formatedDate = year + "-" + month + "-" + day
  document.getElementById("inputFecha")
    .setAttribute("value", formatedDate);

}
console.log("jsLink")

function showDiv(id = "formulario") {
  //encontrar el div del formulario
  let div = document.getElementById(id)
  //Si esta escondido mostrarlo de lo contrario esconder
  if (div.style.display === "none") {
    div.style.display = "block";
    return
  }
  div.style.display = "none"
  return
}
//Esta funcion no se usa pero es para tener multiples botones que muestran y
//esconden tablas
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

//esta funcion no se usa
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

function busqueda(tableBodyId="myTBody") {
  console.log("busqueda")
  var input, a, filter, tbody;
  //busca el bloque de texto
  input = document.getElementById("buscador")
  //el texto del bloque es nuestro filtro
  filter = input.value.toLowerCase();
  //obtenemos el cuerpo de la tabla
  tbody = document.getElementById(tableBodyId)
  //tr es una lista de todos las filas
  tr = tbody.getElementsByTagName("tr")
  for (let i = 0; i < tr.length; i++) {
    //obtiene todas las columnas de la fila actual
    //console.log("row")
    td = tr[i].querySelectorAll(".toCheck")
    //console.log("td " + td.length)
    //console.log(td)
    for(let j = 0; j < td.length; j++) {
      console.log("col")
      texto = td[j].textContent.toLowerCase()
      //console.log(texto)
      if(texto.indexOf(filter) > -1) {
        tr[i].style.display = ""
        break;
      }else {
        tr[i].style.display = "none"
      }
    }
  }
}
//al tocar el boton radio todo se destickea todo lo demas
function todoCheck() {
  checkboxContainer = document.getElementById("checkbox_container")
  checkboxes = checkboxContainer.getElementsByTagName("input")
  for(let i = 0; i < checkboxes.length; i++) {
    checkboxes[i].checked = false
  }
}
//al tickear una opcion automaticamente el boton radio se 
//destickea
function sheetCheck() {
  todo_check = document.getElementById("todo_check")
  todo_check.checked = false
}
//al tickear tickear todo se tickean todas las opciones inferiores
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
//Para filtrar los modelos de equipo en base a los tipos de equipo seria nesesario
//tener los grupos ya filtrados. y guardados de alguna manera.
//podria tenerlos separados en selects invisibles.
//por cada tipo un select

//tipos para mostrar Mac
tipos_mac = {
  "Telefono": true
}
tipos_imei = {
  "Tablet": true,
  "celular": true
}
tipos_num_telefono = {
  "Celular": true,
  "Telefono": true
}
function mostrarSelectModelo() {
  console.log("mostrar")
  //obtener la id del tipo
  tipo = document.getElementById("nombre_tipo_equipo").value
  
  console.log("tipo")
  console.log(tipo)
  //get all divs with class x give class x to relevant divs
  div = document.getElementById("select_div")   
  selects = div.querySelectorAll(".select_modelo")
  //esconder todos los divs menos los relevantes
  for(let i = 0; i < selects.length; i++) {
    if(selects[i].id == tipo) {
      selects[i].style.display = ""
      console.log(selects[i])
    }else {
      selects[i].style.display = "none"

    }
  }

  //esconder mac
  tipo = document.getElementById("nombre_tipo_equipo").value
  mac_div = document.getElementById("Mac")
  if(tipos_mac[tipo]) {
    mac_div.style.display = "block"
  }else {
    mac_div.style.display = "none"
  }

  //esconder imei
  imei_div = document.getElementById("Imei")
  if(tipos_imei[tipo]) {
    imei_div.style.display = "block"
  }else {
    imei_div.style.display = "none"
  }
  //esconder numero de telefono
  num_telefono_div = document.getElementById("Telefono")
  if(tipos_num_telefono[tipo]) {
    num_telefono_div.style.display = "block"
  }else {
    num_telefono_div.style.display = "none"
  }


}

function mostrarTipo_equipo() {
  select = document.getElementById("marca_equipo")
  idMarca = select.value;
  console.log("mostarTipo_equipo" + idMarca)

  //Obten todos los divs de la clase select_modelo
  divs_select_para_marca = document.querySelectorAll('.select_modelo')
  //parece que el objeto retornado es un dicionario por lo que un 
  //for in no funciona pero las claves son numeros naturales + 0
  //console.log(divs_select_para_marca)
  //console.log(divs_select_para_marca[0])
  
  for(let i = 0; i < divs_select_para_marca.length; i++) {
    div = divs_select_para_marca[i]
    div.style.display = "none"
  }
  objective_div = document.getElementById(idMarca)
  objective_div.style.display = "block"

  boton = document.getElementById("enviar")
  boton.style.display = "block"
}
//Envia el tipo a 
function enviarTipo(valor) {
  console.log("test")
  console.log(valor)
  select = document.getElementById(valor)
  tipo_equipo_value = select.value
  console.log(select.value)
  output_tipo_equipo = document.getElementById('nombre_tipo_equipo')
  output_tipo_equipo.value = select.value

}
function abrir_cerrar_ojo(id_ojo, repetir) {
  ojo_contrasenna = document.getElementById(id_ojo)
  src = ojo_contrasenna.src
  //console.log("src")
  //console.log(src)
  //relative_tmp = location.href.split("/")
  //relative_path = relative_tmp[0] + "//" + relative_tmp[2]
  //console.log("absURL")
  //console.log(relative_path)
  //console.log(document.URL)
  //console.log(location.href)
  img_name = src.split("/")
  console.log("img_name")
  console.log(img_name)
  if(img_name[5] == "eye.png") {
    console.log("if")
    ojo_contrasenna.src = "../static/img/hidden.png"
    if(repetir) {
      input = document.getElementById('contrasenna_repetir').type = 'text'
    }else {
      input = document.getElementById('contrasenna').type = 'text'
    }
  }else {
    console.log("else")
    ojo_contrasenna.src = "../static/img/eye.png"
    if(repetir) {
      input = document.getElementById('contrasenna_repetir').type = 'password'
    }else {
      input = document.getElementById('contrasenna').type = 'password'
    }
  }



}