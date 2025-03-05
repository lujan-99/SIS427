document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const usuario = document.getElementById('usuario').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');

    // Datos de usuario válidos
    const usuariosValidos = {
        "root": "root",
        "David": "123"
    };

    // Validación de usuario y contraseña
    if (usuariosValidos[usuario] === password) {
        alert("Bienvenido, " + usuario);
        // Aquí rediriges a la página principal si lo deseas
        // window.location.href = "bienvenido.html";
    } else {
        errorMessage.textContent = "Usuario o contraseña incorrectos.";
    }
});
