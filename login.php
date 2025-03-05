<?php
$usuarios = [
    "root" => "root",
    "David" => "123"
];

$user = $_POST['usuario'] ?? '';
$pass = $_POST['password'] ?? '';

if (isset($usuarios[$user]) && $usuarios[$user] === $pass) {
    header("Location: bienvenido.php?usuario=$user");
    exit();
} else {
    echo "Usuario o contraseña incorrectos.";
}
?>
